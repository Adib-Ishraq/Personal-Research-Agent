from agent import run_agent
from memory import search_memory, list_all_papers
from citation_graph import add_citation_edge, print_citation_tree

def main():
    while True:
        print("\n" + "="*60)
        print("🧠 Research Agent — Phase 4")
        print("="*60)
        print("  1 — Fetch + chase citations on a topic")
        print("  2 — Search papers in memory")
        print("  3 — List all papers in memory")
        print("  4 — View citation tree")
        print("  5 — Add citation link manually")
        print("  6 — Exit")

        choice = input("\nChoose (1-6): ").strip()

        if choice == "1":
            query = input("Research topic: ").strip()
            run_agent(query)

        elif choice == "2":
            query = input("Search query: ").strip()
            results = search_memory(query, n_results=3)
            if results:
                print(f"\nFound {len(results)} relevant papers:\n")
                for i, r in enumerate(results, 1):
                    print(f"{'='*50}")
                    print(f"Result {i}:")
                    print(r["content"][:500])
                    print(f"Metadata: {r['metadata']}")
            else:
                print("\n❌ No papers found. Try fetching papers first.")

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
    main()






