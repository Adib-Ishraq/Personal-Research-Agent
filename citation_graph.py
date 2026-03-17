import networkx as nx
import json
import os

GRAPH_FILE = "./research_db/citation_graph.json"

def _load_graph():
    if os.path.exists(GRAPH_FILE):
        with open(GRAPH_FILE) as f:
            data = json.load(f)
        G = nx.DiGraph()
        G.add_nodes_from(data["nodes"])
        G.add_edges_from(data["edges"])
        return G
    return nx.DiGraph()

def _save_graph(G):
    os.makedirs("./research_db", exist_ok=True)
    with open(GRAPH_FILE, "w") as f:
        json.dump({
            "nodes": list(G.nodes(data=True)),
            "edges": list(G.edges())
        }, f, indent=2)

def add_paper_node(paper_id: str, title: str):
    G = _load_graph()
    G.add_node(paper_id, title=title)
    _save_graph(G)

def add_citation_edge(parent_id: str, child_id: str):
    """parent paper cites child paper"""
    G = _load_graph()
    G.add_edge(parent_id, child_id)
    _save_graph(G)

def get_citation_depth(paper_id: str) -> int:
    """How many hops from a root paper is this paper?"""
    G = _load_graph()
    roots = [n for n in G.nodes if G.in_degree(n) == 0]
    min_depth = float("inf")
    for root in roots:
        try:
            depth = nx.shortest_path_length(G, root, paper_id)
            min_depth = min(min_depth, depth)
        except nx.NetworkXNoPath:
            continue
    return min_depth if min_depth != float("inf") else 0

def print_citation_tree():
    G = _load_graph()
    if G.number_of_nodes() == 0:
        print("Citation graph is empty.")
        return

    print(f"\n📊 Citation Graph: {G.number_of_nodes()} papers, {G.number_of_edges()} links\n")
    roots = [n for n in G.nodes if G.in_degree(n) == 0]

    def print_tree(node, depth=0):
        title = G.nodes[node].get("title", node)[:55]
        prefix = "  " * depth + ("└─ " if depth > 0 else "")
        print(f"{prefix}{title}")
        for child in G.successors(node):
            print_tree(child, depth + 1)

    for root in roots:
        print_tree(root)