"""Main interface with optional cloud mode."""
from agent import run_agent
from memory import search_memory, list_all_papers
from citation_graph import add_citation_edge, print_citation_tree
import os

# Check if using cloud
USE_CLOUD = os.getenv("SUPABASE_URL") is not None

if USE_CLOUD:
    from supabase_db import search_memory as search_memory_cloud
    from supabase_db import list_all_papers as list_all_papers_cloud
    from supabase_graph import add_citation_edge as add_citation_edge_cloud
    from supabase_graph import print_citation_tree as print_citation_tree_cloud
    
    search_memory = search_memory_cloud
    list_all_papers = list_all_papers_cloud
    add_citation_edge = add_citation_edge_cloud
    print_citation_tree = print_citation_tree_cloud

def main():
    mode = "☁️ CLOUD" if USE_CLOUD else "💻 LOCAL"
    
    while True:
        print("\n" + "="*60)
        print(f"🧠 Research Agent {mode}")
        print("="*60)
        print("  1 — Search for new papers")
        print("  2 — Search papers in memory")
        print("  3 — List all papers")
        print("  4 — View citation graph")
        print("  5 — Add citation link")
        print("  6 — Exit")

        choice = input("\nChoose (1-6): ").strip()

        if choice == "1":
            query = input("Research topic: ").strip()
            run_agent(query)

        elif choice == "2":
            query = input("Search query: ").strip()
            results = search_memory(query, n_results=3)
            if results:
                print(f"\nFound {len(results)} papers:\n")
                for i, r in enumerate(results, 1):
                    print(f"{'='*50}")
                    print(f"Result {i}:")
                    print(r["content"][:500])
                    print(f"Metadata: {r['metadata']}")
            else:
                print("\n❌ No papers found.")

        elif choice == "3":
            print("\n📚 Papers in memory:")
            list_all_papers()

        elif choice == "4":
            print_citation_tree()

        elif choice == "5":
            parent_id = input("Citing paper ID: ").strip()
            child_id = input("Cited paper ID: ").strip()
            add_citation_edge(parent_id, child_id)
            print(f"✅ Link added: {parent_id} → {child_id}")

        elif choice == "6":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid option.")

if __name__ == "__main__":
    if USE_CLOUD:
        print("☁️  Running in CLOUD mode (Supabase)")
    else:
        print("💻 Running in LOCAL mode (ChromaDB)")
    main()
