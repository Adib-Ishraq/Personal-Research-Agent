"""Citation graph stored in Supabase."""
import os
from dotenv import load_dotenv
import json
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_paper_node(paper_id: str, title: str):
    """Add or update paper node in citation graph."""
    try:
        supabase.table("citation_graph").upsert({
            "paper_id": paper_id,
            "title": title,
            "type": "node"
        }).execute()
    except Exception as e:
        print(f"  Graph error: {e}")

def add_citation_edge(parent_id: str, child_id: str):
    """Add citation edge (parent cites child)."""
    try:
        supabase.table("citation_graph").insert({
            "parent_id": parent_id,
            "child_id": child_id,
            "type": "edge"
        }).execute()
    except Exception as e:
        print(f"  Graph error: {e}")

def print_citation_tree():
    """Display citation tree from cloud."""
    try:
        # Get all nodes
        nodes_response = supabase.table("citation_graph").select("*").eq("type", "node").execute()
        nodes = {n["paper_id"]: n["title"] for n in nodes_response.data}
        
        # Get all edges
        edges_response = supabase.table("citation_graph").select("*").eq("type", "edge").execute()
        edges = [(e["parent_id"], e["child_id"]) for e in edges_response.data]
        
        # Build graph
        children = {}
        for parent, child in edges:
            if parent not in children:
                children[parent] = []
            children[parent].append(child)
        
        # Find roots (papers with no incoming edges)
        parents = set(p for p, c in edges)
        roots = [n for n in nodes.keys() if n not in parents]
        
        print(f"\n📊 Citation Graph: {len(nodes)} papers, {len(edges)} links\n")
        
        def print_tree(node_id, depth=0):
            title = nodes.get(node_id, node_id)[:55]
            prefix = "  " * depth + ("└─ " if depth > 0 else "")
            print(f"{prefix}{title}")
            for child in children.get(node_id, []):
                print_tree(child, depth + 1)
        
        for root in roots:
            print_tree(root)
    
    except Exception as e:
        print(f"  Graph error: {e}")

def get_citation_depth(paper_id: str) -> int:
    """Calculate depth from root papers."""
    try:
        edges_response = supabase.table("citation_graph").select("*").eq("type", "edge").execute()
        edges = [(e["parent_id"], e["child_id"]) for e in edges_response.data]
        
        parents = set(p for p, c in edges)
        roots = [n for p, n in edges if p not in parents]
        
        # Simple BFS to find shortest path
        from collections import deque
        for root in roots:
            queue = deque([(root, 0)])
            visited = set()
            while queue:
                node, dist = queue.popleft()
                if node == paper_id:
                    return dist
                if node not in visited:
                    visited.add(node)
                    for parent, child in edges:
                        if parent == node:
                            queue.append((child, dist + 1))
        return 0
    except Exception as e:
        print(f"  Graph error: {e}")
        return 0
