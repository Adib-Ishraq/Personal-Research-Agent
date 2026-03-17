import chromadb
from chromadb.utils import embedding_functions

# Uses a local folder called "research_db" - no server needed
client = chromadb.PersistentClient(path="./research_db")

# Free local embeddings using sentence-transformers
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # small, fast, downloads once
)

collection = client.get_or_create_collection(
    name="papers",
    embedding_function=embedding_fn
)

def paper_exists(arxiv_id: str) -> bool:
    """Check if we've already stored this paper"""
    results = collection.get(ids=[arxiv_id])
    return len(results["ids"]) > 0

def save_paper(arxiv_id: str, title: str, summary: str, metadata: dict):
    """Save a paper summary into memory"""
    collection.add(
        ids=[arxiv_id],
        documents=[f"{title}\n\n{summary}"],
        metadatas=[metadata]
    )
    print(f"  💾 Saved to memory: {title[:50]}...")

def search_memory(query: str, n_results: int = 3):
    """Semantic search over all stored papers"""
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count())
    )
    if not results["ids"][0]:
        return []
    
    papers = []
    for i, doc in enumerate(results["documents"][0]):
        papers.append({
            "content": doc,
            "metadata": results["metadatas"][0][i]
        })
    return papers

def list_all_papers():
    """List all papers in memory"""
    results = collection.get()
    if not results["ids"]:
        print("No papers in memory yet.")
        return
    for i, meta in enumerate(results["metadatas"]):
        print(f"  [{i+1}] {meta.get('title', 'Unknown')[:60]} ({meta.get('published', '')})")

def delete_paper(arxiv_id: str):
    """Delete a paper by its arxiv_id"""
    try:
        collection.delete(ids=[arxiv_id])
        print(f"✅ Deleted: {arxiv_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting paper: {e}")
        return False

def delete_all_papers():
    """Clear all papers from memory"""
    try:
        results = collection.get()
        if results["ids"]:
            collection.delete(ids=results["ids"])
            print(f"✅ Deleted all {len(results['ids'])} papers!")
            return True
        else:
            print("No papers to delete.")
            return False
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False