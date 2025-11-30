"""
Adda P-Bot Vocabulary Generator v2
Builds hierarchical vocabulary structure from Smart Blocks in the Lake.
"""
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Set, List, Any
from collections import defaultdict
from datetime import datetime

try:
    # When imported as a module
    from .models import TaxonomyRoot, TaxonomyBranch, ScopeContext, VALID_BRANCHES
except ImportError:
    # When run directly as a script
    from models import TaxonomyRoot, TaxonomyBranch, ScopeContext, VALID_BRANCHES

log = logging.getLogger("Pipeline")


class VocabularyGenerator:
    """
    Scans Smart Block markdown files and extracts vocabulary.
    Builds a hierarchical structure: Root -> Branch -> Scope -> {topics, entities}
    """
    
    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            # Default to data_pipeline/output relative to this file
            base_dir = Path(__file__).resolve().parent
            output_dir = base_dir / "output"
        
        self.output_dir = output_dir
        
        # Nested structure: Root -> Branch -> Scope -> {topics, entities, files}
        self.vocabulary: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
        self._initialize_structure()
        
        # Flat collections for quick lookups
        self.all_topics: Set[str] = set()
        self.all_entities: Set[str] = set()
        self.all_tags: Set[str] = set()
        self.block_types: Set[str] = set()
        
        # Statistics
        self.files_processed = 0
        self.errors: List[Dict] = []
    
    def _initialize_structure(self):
        """Initialize the nested vocabulary structure."""
        for root in TaxonomyRoot:
            self.vocabulary[root.value] = {}
            for branch in VALID_BRANCHES.get(root, []):
                self.vocabulary[root.value][branch.value] = {}
                for scope in ScopeContext:
                    self.vocabulary[root.value][branch.value][scope.value] = {
                        "topics": set(),
                        "entities": set(),
                        "files": [],
                        "count": 0
                    }
    
    def scan_outputs(self, scan_dir: Path = None) -> Dict:
        """
        Scan all markdown files and extract vocabulary.
        Returns the hierarchical vocabulary structure.
        """
        if scan_dir is None:
            scan_dir = self.output_dir
        
        output_dir = scan_dir
        
        if not output_dir.exists():
            log.error(f"Directory not found: {output_dir}")
            return {}
        
        md_files = list(output_dir.glob("*.md"))
        log.info(f"Scanning {len(md_files)} markdown files for vocabulary...")
        
        for md_file in md_files:
            self._process_file(md_file)
        
        log.info(f"Processed {self.files_processed} files, {len(self.errors)} errors")
        log.info(f"Found {len(self.all_topics)} unique topics, {len(self.all_entities)} unique entities")
        
        return self.to_dict()
    
    def _process_file(self, file_path: Path):
        """Process a single markdown file and extract vocabulary."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter
            if not content.startswith("---"):
                return
            
            parts = content.split("---", 2)
            if len(parts) < 3:
                return
            
            try:
                frontmatter = yaml.safe_load(parts[1])
            except yaml.YAMLError as e:
                self.errors.append({"file": file_path.name, "error": f"YAML parse error: {e}"})
                return
            
            if not frontmatter:
                return
            
            # Extract taxonomy classification
            root = frontmatter.get("taxonomy_root", "DOMAIN_OBJECTS")
            branch = frontmatter.get("taxonomy_branch", "ROLES")
            scope = frontmatter.get("scope_context", "FRAMEWORK_SPECIFIC")
            
            # Validate enums (use defaults if invalid)
            try:
                root = TaxonomyRoot(root).value
            except ValueError:
                root = TaxonomyRoot.DOMAIN_OBJECTS.value
            
            try:
                branch = TaxonomyBranch(branch).value
            except ValueError:
                branch = TaxonomyBranch.ROLES.value
            
            try:
                scope = ScopeContext(scope).value
            except ValueError:
                scope = ScopeContext.FRAMEWORK_SPECIFIC.value
            
            # Ensure branch is valid for root
            valid_branches = [b.value for b in VALID_BRANCHES.get(TaxonomyRoot(root), [])]
            if branch not in valid_branches and valid_branches:
                branch = valid_branches[0]
            
            # Extract vocabulary items
            topics = frontmatter.get("topic_tags", [])
            entities = frontmatter.get("entities", [])
            tags = frontmatter.get("tags", [])
            block_type = frontmatter.get("block_type", "DEFINITION")
            
            # Add to hierarchical structure
            bucket = self.vocabulary[root][branch][scope]
            bucket["topics"].update(topics)
            bucket["entities"].update(entities)
            bucket["files"].append(file_path.name)
            bucket["count"] += 1
            
            # Add to flat collections
            self.all_topics.update(topics)
            self.all_entities.update(entities)
            self.all_tags.update(tags)
            self.block_types.add(block_type)
            
            self.files_processed += 1
            
        except Exception as e:
            self.errors.append({"file": file_path.name, "error": str(e)})
    
    def to_dict(self) -> Dict:
        """Convert vocabulary to serializable dictionary."""
        result = {}
        
        for root, branches in self.vocabulary.items():
            result[root] = {}
            for branch, scopes in branches.items():
                result[root][branch] = {}
                for scope, data in scopes.items():
                    if data["count"] > 0:
                        result[root][branch][scope] = {
                            "topics": sorted(list(data["topics"])),
                            "entities": sorted(list(data["entities"])),
                            "file_count": data["count"]
                        }
                
                # Remove empty branches
                if not result[root][branch]:
                    del result[root][branch]
            
            # Remove empty roots
            if not result[root]:
                del result[root]
        
        return result
    
    def get_flat_vocabulary(self) -> Dict:
        """Get flat vocabulary structure for quick lookups."""
        return {
            "topics": sorted(list(self.all_topics)),
            "entities": sorted(list(self.all_entities)),
            "tags": sorted(list(self.all_tags)),
            "block_types": sorted(list(self.block_types))
        }
    
    def save_vocabulary(self, output_path: Path = None):
        """Save vocabulary to JSON file."""
        if output_path is None:
            output_path = self.output_dir / "vocabulary.json"
        
        vocab_data = {
            "generated": datetime.now().isoformat(),
            "files_processed": self.files_processed,
            "summary": {
                "unique_topics": len(self.all_topics),
                "unique_entities": len(self.all_entities),
                "unique_tags": len(self.all_tags),
                "block_types": sorted(list(self.block_types))
            },
            "hierarchical": self.to_dict(),
            "flat": self.get_flat_vocabulary()
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vocab_data, f, ensure_ascii=False, indent=2)
        
        log.info(f"Saved vocabulary to {output_path}")
        return output_path
    
    def get_stats(self) -> str:
        """Generate statistics report."""
        lines = []
        lines.append("=" * 70)
        lines.append("VOCABULARY STATISTICS")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Files processed: {self.files_processed}")
        lines.append(f"Errors: {len(self.errors)}")
        lines.append("=" * 70)
        lines.append("")
        
        lines.append("SUMMARY:")
        lines.append(f"  Unique topics: {len(self.all_topics)}")
        lines.append(f"  Unique entities: {len(self.all_entities)}")
        lines.append(f"  Unique tags: {len(self.all_tags)}")
        lines.append(f"  Block types: {sorted(list(self.block_types))}")
        lines.append("")
        
        lines.append("DISTRIBUTION BY ROOT -> BRANCH -> SCOPE:")
        lines.append("-" * 50)
        
        for root in TaxonomyRoot:
            root_total = sum(
                self.vocabulary[root.value][b.value][s.value]["count"]
                for b in VALID_BRANCHES.get(root, [])
                for s in ScopeContext
            )
            if root_total == 0:
                continue
            
            lines.append(f"\n[{root.value}] ({root_total} files)")
            
            for branch in VALID_BRANCHES.get(root, []):
                branch_total = sum(
                    self.vocabulary[root.value][branch.value][s.value]["count"]
                    for s in ScopeContext
                )
                if branch_total == 0:
                    continue
                
                lines.append(f"  {branch.value}: {branch_total} files")
                
                for scope in ScopeContext:
                    data = self.vocabulary[root.value][branch.value][scope.value]
                    if data["count"] > 0:
                        lines.append(f"    - {scope.value}: {data['count']} files, {len(data['topics'])} topics, {len(data['entities'])} entities")
        
        if self.errors:
            lines.append("")
            lines.append("ERRORS:")
            lines.append("-" * 50)
            for err in self.errors[:10]:
                lines.append(f"  {err['file']}: {err['error'][:60]}...")
            if len(self.errors) > 10:
                lines.append(f"  ... and {len(self.errors) - 10} more")
        
        return "\n".join(lines)


def build_vocabulary(output_dir: Path = None, save_path: Path = None) -> Dict:
    """
    Convenience function to build vocabulary from pipeline output.
    Returns the vocabulary dictionary.
    """
    generator = VocabularyGenerator(output_dir)
    vocab = generator.scan_outputs()
    
    if save_path:
        generator.save_vocabulary(save_path)
    
    return vocab


if __name__ == "__main__":
    # Run as standalone script
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Determine paths - scan from data_pipeline/output
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "output"
    
    if not output_dir.exists():
        log.error(f"Output directory not found: {output_dir}")
        log.error("Run start_pipeline.py first to generate Smart Blocks.")
        sys.exit(1)
    
    generator = VocabularyGenerator(output_dir)
    generator.scan_outputs()
    
    # Save vocabulary to same output directory
    generator.save_vocabulary(output_dir / "vocabulary.json")
    
    # Save stats
    stats_path = output_dir / "vocabulary_stats.txt"
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(generator.get_stats())
    log.info(f"Saved stats to {stats_path}")
    
    # Print summary
    print(generator.get_stats())

