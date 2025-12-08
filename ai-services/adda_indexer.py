"""
Adda Indexer v2 - Taxonomy-Aware Indexing
Reads from data_pipeline/output/ and indexes into ChromaDB + Kuzu.

Usage:
    python adda_indexer.py

This script should be run after data_pipeline has processed documents.
It reads Smart Blocks with taxonomy metadata and creates:
1. ChromaDB vectors with taxonomy filters (taxonomy_root, taxonomy_branch, scope_context)
2. Kuzu graph with Block, Topic, Entity, Branch, Scope, Step nodes and relations
"""
import os
import yaml
import json
import shutil
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

# Third party
import chromadb
from chromadb.utils import embedding_functions
import kuzu

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.resolve()

# Source: data_pipeline output (not storage/lake)
SOURCE_DIR = BASE_DIR / "data_pipeline" / "output"

# Destinations
INDEX_DIR = BASE_DIR / "storage" / "index"
CHROMA_PATH = INDEX_DIR / "chroma"
KUZU_PATH = INDEX_DIR / "kuzu"
LOG_PATH = BASE_DIR / "logs" / "indexer.log"
CONFIG_DIR = BASE_DIR / "config"

INDEX_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - INDEXER - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
log = logging.getLogger("INDEXER")


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_chromadb() -> chromadb.Collection:
    """Initialize ChromaDB with embedding function."""
    log.info("Initializing ChromaDB...")
    
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Delete existing collection to reindex fresh
    try:
        chroma_client.delete_collection(name="adda_knowledge")
        log.info("Deleted existing collection for fresh reindex")
    except:
        pass
    
    collection = chroma_client.create_collection(
        name="adda_knowledge",
        embedding_function=embed_fn
    )
    
    return collection


def init_kuzu() -> kuzu.Connection:
    """Initialize Kuzu graph database with new schema."""
    log.info("Initializing Kuzu...")
    
    # Remove existing database for fresh reindex
    if KUZU_PATH.exists():
        shutil.rmtree(KUZU_PATH)
        log.info("Removed existing Kuzu database for fresh reindex")
    
    db = kuzu.Database(str(KUZU_PATH))
    conn = kuzu.Connection(db)
    
    return conn


def setup_kuzu_schema(conn: kuzu.Connection):
    """
    Create Kuzu graph schema with taxonomy-aware nodes and relations.
    
    Nodes:
    - Block: Smart Block (uuid, type, authority)
    - Topic: A topic/concept (name)
    - Entity: A named entity (name)
    - Branch: Taxonomy branch (name, root)
    - Scope: Scope context (name)
    - Step: Process step (name)
    
    Relations:
    - MENTIONS_TOPIC: Block -> Topic
    - MENTIONS_ENTITY: Block -> Entity
    - BELONGS_TO_BRANCH: Block -> Branch
    - APPLIES_IN_SCOPE: Block -> Scope
    - IN_STEP: Block -> Step
    """
    log.info("Creating Kuzu schema...")
    
    # NODE TABLES
    conn.execute("""
        CREATE NODE TABLE Block(
            uuid STRING, 
            type STRING, 
            authority STRING,
            filename STRING,
            PRIMARY KEY (uuid)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Topic(
            name STRING, 
            PRIMARY KEY (name)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Entity(
            name STRING, 
            PRIMARY KEY (name)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Branch(
            name STRING, 
            root STRING, 
            PRIMARY KEY (name)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Scope(
            name STRING, 
            PRIMARY KEY (name)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Step(
            name STRING, 
            PRIMARY KEY (name)
        )
    """)
    
    # RELATION TABLES
    conn.execute("CREATE REL TABLE MENTIONS_TOPIC(FROM Block TO Topic)")
    conn.execute("CREATE REL TABLE MENTIONS_ENTITY(FROM Block TO Entity)")
    conn.execute("CREATE REL TABLE BELONGS_TO_BRANCH(FROM Block TO Branch)")
    conn.execute("CREATE REL TABLE APPLIES_IN_SCOPE(FROM Block TO Scope)")
    conn.execute("CREATE REL TABLE IN_STEP(FROM Block TO Step)")
    
    log.info("Kuzu schema created successfully")


