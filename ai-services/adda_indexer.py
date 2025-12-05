"""
Adda Indexer v3 - Taxonomy-Aware Indexing with Learning Support
Reads from data_pipeline/output/ and indexes into ChromaDB + Kuzu.

Usage:
    python adda_indexer.py                              # Basic indexing
    python adda_indexer.py --learnings learnings.json   # With learned relations

This script should be run after data_pipeline has processed documents.
It reads Smart Blocks with taxonomy metadata and creates:
1. ChromaDB vectors with taxonomy filters (taxonomy_root, taxonomy_branch, scope_context)
2. Kuzu graph with:
   - TAXONOMY NODES (from adda_taxonomy.json): Area, County, Level, Kompetensomrade, Avropsform
   - BLOCK NODES: Block, Topic, Entity, Branch, Scope, Step
   - LEARNED NODES (from learnings.json): City, Exempelroll, LearnedRelation, Alias
"""
import os
import yaml
import json
import shutil
import logging
import uuid
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

# Third party
import chromadb
from chromadb.utils import embedding_functions
import kuzu

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.resolve()

# Load config to get lake/index paths
def _load_config():
    config_path = BASE_DIR / "config" / "adda_config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return None

_config = _load_config()
if _config:
    # Use paths from config (supports lake_v2/index_v2)
    SOURCE_DIR = BASE_DIR / _config['paths']['lake']
    INDEX_DIR = BASE_DIR / _config['paths']['index_root']
