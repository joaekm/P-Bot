"""
Context Builder Component - Deterministic Context Retrieval (v5.7)
Replaces Hunter with taxonomy-aware dual retrieval.

v5.7 Changes:
- Returns ContextResult instead of plain dict
- Automatically resolves ALL detected entities via graph during context build
- Includes resolved_locations, resolved_roles, resolved_aliases, learned_rules

v5.6 Changes:
- Added resolve_location() for geo lookups (City -> County -> Area)
- Added resolve_role() for role lookups (Exempelroll -> Kompetensomrade)
- Added resolve_alias() for alias/synonym lookups

v5.5 Changes:
- Uses search_strategy from IntentTarget to decide which sources to query
- Uses search_terms from IntentTarget for optimized searches
- Fully deterministic - no LLM calls here

Retrieval Strategy (controlled by IntentTarget.search_strategy):
1. LAKE: Keyword search on topic_tags (if search_strategy.lake = true)
2. VECTOR: Semantic search with taxonomy filters (if search_strategy.vector = true)
3. GRAPH: Entity-based traversal via Kuzu (if search_strategy.graph = true)
4. RELATIONS: Auto-resolve detected entities via graph (always on)
"""
import logging
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Set

import kuzu

from ..models import (
    IntentTarget, 
    TaxonomyBranch, 
    ScopeContext,
    ContextResult,
    ResolvedLocation,
    ResolvedRole,
    LearnedRule,
)

logger = logging.getLogger("ADDA_ENGINE")


