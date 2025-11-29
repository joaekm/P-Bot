"""
Hunter Component - Document Search (Lake & Vector)
Handles both exact file-based search and semantic vector search.
"""
import logging
import yaml
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger("ADDA_ENGINE")


class HunterComponent:
    """
    Hunter - Searches for relevant documents in Lake and ChromaDB.
    
    Two search strategies:
    - Lake Search: Exact file-based search using glob patterns
    - Vector Search: Semantic search using ChromaDB embeddings
    """
    
    def __init__(self, lake_path: Path, collection):
        self.lake_path = lake_path
        self.collection = collection
    
    def search_lake(self, target_step: str, target_type: str, allowed_authorities: List[str] = None) -> Dict[str, Dict]:
        """Search files in lake based on Planner's Step/Type with authority filter."""
        if allowed_authorities is None:
            allowed_authorities = ["PRIMARY", "SECONDARY"]
            
        hits = {}
        if not target_step:
            return hits
        
        # Smart filename search: "step_3_volume_RULE_*.md"
        pattern = f"{target_step}*{target_type}*.md"
        
        # Fallback: If planner says "ALL", search broader
        if target_type == "ALL":
            pattern = f"{target_step}*.md"
            
        logger.info(f"Hunter scanning lake for: {pattern} (allowed authorities: {allowed_authorities})")
        
        for file_path in self.lake_path.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                
                # Parse frontmatter to check authority_level
                parts = raw_content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        authority = frontmatter.get('authority_level', 'UNKNOWN')
                    except:
                        authority = 'UNKNOWN'
                    content = parts[2].strip()
                else:
                    content = raw_content
                    authority = 'UNKNOWN'
                
                # KILLSWITCH: Skip if authority not in allowed list
                if authority not in allowed_authorities:
                    logger.debug(f"🚫 BLOCKED {file_path.name} (authority: {authority} not in {allowed_authorities})")
                    continue
                    
                doc_id = file_path.stem
                hits[doc_id] = {
                    "id": doc_id,
                    "filename": file_path.name,
                    "content": content,
                    "source": "HUNTER (Direct Hit)",
                    "type": target_type,
                    "authority": authority
                }
            except Exception:
                continue
                
        # Limit Hunter results (max 5 relevant rules)
        return dict(list(hits.items())[:5])
    
    def search_vector(self, query: str, filter_step: str = None, allowed_authorities: List[str] = None) -> Dict[str, Dict]:
        """Semantic search with authority filter."""
        if allowed_authorities is None:
            allowed_authorities = ["PRIMARY", "SECONDARY"]
            
        hits = {}
        if not self.collection:
            return hits
        
        # Build where clause with step AND authority filter
        conditions = []
        
        if filter_step and filter_step != "general":
            conditions.append({"step": filter_step})
        
        # Authority filter (KILLSWITCH)
        if len(allowed_authorities) == 1:
            conditions.append({"authority": allowed_authorities[0]})
        else:
            conditions.append({"authority": {"$in": allowed_authorities}})
        
        # Combine conditions
        if len(conditions) == 1:
            where_clause = conditions[0]
        elif len(conditions) > 1:
            where_clause = {"$and": conditions}
        else:
            where_clause = None
            
        try:
            logger.info(f"Vector search with filter: {where_clause}")
            res = self.collection.query(
                query_texts=[query],
                n_results=10,
                where=where_clause
            )
            
            if not res['ids']:
                return hits
            
            for i, doc_id in enumerate(res['ids'][0]):
                meta = res['metadatas'][0][i]
                hits[doc_id] = {
                    "id": doc_id,
                    "filename": meta.get('filename', 'unknown'),
                    "content": res['documents'][0][i],
                    "source": "VECTOR",
                    "type": meta.get('type', 'UNKNOWN'),
                    "authority": meta.get('authority', 'UNKNOWN')
                }
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            
        return hits