else:
    # Fallback to defaults
    SOURCE_DIR = BASE_DIR / "storage" / "lake"
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
    
    TAXONOMY NODES (MASTER - from adda_taxonomy.json):
    - Area: Anbudsområde A-G (code, name)
    - County: Län (name)
    - Level: Kompetensnivå 1-5 (code, name, dr_allowed)
    - Kompetensomrade: Kompetensområde (name)
    - Avropsform: DR/FKU (code, name)
    
    BLOCK NODES (from Smart Blocks):
    - Block: Smart Block (uuid, type, authority)
    - Topic: A topic/concept (name)
    - Entity: A named entity (name)
    - Branch: Taxonomy branch (name, root)
    - Scope: Scope context (name)
    - Step: Process step (name)
    
    LEARNED NODES (from learnings.json):
    - City: Stad/kommun (name)
    - Exempelroll: Roll från Bilaga A (name)
    - LearnedRelation: Lärd relation (id, subject, predicate, object, confidence)
    - Alias: Synonymer/felstavningar (alias, canonical, entity_type)
    
    Relations:
    - MENTIONS_TOPIC: Block -> Topic
    - MENTIONS_ENTITY: Block -> Entity
    - BELONGS_TO_BRANCH: Block -> Branch
    - APPLIES_IN_SCOPE: Block -> Scope
    - IN_STEP: Block -> Step
    - LOCATED_IN: City -> County
    - BELONGS_TO_AREA: County -> Area
    - BELONGS_TO_OMRADE: Exempelroll -> Kompetensomrade
    - TRIGGERS: Level -> Avropsform
    - LEARNED_FROM: LearnedRelation -> Block
    """
    log.info("Creating Kuzu schema...")
    
    # =========================================================================
    # TAXONOMY NODES (MASTER - populated from adda_taxonomy.json)
    # =========================================================================
    
    conn.execute("""
        CREATE NODE TABLE Area(
            code STRING,
            name STRING,
            PRIMARY KEY (code)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE County(
            name STRING,
            PRIMARY KEY (name)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Level(
            code STRING,
            name STRING,
            dr_allowed BOOL,
            PRIMARY KEY (code)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Kompetensomrade(
            name STRING,
            PRIMARY KEY (name)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Avropsform(
            code STRING,
            name STRING,
            PRIMARY KEY (code)
        )
    """)
    
    # =========================================================================
    # BLOCK NODES (from Smart Blocks)
    # =========================================================================
    
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
    
    # =========================================================================
    # LEARNED NODES (populated from learnings.json)
    # =========================================================================
    
    conn.execute("""
        CREATE NODE TABLE City(
            name STRING,
            PRIMARY KEY (name)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Exempelroll(
            name STRING,
            PRIMARY KEY (name)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE LearnedRelation(
            id STRING,
            subject STRING,
            predicate STRING,
            object STRING,
            confidence DOUBLE,
            PRIMARY KEY (id)
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE Alias(
            alias STRING,
            canonical STRING,
            entity_type STRING,
            PRIMARY KEY (alias)
        )
    """)
    
    # =========================================================================
    # RELATION TABLES
    # =========================================================================
    
    # Block relations
    conn.execute("CREATE REL TABLE MENTIONS_TOPIC(FROM Block TO Topic)")
    conn.execute("CREATE REL TABLE MENTIONS_ENTITY(FROM Block TO Entity)")
    conn.execute("CREATE REL TABLE BELONGS_TO_BRANCH(FROM Block TO Branch)")
    conn.execute("CREATE REL TABLE APPLIES_IN_SCOPE(FROM Block TO Scope)")
    conn.execute("CREATE REL TABLE IN_STEP(FROM Block TO Step)")
    
    # Taxonomy relations
    conn.execute("CREATE REL TABLE BELONGS_TO_AREA(FROM County TO Area)")
    conn.execute("CREATE REL TABLE LOCATED_IN(FROM City TO County)")
    conn.execute("CREATE REL TABLE BELONGS_TO_OMRADE(FROM Exempelroll TO Kompetensomrade)")
    conn.execute("CREATE REL TABLE TRIGGERS(FROM Level TO Avropsform)")
    
    # Learning relations
    conn.execute("CREATE REL TABLE LEARNED_FROM(FROM LearnedRelation TO Block)")
    
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
# TAXONOMY INITIALIZATION (MASTER NODES)
# =============================================================================

def init_taxonomy_nodes(conn: kuzu.Connection):
    """
    Initialize MASTER nodes from adda_taxonomy.json.
    These are the fixed reference nodes that learnings connect to.
    """
    taxonomy_path = CONFIG_DIR / "adda_taxonomy.json"
    
    if not taxonomy_path.exists():
        log.warning(f"Taxonomy file not found: {taxonomy_path}")
        return
    
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)
    
    log.info("Initializing taxonomy MASTER nodes...")
    
    # =========================================================================
    # 1. ANBUDSOMRÅDEN (Area + County + relations)
    # =========================================================================
    areas_data = taxonomy.get("anbudsomraden", {}).get("areas", {})
    area_count = 0
    county_count = 0
    
    for code, area_info in areas_data.items():
        area_name = area_info.get("name", "")
        counties = area_info.get("counties", [])
        
        # Create Area node
        safe_name = area_name.replace("'", "''")
        try:
            conn.execute(f"CREATE (:Area {{code: '{code}', name: '{safe_name}'}})")
            area_count += 1
        except Exception as e:
            log.debug(f"Area creation error for {code}: {e}")
        
        # Create County nodes and relations
        for county in counties:
            safe_county = county.replace("'", "''")
            try:
                conn.execute(f"MERGE (:County {{name: '{safe_county}'}})")
                county_count += 1
            except Exception as e:
                log.debug(f"County creation error for {county}: {e}")
            
            # Create relation County -> Area
            try:
                conn.execute(f"""
                    MATCH (c:County {{name: '{safe_county}'}}), (a:Area {{code: '{code}'}})
                    CREATE (c)-[:BELONGS_TO_AREA]->(a)
                """)
            except Exception as e:
                log.debug(f"County-Area relation error: {e}")
    
    log.info(f"  Created {area_count} Area nodes, {county_count} County nodes")
    
    # =========================================================================
    # 2. KOMPETENSNIVÅER (Level + relation to Avropsform)
    # =========================================================================
    levels_data = taxonomy.get("kompetensnivaer", {}).get("levels", {})
    level_count = 0
    
    for code, level_info in levels_data.items():
        level_name = level_info.get("name", "")
        dr_allowed = level_info.get("dr_allowed", True)
        
        safe_name = level_name.replace("'", "''")
        try:
            conn.execute(f"""
                CREATE (:Level {{
                    code: '{code}', 
                    name: '{safe_name}', 
                    dr_allowed: {str(dr_allowed).lower()}
                }})
            """)
            level_count += 1
        except Exception as e:
            log.debug(f"Level creation error for {code}: {e}")
    
    log.info(f"  Created {level_count} Level nodes")
    
    # =========================================================================
    # 3. KOMPETENSOMRÅDEN
    # =========================================================================
    omraden = taxonomy.get("kompetensomraden", {}).get("areas", [])
    omrade_count = 0
    
    for omrade in omraden:
        safe_omrade = omrade.replace("'", "''")
        try:
            conn.execute(f"CREATE (:Kompetensomrade {{name: '{safe_omrade}'}})")
            omrade_count += 1
        except Exception as e:
            log.debug(f"Kompetensomrade creation error for {omrade}: {e}")
    
    log.info(f"  Created {omrade_count} Kompetensomrade nodes")
    
    # =========================================================================
    # 4. AVROPSFORMER
    # =========================================================================
    forms_data = taxonomy.get("avropsformer", {}).get("forms", {})
    form_count = 0
    
    for code, form_info in forms_data.items():
        form_name = form_info.get("name", "")
        
        safe_name = form_name.replace("'", "''")
        try:
            conn.execute(f"CREATE (:Avropsform {{code: '{code}', name: '{safe_name}'}})")
            form_count += 1
        except Exception as e:
            log.debug(f"Avropsform creation error for {code}: {e}")
    
    log.info(f"  Created {form_count} Avropsform nodes")
    
    # =========================================================================
    # 5. LEVEL -> AVROPSFORM TRIGGERS
    # =========================================================================
    # Level 5 requires FKU
    try:
        conn.execute("""
            MATCH (l:Level {code: '5'}), (a:Avropsform {code: 'FKU'})
            CREATE (l)-[:TRIGGERS]->(a)
        """)
        log.info("  Created Level 5 -> FKU trigger relation")
    except Exception as e:
        log.debug(f"Trigger relation error: {e}")


# =============================================================================
# LEARNINGS APPLICATION
# =============================================================================

def apply_learnings(conn: kuzu.Connection, learnings_path: Path):
    """
    Apply learned relations from learnings.json to the graph.
    
    Learnings types:
    - geo: City -> County (LOCATED_IN)
    - roles: Exempelroll -> Kompetensomrade (BELONGS_TO_OMRADE)
    - rules: LearnedRelation nodes
    - aliases: Alias nodes
    """
    if not learnings_path.exists():
        log.warning(f"Learnings file not found: {learnings_path}")
        return
    
    with open(learnings_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    learnings = data.get("learnings", [])
    log.info(f"Applying {len(learnings)} learnings to graph...")
    
    geo_count = 0
    role_count = 0
    rule_count = 0
    alias_count = 0
    
    for learning in learnings:
        ltype = learning.get("type", "")
        confidence = learning.get("confidence", 0.5)
        
        # Skip low-confidence learnings
        if confidence < 0.7:
            continue
        
        if ltype == "geo":
            # City -> County relation
            city = learning.get("subject", "")
            county = learning.get("object", "")
            
            if city and county:
                safe_city = city.replace("'", "''")
                safe_county = county.replace("'", "''")
                
                try:
                    # Create City node
                    conn.execute(f"MERGE (:City {{name: '{safe_city}'}})")
                    
                    # Create relation to County (County already exists from taxonomy)
                    conn.execute(f"""
                        MATCH (c:City {{name: '{safe_city}'}}), (co:County {{name: '{safe_county}'}})
                        MERGE (c)-[:LOCATED_IN]->(co)
                    """)
                    geo_count += 1
                except Exception as e:
                    log.debug(f"Geo learning error for {city}: {e}")
        
        elif ltype == "roles":
            # Exempelroll -> Kompetensomrade relation
            role = learning.get("subject", "")
            omrade = learning.get("object", "")
            
            if role and omrade:
                safe_role = role.replace("'", "''")
                safe_omrade = omrade.replace("'", "''")
                
                try:
                    # Create Exempelroll node
                    conn.execute(f"MERGE (:Exempelroll {{name: '{safe_role}'}})")
                    
                    # Create relation to Kompetensomrade
                    conn.execute(f"""
                        MATCH (r:Exempelroll {{name: '{safe_role}'}}), (k:Kompetensomrade {{name: '{safe_omrade}'}})
                        MERGE (r)-[:BELONGS_TO_OMRADE]->(k)
                    """)
                    role_count += 1
                except Exception as e:
                    log.debug(f"Role learning error for {role}: {e}")
        
        elif ltype == "rules":
            # LearnedRelation node
            subject = learning.get("subject", "")
            predicate = learning.get("predicate", "")
            obj = learning.get("object", "")
            
            if subject and predicate and obj:
                rel_id = str(uuid.uuid4())[:8]
                safe_subject = subject.replace("'", "''")
                safe_predicate = predicate.replace("'", "''")
                safe_obj = obj.replace("'", "''")
                
                try:
                    conn.execute(f"""
                        CREATE (:LearnedRelation {{
                            id: '{rel_id}',
                            subject: '{safe_subject}',
                            predicate: '{safe_predicate}',
                            object: '{safe_obj}',
                            confidence: {confidence}
                        }})
                    """)
                    rule_count += 1
                except Exception as e:
                    log.debug(f"Rule learning error: {e}")
        
        elif ltype == "aliases":
            # Alias node
            alias = learning.get("alias", "")
            canonical = learning.get("canonical", "")
            entity_type = learning.get("entity_type", "unknown")
            
            if alias and canonical:
                safe_alias = alias.replace("'", "''")
                safe_canonical = canonical.replace("'", "''")
                safe_type = entity_type.replace("'", "''")
                
                try:
                    conn.execute(f"""
                        MERGE (:Alias {{
                            alias: '{safe_alias}',
                            canonical: '{safe_canonical}',
                            entity_type: '{safe_type}'
                        }})
                    """)
                    alias_count += 1
                except Exception as e:
                    log.debug(f"Alias learning error for {alias}: {e}")
    
    log.info(f"  Applied learnings:")
    log.info(f"    - Geo (City->County): {geo_count}")
    log.info(f"    - Roles (Exempelroll->Omrade): {role_count}")
    log.info(f"    - Rules (LearnedRelation): {rule_count}")
    log.info(f"    - Aliases: {alias_count}")


# =============================================================================
# MAIN
# =============================================================================

def run_indexer(learnings_path: Optional[Path] = None):
    """
    Main indexer entry point.
    
    Args:
        learnings_path: Optional path to learnings.json for graph enrichment
    """
    log.info("=" * 60)
    log.info("ADDA INDEXER v3 - Taxonomy-Aware Indexing with Learning Support")
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
    
    # Initialize MASTER nodes from taxonomy
    init_taxonomy_nodes(conn)
    
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
    
    # Apply learnings if provided
    if learnings_path:
        apply_learnings(conn, learnings_path)
    
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
    if learnings_path:
        log.info(f"  - Learnings applied from: {learnings_path}")
    log.info("=" * 60)


def main():
    """Command-line entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Adda Indexer v3 - Taxonomy-Aware Indexing with Learning Support"
    )
    parser.add_argument(
        "--learnings",
        type=str,
        help="Path to learnings.json file for graph enrichment"
    )
    
    args = parser.parse_args()
    
    learnings_path = None
    if args.learnings:
        learnings_path = Path(args.learnings)
        if not learnings_path.is_absolute():
            learnings_path = BASE_DIR / args.learnings
    
    run_indexer(learnings_path)


if __name__ == "__main__":
    main()