class ContextBuilderComponent:
    """
    Context Builder - Builds context from multiple retrieval strategies.
    
    Takes an IntentTarget and returns relevant documents from:
    - Lake (Markdown files) via keyword matching
    - ChromaDB via semantic search with filters
    - Kuzu via graph traversal
    """
    
    def __init__(self, lake_path: Path, collection, kuzu_conn: Optional[kuzu.Connection] = None):
        """
        Initialize ContextBuilder.
        
        Args:
            lake_path: Path to Markdown files (data_pipeline/output or storage/lake)
            collection: ChromaDB collection
            kuzu_conn: Optional Kuzu connection for graph queries
        """
        self.lake_path = lake_path
        self.collection = collection
        self.kuzu_conn = kuzu_conn
    
    def build_context(self, intent: IntentTarget) -> ContextResult:
        """
        Build context based on IntentTarget.
        
        v5.7: Returns ContextResult with documents AND resolved graph relations.
        v5.5: Uses search_strategy and search_terms from IntentTarget.
        
        Returns ContextResult with:
        - documents: Dict of document_id -> document_data
        - resolved_locations: List of City->County->Area mappings
        - resolved_roles: List of Role->Kompetensområde mappings
        - resolved_aliases: Dict of alias->canonical mappings
        - learned_rules: List of business rules
        """
        candidates = {}
        resolved_locations = []
        resolved_roles = []
        resolved_aliases = {}
        learned_rules = []
        
        # Determine allowed authorities (Ghost Mode)
        allowed_authorities = ["PRIMARY"]
        if not intent.should_block_secondary():
            allowed_authorities.append("SECONDARY")
        
        # Get search terms (v5.5: from LLM)
        search_terms = intent.search_terms if intent.search_terms else intent.detected_topics
        
        logger.info(f"Building context: intent={intent.intent_category}, "
                   f"strategy={intent.search_strategy}, "
                   f"search_terms={search_terms[:3]}, "
                   f"authorities={allowed_authorities}")
        
        # 1. LAKE: Keyword search on topic_tags (if enabled)
        if intent.should_search_lake() and search_terms:
            topic_hits = self._search_by_topics(
                search_terms, 
                allowed_authorities
            )
            candidates.update(topic_hits)
            logger.info(f"Lake search: {len(topic_hits)} hits")
        
        # 2. VECTOR: Semantic search with taxonomy filters (if enabled)
        if intent.should_search_vector() and intent.taxonomy_branches:
            # Use search_terms for query if available, else original query
            query_text = " ".join(search_terms) if search_terms else intent.original_query
            
            vector_hits = self._search_vector(
                query=query_text,
                branches=intent.taxonomy_branches,
                scopes=intent.scope_preference,
                allowed_authorities=allowed_authorities
            )
            # Add vector hits that aren't already in candidates
            for doc_id, doc in vector_hits.items():
                if doc_id not in candidates:
                    candidates[doc_id] = doc
            logger.info(f"Vector search: {len(vector_hits)} hits")
        
        # 3. GRAPH: Entity-based traversal (if enabled)
        if intent.should_search_graph() and intent.detected_entities and self.kuzu_conn:
            graph_hits = self._search_graph_by_entities(
                intent.detected_entities,
                allowed_authorities
            )
            for doc_id, doc in graph_hits.items():
                if doc_id not in candidates:
                    candidates[doc_id] = doc
            logger.info(f"Graph search: {len(graph_hits)} hits")
        
        # 4. FALLBACK: If no results and vector is enabled, do broader search
        if not candidates and intent.should_search_vector():
            logger.info("No results from targeted search, falling back to broad vector search")
            fallback_hits = self._search_vector_fallback(
                intent.original_query,
                allowed_authorities
            )
            candidates.update(fallback_hits)
        
        # 5. CART OPERATIONS: If no search strategy enabled, still allow Synthesizer to run
        # This happens when user is modifying their cart (ADD/DELETE) not searching for info
        if not candidates and not any([intent.should_search_lake(), intent.should_search_vector(), intent.should_search_graph()]):
            logger.info("No search strategy enabled - likely a cart operation")
        
        # =====================================================================
        # 6. RESOLVE GRAPH RELATIONS (v5.7 - ALWAYS ON)
        # Resolve ALL detected entities via graph, regardless of search strategy
        # This ensures geo/role/alias information flows to Planner/Synthesizer
        # =====================================================================
        # v5.7.1: Combine detected_entities + search_terms for better coverage
        # The LLM sometimes puts entities in search_terms instead of detected_entities
        all_entities_to_resolve = set(intent.detected_entities or [])
        all_entities_to_resolve.update(intent.search_terms or [])
        
        if self.kuzu_conn and all_entities_to_resolve:
            logger.info(f"🔍 Resolving {len(all_entities_to_resolve)} entities: {list(all_entities_to_resolve)[:5]}")
            for entity in all_entities_to_resolve:
                # 6a. Geo resolution (City -> County -> Area)
                geo = self.resolve_location(entity)
                if geo:
                    resolved_locations.append(ResolvedLocation(
                        city=geo["city"],
                        county=geo["county"],
                        area_code=geo["area_code"],
                        area_name=geo["area_name"]
                    ))
                
                # 6b. Role resolution (Exempelroll -> Kompetensområde)
                role_info = self.resolve_role(entity)
                if role_info:
                    resolved_roles.append(ResolvedRole(
                        role=role_info["role"],
                        kompetensomrade=role_info["kompetensomrade"]
                    ))
                
                # 6c. Alias resolution
                canonical = self.resolve_alias(entity)
                if canonical:
                    resolved_aliases[entity] = canonical
                
                # 6d. Learned rules
                rules = self.get_learned_relations(entity)
                for rule in rules:
                    learned_rules.append(LearnedRule(
                        subject=rule["predicate"],  # Note: get_learned_relations returns different structure
                        predicate=rule.get("predicate", "relates_to"),
                        object=rule["object"],
                        confidence=rule.get("confidence", 0.8)
                    ))
        
        # Log resolved relations
        if resolved_locations:
            logger.info(f"📍 Resolved locations: {[loc.city for loc in resolved_locations]}")
        if resolved_roles:
            logger.info(f"👤 Resolved roles: {[r.role for r in resolved_roles]}")
        if resolved_aliases:
            logger.info(f"🔄 Resolved aliases: {list(resolved_aliases.keys())}")
        if learned_rules:
            logger.info(f"📋 Learned rules: {len(learned_rules)}")
        
        logger.info(f"Total context: {len(candidates)} docs, {len(resolved_locations)} locations, "
                   f"{len(resolved_roles)} roles, {len(resolved_aliases)} aliases")
        
        return ContextResult(
            documents=candidates,
            resolved_locations=resolved_locations,
            resolved_roles=resolved_roles,
            resolved_aliases=resolved_aliases,
            learned_rules=learned_rules
        )
    
    # =========================================================================
    # SEARCH STRATEGIES
    # =========================================================================
    
    def _search_by_topics(
        self, 
        topics: List[str], 
        allowed_authorities: List[str]
    ) -> Dict[str, Dict]:
        """
        Search Lake files by matching topic_tags in YAML frontmatter.
        """
        hits = {}
        
        for file_path in self.lake_path.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                
                # Parse frontmatter
                parts = raw_content.split("---", 2)
                if len(parts) < 3:
                    continue
                
                try:
                    frontmatter = yaml.safe_load(parts[1])
                except:
                    continue
                
                if not frontmatter:
                    continue
                
                # Check authority
                authority = frontmatter.get('authority_level', 'UNKNOWN')
                if authority not in allowed_authorities:
                    continue
                
                # Check topic_tags for matches
                file_topics = frontmatter.get('topic_tags', [])
                file_topics_lower = [t.lower() for t in file_topics]
                
                matched = False
                for topic in topics:
                    if topic.lower() in file_topics_lower:
                        matched = True
                        break
                
                if matched:
                    doc_id = frontmatter.get('uuid', file_path.stem)
                    hits[doc_id] = {
                        "id": doc_id,
                        "filename": file_path.name,
                        "content": parts[2].strip(),
                        "source": "TOPIC_MATCH",
                        "type": frontmatter.get('block_type', 'UNKNOWN'),
                        "authority": authority,
                        "taxonomy_branch": frontmatter.get('taxonomy_branch', ''),
                        "scope_context": frontmatter.get('scope_context', ''),
                        "topic_tags": file_topics
                    }
                    
            except Exception as e:
                logger.debug(f"Error reading {file_path}: {e}")
                continue
        
        return dict(list(hits.items())[:10])  # Limit to 10 results
    
    def _search_vector(
        self,
        query: str,
        branches: List[TaxonomyBranch],
        scopes: List[ScopeContext],
        allowed_authorities: List[str]
    ) -> Dict[str, Dict]:
        """
        Semantic search with taxonomy filters.
        """
        hits = {}
        
        if not self.collection:
            return hits
        
        # Build filter conditions
        conditions = []
        
        # Authority filter
        if len(allowed_authorities) == 1:
            conditions.append({"authority": allowed_authorities[0]})
        else:
            conditions.append({"authority": {"$in": allowed_authorities}})
        
        # Branch filter (use first branch)
        if branches:
            conditions.append({"taxonomy_branch": branches[0].value})
        
        # Scope filter
        if scopes:
            scope_values = [s.value for s in scopes]
            if len(scope_values) == 1:
                conditions.append({"scope_context": scope_values[0]})
            else:
                conditions.append({"scope_context": {"$in": scope_values}})
        
        # Combine conditions
        if len(conditions) == 1:
            where_clause = conditions[0]
        elif len(conditions) > 1:
            where_clause = {"$and": conditions}
        else:
            where_clause = None
        
        try:
            logger.debug(f"Vector search filter: {where_clause}")
            res = self.collection.query(
                query_texts=[query],
                n_results=10,
                where=where_clause
            )
            
            if not res['ids'] or not res['ids'][0]:
                return hits
            
            for i, doc_id in enumerate(res['ids'][0]):
                meta = res['metadatas'][0][i]
                hits[doc_id] = {
                    "id": doc_id,
                    "filename": meta.get('filename', 'unknown'),
                    "content": res['documents'][0][i],
                    "source": "VECTOR",
                    "type": meta.get('type', 'UNKNOWN'),
                    "authority": meta.get('authority', 'UNKNOWN'),
                    "taxonomy_branch": meta.get('taxonomy_branch', ''),
                    "scope_context": meta.get('scope_context', '')
                }
                
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
        
        return hits
    
    def _search_vector_fallback(
        self,
        query: str,
        allowed_authorities: List[str]
    ) -> Dict[str, Dict]:
        """
        Fallback vector search without taxonomy filters.
        Used when targeted search returns no results.
        """
        hits = {}
        
        if not self.collection:
            return hits
        
        # Only filter by authority
        if len(allowed_authorities) == 1:
            where_clause = {"authority": allowed_authorities[0]}
        else:
            where_clause = {"authority": {"$in": allowed_authorities}}
        
        try:
            res = self.collection.query(
                query_texts=[query],
                n_results=8,
                where=where_clause
            )
            
            if not res['ids'] or not res['ids'][0]:
                return hits
            
            for i, doc_id in enumerate(res['ids'][0]):
                meta = res['metadatas'][0][i]
                hits[doc_id] = {
                    "id": doc_id,
                    "filename": meta.get('filename', 'unknown'),
                    "content": res['documents'][0][i],
                    "source": "VECTOR_FALLBACK",
                    "type": meta.get('type', 'UNKNOWN'),
                    "authority": meta.get('authority', 'UNKNOWN'),
                    "taxonomy_branch": meta.get('taxonomy_branch', ''),
                    "scope_context": meta.get('scope_context', '')
                }
                
        except Exception as e:
            logger.error(f"Fallback vector search failed: {e}")
        
        return hits
    
    def _search_graph_by_entities(
        self,
        entities: List[str],
        allowed_authorities: List[str]
    ) -> Dict[str, Dict]:
        """
        Search Kuzu graph for blocks mentioning specific entities.
        """
        hits = {}
        
        if not self.kuzu_conn:
            return hits
        
        for entity in entities[:3]:  # Limit to first 3 entities
            try:
                safe_entity = entity.replace("'", "''")
                
                # Query blocks that mention this entity
                result = self.kuzu_conn.execute(f"""
                    MATCH (b:Block)-[:MENTIONS_ENTITY]->(e:Entity {{name: '{safe_entity}'}})
                    RETURN b.uuid, b.type, b.authority, b.filename
                """)
                
                while result.has_next():
                    row = result.get_next()
                    uuid, block_type, authority, filename = row
                    
                    # Check authority
                    if authority not in allowed_authorities:
                        continue
                    
                    # Read content from file
                    content = self._read_file_content(filename)
                    
                    if uuid not in hits:
                        hits[uuid] = {
                            "id": uuid,
                            "filename": filename,
                            "content": content,
                            "source": "GRAPH",
                            "type": block_type,
                            "authority": authority,
                            "matched_entity": entity
                        }
                        
            except Exception as e:
                logger.debug(f"Graph search error for entity '{entity}': {e}")
        
        return dict(list(hits.items())[:5])  # Limit to 5 results
    
    def _read_file_content(self, filename: str) -> str:
        """Read content from a Lake file."""
        file_path = self.lake_path / filename
        
        if not file_path.exists():
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract content after frontmatter
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
            return content
            
        except Exception:
            return ""
    
    # =========================================================================
    # GRAPH RESOLVERS (v5.6) - Lookup learned relations
    # =========================================================================
    
    def resolve_location(self, location: str) -> Optional[Dict]:
        """
        Resolve a location (city/kommun) to its anbudsområde via the graph.
        
        Graph traversal: City -> County -> Area
        
        Args:
            location: Name of city/kommun (e.g., "Härnösand")
            
        Returns:
            Dict with city, county, area_code, area_name or None if not found
        """
        if not self.kuzu_conn:
            logger.debug("No Kuzu connection available for geo lookup")
            return None
        
        safe_loc = location.replace("'", "''")
        
        try:
            # Try exact match first
            result = self.kuzu_conn.execute(f"""
                MATCH (c:City {{name: '{safe_loc}'}})-[:LOCATED_IN]->(county:County)-[:BELONGS_TO_AREA]->(area:Area)
                RETURN c.name, county.name, area.code, area.name
            """)
            
            if result.has_next():
                row = result.get_next()
                return {
                    "city": row[0],
                    "county": row[1],
                    "area_code": row[2],
                    "area_name": row[3]
                }
            
            # Try case-insensitive match
            result = self.kuzu_conn.execute(f"""
                MATCH (c:City)-[:LOCATED_IN]->(county:County)-[:BELONGS_TO_AREA]->(area:Area)
                WHERE lower(c.name) = lower('{safe_loc}')
                RETURN c.name, county.name, area.code, area.name
            """)
            
            if result.has_next():
                row = result.get_next()
                return {
                    "city": row[0],
                    "county": row[1],
                    "area_code": row[2],
                    "area_name": row[3]
                }
                
        except Exception as e:
            logger.debug(f"Geo lookup failed for '{location}': {e}")
        
        return None
    
    def resolve_role(self, role: str) -> Optional[Dict]:
        """
        Resolve an exempelroll to its kompetensområde via the graph.
        
        Graph traversal: Exempelroll -> Kompetensomrade
        
        Args:
            role: Name of role (e.g., "Fullstackutvecklare")
            
        Returns:
            Dict with role, kompetensomrade or None if not found
        """
        if not self.kuzu_conn:
            logger.debug("No Kuzu connection available for role lookup")
            return None
        
        safe_role = role.replace("'", "''")
        
        try:
            # Try exact match
            result = self.kuzu_conn.execute(f"""
                MATCH (r:Exempelroll {{name: '{safe_role}'}})-[:BELONGS_TO_OMRADE]->(k:Kompetensomrade)
                RETURN r.name, k.name
            """)
            
            if result.has_next():
                row = result.get_next()
                return {
                    "role": row[0],
                    "kompetensomrade": row[1]
                }
            
            # Try case-insensitive match
            result = self.kuzu_conn.execute(f"""
                MATCH (r:Exempelroll)-[:BELONGS_TO_OMRADE]->(k:Kompetensomrade)
                WHERE lower(r.name) = lower('{safe_role}')
                RETURN r.name, k.name
            """)
            
            if result.has_next():
                row = result.get_next()
                return {
                    "role": row[0],
                    "kompetensomrade": row[1]
                }
                
        except Exception as e:
            logger.debug(f"Role lookup failed for '{role}': {e}")
        
        return None
    
    def resolve_alias(self, term: str) -> Optional[str]:
        """
        Resolve an alias/synonym to its canonical form via the graph.
        
        Graph lookup: Alias -> canonical name
        
        Args:
            term: Potential alias or alternate spelling
            
        Returns:
            Canonical form if alias found, else None
        """
        if not self.kuzu_conn:
            logger.debug("No Kuzu connection available for alias lookup")
            return None
        
        safe_term = term.replace("'", "''")
        
        try:
            # Try exact match
            result = self.kuzu_conn.execute(f"""
                MATCH (a:Alias {{alias: '{safe_term}'}})
                RETURN a.canonical, a.entity_type
            """)
            
            if result.has_next():
                row = result.get_next()
                logger.info(f"Resolved alias: '{term}' -> '{row[0]}' ({row[1]})")
                return row[0]
            
            # Try case-insensitive match
            result = self.kuzu_conn.execute(f"""
                MATCH (a:Alias)
                WHERE lower(a.alias) = lower('{safe_term}')
                RETURN a.canonical, a.entity_type
            """)
            
            if result.has_next():
                row = result.get_next()
                logger.info(f"Resolved alias (case-insensitive): '{term}' -> '{row[0]}' ({row[1]})")
                return row[0]
                
        except Exception as e:
            logger.debug(f"Alias lookup failed for '{term}': {e}")
        
        return None
    
    def get_area_from_county(self, county: str) -> Optional[Dict]:
        """
        Get anbudsområde directly from county name.
        Useful when we have county but not city.
        
        Args:
            county: Name of county (e.g., "Västernorrland")
            
        Returns:
            Dict with county, area_code, area_name or None if not found
        """
        if not self.kuzu_conn:
            return None
        
        safe_county = county.replace("'", "''")
        
        try:
            result = self.kuzu_conn.execute(f"""
                MATCH (c:County {{name: '{safe_county}'}})-[:BELONGS_TO_AREA]->(a:Area)
                RETURN c.name, a.code, a.name
            """)
            
            if result.has_next():
                row = result.get_next()
                return {
                    "county": row[0],
                    "area_code": row[1],
                    "area_name": row[2]
                }
                
        except Exception as e:
            logger.debug(f"County->Area lookup failed for '{county}': {e}")
        
        return None
    
    def get_learned_relations(self, subject: str) -> List[Dict]:
        """
        Get all learned relations for a subject.
        
        Args:
            subject: Entity to look up
            
        Returns:
            List of dicts with predicate, object, confidence
        """
        if not self.kuzu_conn:
            return []
        
        relations = []
        safe_subject = subject.replace("'", "''")
        
        try:
            result = self.kuzu_conn.execute(f"""
                MATCH (lr:LearnedRelation {{subject: '{safe_subject}'}})
                RETURN lr.predicate, lr.object, lr.confidence
            """)
            
            while result.has_next():
                row = result.get_next()
                relations.append({
                    "predicate": row[0],
                    "object": row[1],
                    "confidence": row[2]
                })
                
        except Exception as e:
            logger.debug(f"Learned relations lookup failed for '{subject}': {e}")
        
        return relations
    
    # =========================================================================
    # LEGACY COMPATIBILITY (for gradual migration)
    # =========================================================================
    
    def search_lake(
        self, 
        target_step: str, 
        target_type: str, 
        allowed_authorities: List[str] = None
    ) -> Dict[str, Dict]:
        """
        Legacy method for backward compatibility with old Hunter interface.
        """
        if allowed_authorities is None:
            allowed_authorities = ["PRIMARY", "SECONDARY"]
        
        hits = {}
        if not target_step:
            return hits
        
        # Smart filename search
        pattern = f"{target_step}*{target_type}*.md"
        if target_type == "ALL":
            pattern = f"{target_step}*.md"
        
        logger.info(f"Legacy lake search: {pattern}")
        
        for file_path in self.lake_path.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                
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
                
                if authority not in allowed_authorities:
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
        
        return dict(list(hits.items())[:5])
    
    def search_vector(
        self, 
        query: str, 
        filter_step: str = None, 
        allowed_authorities: List[str] = None
    ) -> Dict[str, Dict]:
        """
        Legacy method for backward compatibility with old Hunter interface.
        """
        if allowed_authorities is None:
            allowed_authorities = ["PRIMARY", "SECONDARY"]
        
        hits = {}
        if not self.collection:
            return hits
        
        conditions = []
        
        if filter_step and filter_step != "general":
            conditions.append({"step": filter_step})
        
        if len(allowed_authorities) == 1:
            conditions.append({"authority": allowed_authorities[0]})
        else:
            conditions.append({"authority": {"$in": allowed_authorities}})
        
        if len(conditions) == 1:
            where_clause = conditions[0]
        elif len(conditions) > 1:
            where_clause = {"$and": conditions}
        else:
            where_clause = None
        
        try:
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
            logger.error(f"Legacy vector search failed: {e}")
        
        return hits