# =============================================================================
# PARSING
# =============================================================================

def parse_frontmatter(content: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Parse YAML frontmatter from Markdown content."""
    try:
        if "---" not in content:
            return None, None
        
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, None
        
        yaml_content = parts[1]
        text = parts[2].strip()
        
        meta = yaml.safe_load(yaml_content)
        return meta, text
        
    except Exception as e:
        log.debug(f"YAML parse error: {e}")
        return None, None


# =============================================================================
# INDEXING
# =============================================================================

class IndexerState:
    """Track created nodes to avoid PRIMARY KEY violations in Kuzu."""
    
    def __init__(self):
        self.created_topics: Set[str] = set()
        self.created_entities: Set[str] = set()
        self.created_branches: Set[str] = set()
        self.created_scopes: Set[str] = set()
        self.created_steps: Set[str] = set()
        
        # Vocabulary aggregation
        self.all_topics: Set[str] = set()
        self.all_entities: Set[str] = set()
        self.taxonomy: Dict[str, Dict[str, List[str]]] = {}


def safe_create_topic(conn: kuzu.Connection, name: str, state: IndexerState):
    """Create Topic node if not already created."""
    if not name or name in state.created_topics:
        return
    
    try:
        # Escape single quotes in name
        safe_name = name.replace("'", "''")
        conn.execute(f"CREATE (:Topic {{name: '{safe_name}'}})")
        state.created_topics.add(name)
    except Exception as e:
        if "PRIMARY KEY" not in str(e):
            log.debug(f"Topic creation error: {e}")
        state.created_topics.add(name)


def safe_create_entity(conn: kuzu.Connection, name: str, state: IndexerState):
    """Create Entity node if not already created."""
    if not name or name in state.created_entities:
        return
    
    try:
        safe_name = name.replace("'", "''")
        conn.execute(f"CREATE (:Entity {{name: '{safe_name}'}})")
        state.created_entities.add(name)
    except Exception as e:
        if "PRIMARY KEY" not in str(e):
            log.debug(f"Entity creation error: {e}")
        state.created_entities.add(name)


def safe_create_branch(conn: kuzu.Connection, name: str, root: str, state: IndexerState):
    """Create Branch node if not already created."""
    if not name or name in state.created_branches:
        return
    
    try:
        safe_name = name.replace("'", "''")
        safe_root = root.replace("'", "''")
        conn.execute(f"CREATE (:Branch {{name: '{safe_name}', root: '{safe_root}'}})")
        state.created_branches.add(name)
    except Exception as e:
        if "PRIMARY KEY" not in str(e):
            log.debug(f"Branch creation error: {e}")
        state.created_branches.add(name)


def safe_create_scope(conn: kuzu.Connection, name: str, state: IndexerState):
    """Create Scope node if not already created."""
    if not name or name in state.created_scopes:
        return
    
    try:
        safe_name = name.replace("'", "''")
        conn.execute(f"CREATE (:Scope {{name: '{safe_name}'}})")
        state.created_scopes.add(name)
    except Exception as e:
        if "PRIMARY KEY" not in str(e):
            log.debug(f"Scope creation error: {e}")
        state.created_scopes.add(name)


def safe_create_step(conn: kuzu.Connection, name: str, state: IndexerState):
    """Create Step node if not already created."""
    if not name or name in state.created_steps:
        return
    
    try:
        safe_name = name.replace("'", "''")
        conn.execute(f"CREATE (:Step {{name: '{safe_name}'}})")
        state.created_steps.add(name)
    except Exception as e:
        if "PRIMARY KEY" not in str(e):
            log.debug(f"Step creation error: {e}")
        state.created_steps.add(name)


def index_block(
    file_path: Path,
    collection: chromadb.Collection,
    conn: kuzu.Connection,
    state: IndexerState
) -> bool:
    """
    Index a single Smart Block file.
    Returns True if successful, False otherwise.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()
    
    meta, text = parse_frontmatter(raw_content)
    
    if not meta or not text:
        return False
    
    # Extract metadata
    uid = meta.get('uuid', str(uuid.uuid4()))
    block_type = meta.get('block_type', 'DEFINITION')
    authority = meta.get('authority_level', 'PRIMARY')
    
    # NEW: Taxonomy fields
    taxonomy_root = meta.get('taxonomy_root', 'DOMAIN_OBJECTS')
    taxonomy_branch = meta.get('taxonomy_branch', 'ROLES')
    scope_context = meta.get('scope_context', 'FRAMEWORK_SPECIFIC')
    
    # Topics and Entities
    topic_tags = meta.get('topic_tags', [])
    entities = meta.get('entities', [])
    
    # Process step
    suggested_phase = meta.get('suggested_phase', ['general'])
    step = suggested_phase[0] if suggested_phase else 'general'
    
    # Legacy tags
    tags = meta.get('tags', [])
    
    # =========================================================================
    # 1. CHROMADB: Vector Index with Taxonomy Metadata
    # =========================================================================
    
    # Build searchable text with taxonomy context
    searchable_text = f"""
TYPE: {block_type}
ROOT: {taxonomy_root}
BRANCH: {taxonomy_branch}
SCOPE: {scope_context}
STEP: {step}
TOPICS: {', '.join(topic_tags)}
ENTITIES: {', '.join(entities)}
TAGS: {', '.join(tags)}

{text}
"""
    
    collection.add(
        ids=[uid],
        documents=[searchable_text],
        metadatas=[{
            "uuid": uid,
            "type": block_type,
            "taxonomy_root": taxonomy_root,
            "taxonomy_branch": taxonomy_branch,
            "scope_context": scope_context,
            "step": step,
            "authority": authority,
            "filename": file_path.name
        }]
    )
    
    # =========================================================================
    # 2. KUZU: Graph Index with Relations
    # =========================================================================
    
    # Create Block node
    safe_filename = file_path.name.replace("'", "''")
    safe_type = block_type.replace("'", "''")
    safe_auth = authority.replace("'", "''")
    
    try:
        conn.execute(f"""
            CREATE (:Block {{
                uuid: '{uid}', 
                type: '{safe_type}', 
                authority: '{safe_auth}',
                filename: '{safe_filename}'
            }})
        """)
    except Exception as e:
        log.debug(f"Block creation error: {e}")
        return False
    
    # Create shared nodes (Branch, Scope, Step)
    safe_create_branch(conn, taxonomy_branch, taxonomy_root, state)
    safe_create_scope(conn, scope_context, state)
    safe_create_step(conn, step, state)
    
    # Create Topic and Entity nodes
    for topic in topic_tags:
        safe_create_topic(conn, topic, state)
        state.all_topics.add(topic)
        
        # Track taxonomy hierarchy
        if taxonomy_root not in state.taxonomy:
            state.taxonomy[taxonomy_root] = {}
        if taxonomy_branch not in state.taxonomy[taxonomy_root]:
            state.taxonomy[taxonomy_root][taxonomy_branch] = []
        if topic not in state.taxonomy[taxonomy_root][taxonomy_branch]:
            state.taxonomy[taxonomy_root][taxonomy_branch].append(topic)
    
    for entity in entities:
        safe_create_entity(conn, entity, state)
        state.all_entities.add(entity)
    
    # Create relations
    try:
        # Block -> Branch
        safe_branch = taxonomy_branch.replace("'", "''")
        conn.execute(f"""
            MATCH (b:Block {{uuid: '{uid}'}}), (br:Branch {{name: '{safe_branch}'}})
            CREATE (b)-[:BELONGS_TO_BRANCH]->(br)
        """)
        
        # Block -> Scope
        safe_scope = scope_context.replace("'", "''")
        conn.execute(f"""
            MATCH (b:Block {{uuid: '{uid}'}}), (s:Scope {{name: '{safe_scope}'}})
            CREATE (b)-[:APPLIES_IN_SCOPE]->(s)
        """)
        
        # Block -> Step
        safe_step = step.replace("'", "''")
        conn.execute(f"""
            MATCH (b:Block {{uuid: '{uid}'}}), (st:Step {{name: '{safe_step}'}})
            CREATE (b)-[:IN_STEP]->(st)
        """)
        
        # Block -> Topics
        for topic in topic_tags:
            safe_topic = topic.replace("'", "''")
            conn.execute(f"""
                MATCH (b:Block {{uuid: '{uid}'}}), (t:Topic {{name: '{safe_topic}'}})
                CREATE (b)-[:MENTIONS_TOPIC]->(t)
            """)
        
        # Block -> Entities
        for entity in entities:
            safe_entity = entity.replace("'", "''")
            conn.execute(f"""
                MATCH (b:Block {{uuid: '{uid}'}}), (e:Entity {{name: '{safe_entity}'}})
                CREATE (b)-[:MENTIONS_ENTITY]->(e)
            """)
            
    except Exception as e:
        log.debug(f"Relation creation error: {e}")
    
    return True


def save_vocabulary(state: IndexerState):
    """Save aggregated vocabulary to config/vocabulary.json."""
    vocabulary = {
        "taxonomy": state.taxonomy,
        "topics": sorted(list(state.all_topics)),
        "entities": sorted(list(state.all_entities)),
        "block_types": ["RULE", "DEFINITION", "INSTRUCTION", "DATA_POINTER", "EXAMPLE"]
    }
    
    vocab_path = CONFIG_DIR / "vocabulary.json"
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(vocabulary, f, ensure_ascii=False, indent=2)
    
    log.info(f"Saved vocabulary to {vocab_path}")
    log.info(f"  - Topics: {len(state.all_topics)}")
    log.info(f"  - Entities: {len(state.all_entities)}")
    log.info(f"  - Taxonomy roots: {len(state.taxonomy)}")


# =============================================================================
# MAIN
# =============================================================================

def run_indexer():
    """Main indexer entry point."""
    log.info("=" * 60)
    log.info("ADDA INDEXER v2 - Taxonomy-Aware Indexing")
    log.info("=" * 60)
    
    # Check source directory
    if not SOURCE_DIR.exists():
        log.error(f"Source directory not found: {SOURCE_DIR}")
        log.error("Run data_pipeline first to generate Smart Blocks.")
        return
    
    files = list(SOURCE_DIR.glob("*.md"))
    if not files:
        log.warning(f"No Markdown files found in {SOURCE_DIR}")
        return
    
    log.info(f"Found {len(files)} files to index")
    
    # Initialize databases
    collection = init_chromadb()
    conn = init_kuzu()
    setup_kuzu_schema(conn)
    
    # Index files
    state = IndexerState()
    count = 0
    skipped = 0
    
    for file_path in files:
        success = index_block(file_path, collection, conn, state)
        if success:
            count += 1
            if count % 50 == 0:
                log.info(f"Indexed {count} files...")
        else:
            skipped += 1
    
    # Save vocabulary
    save_vocabulary(state)
    
    # Summary
    log.info("=" * 60)
    log.info(f"INDEXING COMPLETE")
    log.info(f"  - Blocks indexed: {count}")
    log.info(f"  - Blocks skipped: {skipped}")
    log.info(f"  - Topics created: {len(state.created_topics)}")
    log.info(f"  - Entities created: {len(state.created_entities)}")
    log.info(f"  - Branches created: {len(state.created_branches)}")
    log.info(f"  - Scopes created: {len(state.created_scopes)}")
    log.info(f"  - Steps created: {len(state.created_steps)}")
    log.info("=" * 60)


if __name__ == "__main__":
    run_indexer()

