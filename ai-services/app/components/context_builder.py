"""
Context Builder Component v5.24

Pipeline placering:
    IntentAnalyzer → [ContextBuilder] → Planner → AvropsContainerManager → Synthesizer
         ↓                 ↓
       intent           context

IN:  intent: dict med branches, search_terms, query
OUT: dict med documents:
    {
        "documents": [
            {"id": "...", "filename": "...", "content": "...", "branch": "ROLES", "type": "RULE"}
        ]
    }

Metod:
1. GRAF: Hitta dokument via Block→Branch relationer
2. VEKTOR: Semantisk ranking av hittade dokument
3. KOMBINERA: Graf-träffar boostar vektor-ranking
"""
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional
import kuzu

logger = logging.getLogger("ADDA_ENGINE")


class ContextBuilderComponent:
    """
    Context Builder - Graf för att hitta, Vektor för att ranka.
    Ingen filsökning - allt går via index.
    """
    
    def __init__(self, lake_path: Path, collection, kuzu_conn: Optional[kuzu.Connection] = None):
        self.lake_path = lake_path
        self.collection = collection
        self.kuzu_conn = kuzu_conn
    
    def build_context(self, intent: Dict) -> Dict:
        """Fetch and rank documents based on intent."""
        branches = intent.get("branches", ["ROLES"])
        query = intent.get("query", "")
        search_terms = intent.get("search_terms", [])
        
        # STEP 1: GRAF - hitta dokument-IDs för relevanta branches
        graph_doc_ids = self._get_docs_from_graph(branches)
        logger.info(f"Graf: {len(graph_doc_ids)} docs för {branches}")
        
        # STEP 2: VEKTOR - semantisk sökning och ranking
        vector_query = query or " ".join(search_terms)
        ranked_docs = self._search_and_rank(vector_query, graph_doc_ids)
        
        logger.info(f"Total: {len(ranked_docs)} docs")
        
        return {"documents": ranked_docs}
    
    def _get_docs_from_graph(self, branches: List[str]) -> Set[str]:
        """Hämta dokument-IDs som tillhör givna branches via grafen."""
        doc_ids = set()
        
        if not self.kuzu_conn:
            logger.warning("Ingen Kuzu-koppling - hoppar över graf-sökning")
            return doc_ids
        
        try:
            for branch in branches:
                safe_branch = branch.replace("'", "''")
                result = self.kuzu_conn.execute(f"""
                    MATCH (b:Block)-[:BELONGS_TO_BRANCH]->(br:Branch)
                    WHERE br.name = '{safe_branch}'
                    RETURN b.uuid
                """)
                count = 0
                while result.has_next():
                    doc_ids.add(result.get_next()[0])
                    count += 1
                logger.debug(f"  Branch {branch}: {count} docs")
                    
        except Exception as e:
            logger.error(f"Graf-sökning misslyckades: {e}")
        
        return doc_ids
    
    def _search_and_rank(self, query: str, graph_doc_ids: Set[str]) -> List[Dict]:
        """Vektor-sökning med boost för graf-träffar."""
        if not self.collection:
            logger.warning("Ingen ChromaDB-koppling")
            return []
        
        if not query:
            logger.warning("Tom query - kan inte söka")
            return []
        
        try:
            # Hämta fler resultat för att fånga graf-träffar
            res = self.collection.query(
                query_texts=[query],
                n_results=30,
                where={"authority": "PRIMARY"}
            )
            
            if not res['ids'] or not res['ids'][0]:
                logger.info("Vektor: 0 träffar")
                return []
            
            results = []
            for i, doc_id in enumerate(res['ids'][0]):
                meta = res['metadatas'][0][i]
                
                # Beräkna score: vektor-rank + graf-boost
                # Lägre rank = bättre (position i vektor-resultat)
                vector_rank = i
                
                # Boost om dokumentet finns i graf-resultaten (-15 poäng = högre ranking)
                is_graph_match = doc_id in graph_doc_ids
                graph_boost = -15 if is_graph_match else 0
                
                combined_score = vector_rank + graph_boost
                
                results.append({
                    "id": doc_id,
                    "filename": meta.get('filename', 'unknown'),
                    "branch": meta.get('taxonomy_branch', ''),
                    "type": meta.get('type', 'UNKNOWN'),
                    "content": res['documents'][0][i],
                    "source": "GRAPH+VECTOR" if is_graph_match else "VECTOR",
                    "_score": combined_score
                })
            
            # Sortera på kombinerad score (lägst först)
            results.sort(key=lambda d: d["_score"])
            
            # Logga topp-resultat
            if results:
                top3 = [f"{d['filename'][:30]}({d['source']})" for d in results[:3]]
                logger.info(f"Topp 3: {', '.join(top3)}")
            
            return results[:15]
            
        except Exception as e:
            logger.error(f"Vektor-sökning misslyckades: {e}")
            return []
