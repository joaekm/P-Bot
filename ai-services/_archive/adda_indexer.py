import os
import yaml
import glob
import shutil
import logging
import uuid
import re
from pathlib import Path

# Third party
import chromadb
from chromadb.utils import embedding_functions
import kuzu
from sentence_transformers import SentenceTransformer

# --- KONFIGURATION ---
BASE_DIR = Path(__file__).parent.resolve()

LAKE_DIR = BASE_DIR / "storage" / "lake"
INDEX_DIR = BASE_DIR / "storage" / "index"
CHROMA_PATH = INDEX_DIR / "chroma"
KUZU_PATH = INDEX_DIR / "kuzu"
LOG_PATH = BASE_DIR / "logs" / "indexer.log"

INDEX_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - INDEXER - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
log = logging.getLogger("BUILDER")

# --- 1. INITIERA DATABASER ---

def init_resources():
    log.info("Initierar databaser...")
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = chroma_client.get_or_create_collection(
        name="adda_knowledge",
        embedding_function=embed_fn
    )
    
    db = kuzu.Database(str(KUZU_PATH))
    conn = kuzu.Connection(db)
    
    return collection, conn

# --- 2. GRAF-SCHEMA (KUZU) ---

def setup_graph_schema(conn):
    try: conn.execute("CREATE NODE TABLE SmartBlock(uuid STRING, type STRING, authority STRING, filename STRING, PRIMARY KEY (uuid))")
    except: pass
    
    try: conn.execute("CREATE NODE TABLE Step(name STRING, PRIMARY KEY (name))")
    except: pass

    try: conn.execute("CREATE REL TABLE BELONGS_TO(FROM SmartBlock TO Step)")
    except: pass
    
    steps = ["step_1_intake", "step_2_level", "step_3_volume", "step_4_strategy", "general"]
    for s in steps:
        try: conn.execute(f"CREATE (:Step {{name: '{s}'}})")
        except: pass
    
    log.info("Graf-schema säkrat.")

# --- 3. PARSING (ROBUST) ---

def repair_yaml(yaml_str):
    """Försöker laga trasiga YAML-rader (t.ex. oavslutade citat)."""
    lines = yaml_str.split('\n')
    fixed_lines = []
    for line in lines:
        # Om en rad innehåller "source_file:" och ett citattecken, men inte slutar med ett citattecken
        if "source_file:" in line and '"' in line and not line.strip().endswith('"'):
            # Lägg till ett slutcitat
            line = line.strip() + '"'
        fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def parse_frontmatter(content):
    try:
        if "---" not in content: return None, None
        parts = content.split("---", 2)
        if len(parts) < 3: return None, None
        
        yaml_content = parts[1]
        text = parts[2].strip()
        
        try:
            meta = yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            # Försök laga och parsa igen
            yaml_content = repair_yaml(yaml_content)
            meta = yaml.safe_load(yaml_content)
            
        return meta, text
    except Exception as e:
        # Om det ändå misslyckas, logga men krascha inte
        # log.error(f"YAML Parse Error (Skipping file): {e}")
        return None, None

def run_indexer():
    collection, conn = init_resources()
    setup_graph_schema(conn)
    
    files = list(LAKE_DIR.glob("*.md"))
    if not files:
        log.warning(f"Inga filer hittades i {LAKE_DIR}.")
        return

    log.info(f"Startar indexering av {len(files)} block...")
    
    count = 0
    skipped = 0
    
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            raw_content = file.read()
        
        meta, text = parse_frontmatter(raw_content)
        
        # Om metadata saknas (pga parse error), skapa nöd-metadata
        if not meta:
            skipped += 1
            # log.warning(f"Skippar {f.name} pga korrupt metadata.")
            continue
        
        uid = meta.get('uuid', str(uuid.uuid4()))
        b_type = meta.get('block_type', 'UNKNOWN')
        auth = meta.get('authority_level', 'UNKNOWN')
        steps = meta.get('process_step', ['general'])
        tags = meta.get('tags', [])
        
        # 1. CHROMA
        searchable_text = f"TYPE: {b_type}\nCONTEXT: {', '.join(steps)}\nTAGS: {', '.join(tags)}\n\n{text}"
        
        collection.upsert(
            ids=[uid],
            documents=[searchable_text], 
            metadatas=[{
                "uuid": uid,
                "type": b_type,
                "step": steps[0] if steps else "general",
                "authority": auth,
                "filename": f.name # Använd filnamnet på disken, inte det trasiga i metadatan
            }]
        )
        
        # 2. KUZU
        try:
            conn.execute(f"""
                MERGE (b:SmartBlock {{uuid: '{uid}'}})
                SET b.type = '{b_type}', b.authority = '{auth}', b.filename = '{f.name}'
            """)
            
            for step in steps:
                conn.execute(f"""
                    MATCH (b:SmartBlock {{uuid: '{uid}'}}), (s:Step {{name: '{step}'}})
                    MERGE (b)-[:BELONGS_TO]->(s)
                """)
        except Exception:
            pass # Ignorera graffel för nu

        count += 1
        if count % 50 == 0:
            log.info(f"Indexerat {count} filer...")

    log.info(f"✨ KLART! {count} block indexerade. ({skipped} skippade pga fel).")

if __name__ == "__main__":
    run_indexer()