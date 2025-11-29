#!/usr/bin/env python3
"""
Knowledge Base Management CLI

A command-line tool for inspecting and managing the ChromaDB vector database.

Usage:
    python manage_knowledge.py list
    python manage_knowledge.py add --file "./data/avtal.pdf" --category "rules"
    python manage_knowledge.py remove --file "avtal.pdf"
    python manage_knowledge.py query "semesterersättning" --filter_category "rules"
    python manage_knowledge.py stats
"""

import argparse
import sys
import os
from datetime import datetime
from tabulate import tabulate

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rag_service


def cmd_list(args):
    """List all indexed documents."""
    docs = rag_service.list_all_documents()
    
    if not docs:
        print("No documents indexed.")
        return
    
    # Format as table
    table_data = []
    for doc in docs:
        table_data.append([
            doc['filename'],
            doc['category'],
            doc['chunk_count']
        ])
    
    print(f"\n📚 Indexed Documents ({len(docs)} files)\n")
    print(tabulate(
        table_data,
        headers=['Filename', 'Category', 'Chunks'],
        tablefmt='simple_grid'
    ))
    print()


def cmd_add(args):
    """Add a document to the knowledge base."""
    file_path = args.file
    category = args.category
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return 1
    
    filename = os.path.basename(file_path)
    print(f"📄 Adding '{filename}' to category '{category}'...")
    
    success = rag_service.add_document(file_path, filename, category)
    
    if success:
        print(f"✅ Successfully indexed '{filename}'")
        return 0
    else:
        print(f"❌ Failed to index '{filename}'")
        return 1


def cmd_remove(args):
    """Remove a document from the knowledge base."""
    filename = args.file
    
    print(f"🗑️  Removing '{filename}'...")
    
    success = rag_service.remove_document(filename)
    
    if success:
        print(f"✅ Successfully removed '{filename}'")
        return 0
    else:
        print(f"❌ Failed to remove '{filename}' (may not exist)")
        return 1


def cmd_query(args):
    """Query the knowledge base."""
    query_text = args.query
    category = args.filter_category
    n_results = args.n or 5
    
    print(f"\n🔍 Querying: \"{query_text}\"")
    if category:
        print(f"   Filter: category = '{category}'")
    print()
    
    if category:
        # Use manifest-based query
        manifest = {"allowed_categories": [category], "specific_files": []}
        results = rag_service.query_with_manifest(query_text, manifest, n_results)
    else:
        results = rag_service.query_knowledge_base(query_text, n_results)
    
    documents = results.get('documents', [])
    metadatas = results.get('metadatas', [])
    
    if not documents:
        print("No results found.")
        return
    
    print(f"📋 Found {len(documents)} results:\n")
    
    for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
        source = meta.get('source', 'unknown') if meta else 'unknown'
        cat = meta.get('category', 'general') if meta else 'general'
        
        # Truncate long documents
        preview = doc[:300] + "..." if len(doc) > 300 else doc
        
        print(f"{'─' * 60}")
        print(f"Result {i} | Source: {source} | Category: {cat}")
        print(f"{'─' * 60}")
        print(preview)
        print()


def cmd_stats(args):
    """Show knowledge base statistics."""
    stats = rag_service.get_collection_stats()
    
    print("\n📊 Knowledge Base Statistics\n")
    print(f"Total chunks:    {stats['total_chunks']}")
    print(f"Total documents: {stats['total_documents']}")
    
    print("\nChunks by category:")
    for cat, count in stats.get('categories', {}).items():
        print(f"  - {cat}: {count}")
    
    print()


def cmd_clear(args):
    """Clear all documents from the knowledge base."""
    if not args.confirm:
        print("⚠️  This will delete ALL indexed documents!")
        print("   Add --confirm to proceed.")
        return 1
    
    docs = rag_service.list_all_documents()
    
    if not docs:
        print("Knowledge base is already empty.")
        return 0
    
    print(f"🗑️  Removing {len(docs)} documents...")
    
    for doc in docs:
        rag_service.remove_document(doc['filename'])
    
    print("✅ Knowledge base cleared.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Knowledge Base Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s add --file "./data/raw/rules/avtal.pdf" --category "rules"
  %(prog)s remove --file "avtal.pdf"
  %(prog)s query "kompetensnivå 3" --filter_category "levels"
  %(prog)s stats
  %(prog)s clear --confirm
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all indexed documents')
    list_parser.set_defaults(func=cmd_list)
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a document to the knowledge base')
    add_parser.add_argument('--file', '-f', required=True, help='Path to the file to add')
    add_parser.add_argument('--category', '-c', required=True, 
                          choices=['roles', 'levels', 'rules', 'general'],
                          help='Category for the document')
    add_parser.set_defaults(func=cmd_add)
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a document from the knowledge base')
    remove_parser.add_argument('--file', '-f', required=True, help='Filename to remove')
    remove_parser.set_defaults(func=cmd_remove)
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the knowledge base')
    query_parser.add_argument('query', help='Search query')
    query_parser.add_argument('--filter_category', '-c', 
                             choices=['roles', 'levels', 'rules', 'general'],
                             help='Filter by category')
    query_parser.add_argument('-n', type=int, default=5, help='Number of results (default: 5)')
    query_parser.set_defaults(func=cmd_query)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show knowledge base statistics')
    stats_parser.set_defaults(func=cmd_stats)
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all documents')
    clear_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')
    clear_parser.set_defaults(func=cmd_clear)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args) or 0


if __name__ == '__main__':
    try:
        # Try to import tabulate, fall back if not available
        from tabulate import tabulate
    except ImportError:
        # Simple fallback
        def tabulate(data, headers, tablefmt=None):
            result = "  ".join(headers) + "\n"
            result += "-" * 50 + "\n"
            for row in data:
                result += "  ".join(str(x) for x in row) + "\n"
            return result
    
    sys.exit(main())



