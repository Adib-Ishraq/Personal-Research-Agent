"""Cloud storage using Supabase for paper memory and embeddings."""
import os
from dotenv import load_dotenv
import json
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def paper_exists(arxiv_id: str) -> bool:
    """Check if paper is in cloud memory."""
    try:
        response = supabase.table("papers").select("*").eq("arxiv_id", arxiv_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"  Database error: {e}")
        return False

def save_paper(arxiv_id: str, title: str, summary: str, metadata: dict):
    """Save paper to Supabase."""
    try:
        data = {
            "arxiv_id": arxiv_id,
            "title": title,
            "summary": summary,
            "metadata": json.dumps(metadata),
            "created_at": "now()"
        }
        supabase.table("papers").upsert(data).execute()
        print(f"  💾 Saved to cloud: {title[:50]}...")
    except Exception as e:
        print(f"  Database error: {e}")

def search_memory(query: str, n_results: int = 3):
    """Search papers in cloud using full-text search."""
    try:
        # Supabase full-text search on title + summary
        response = supabase.rpc(
            "search_papers",
            {"search_query": query, "result_limit": n_results}
        ).execute()
        
        papers = []
        for row in response.data:
            papers.append({
                "content": f"{row['title']}\n\n{row['summary']}",
                "metadata": json.loads(row.get("metadata", "{}"))
            })
        return papers
    except Exception as e:
        print(f"  Search error: {e}")
        return []

def list_all_papers():
    """List all papers from cloud."""
    try:
        response = supabase.table("papers").select("arxiv_id, title, metadata").execute()
        
        if not response.data:
            print("No papers in memory yet.")
            return
        
        for i, paper in enumerate(response.data, 1):
            meta = json.loads(paper.get("metadata", "{}"))
            print(f"  [{i}] {paper['title'][:60]} ({meta.get('published', '')})")
    except Exception as e:
        print(f"  Database error: {e}")
