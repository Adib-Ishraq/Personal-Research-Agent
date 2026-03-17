import os
from dotenv import load_dotenv
from groq import Groq
from tools import search_arxiv, fetch_pdf_text, get_references_semantic_scholar, fetch_arxiv_by_id
from memory import paper_exists, save_paper, search_memory
from citation_graph import add_paper_node, add_citation_edge

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_DEPTH = 2
MAX_REFS_PER_PAPER = 3

def summarize_paper(title, abstract, pdf_text):
    prompt = f"""You are a research assistant. Summarize this paper concisely.

Title: {title}
Abstract: {abstract}
Paper content (first few pages):
{pdf_text}

Provide:
1. Core problem being solved
2. Key methodology
3. Main findings/results
4. Relevance to LLMs in healthcare research
5. One critical limitation or gap
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )
    return response.choices[0].message.content

def pick_important_references(parent_title: str, references: list) -> list:
    """Ask the LLM which references are worth chasing"""
    if not references:
        return []

    ref_list = "\n".join([
        f"{i+1}. {r['title']} ({r['year']}) — {r['abstract'][:150]}..."
        for i, r in enumerate(references[:15])
    ])

    prompt = f"""You are a research assistant helping with LLMs in healthcare research.

The paper "{parent_title}" cites these references:
{ref_list}

Which 3 references are MOST important to read for understanding LLMs in healthcare?
Reply with ONLY the numbers, comma-separated. Example: 2, 5, 9
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=30
    )
    raw = response.choices[0].message.content.strip()

    try:
        indices = [int(x.strip()) - 1 for x in raw.split(",") if x.strip().isdigit()]
        return [references[i] for i in indices if i < len(references)][:MAX_REFS_PER_PAPER]
    except Exception:
        return references[:MAX_REFS_PER_PAPER]

def process_paper(paper: dict, depth: int = 0, parent_id: str = None):
    """Recursively process a paper and chase citations up to MAX_DEPTH."""
    arxiv_id = paper.get("arxiv_id", paper.get("title", "unknown"))
    title = paper["title"]
    indent = "  " * depth

    add_paper_node(arxiv_id, title)
    if parent_id:
        add_citation_edge(parent_id, arxiv_id)

    if paper_exists(arxiv_id):
        print(f"{indent}⏭  Already in memory: {title[:55]}...")
        return

    print(f"{indent}📄 Reading (depth={depth}): {title[:55]}...")

    pdf_url = paper.get("pdf_url")
    pdf_text = fetch_pdf_text(pdf_url) if pdf_url else "No PDF available."
    summary = summarize_paper(title, paper.get("abstract", ""), pdf_text)

    save_paper(
        arxiv_id=arxiv_id,
        title=title,
        summary=summary,
        metadata={
            "title": title,                                  # fixed: was missing
            "authors": ", ".join(paper.get("authors", [])),
            "published": paper.get("published", "unknown"),
            "url": arxiv_id,
            "depth": str(depth)
        }
    )

    if depth >= MAX_DEPTH:
        return

    references = get_references_semantic_scholar(title)
    important = pick_important_references(title, references)

    for i, ref in enumerate(important):
        ref_id = ref.get("arxiv_id") or ref.get("paperId", f"ref_{i}")
        if ref_id and not paper_exists(ref_id):
            print(f"{indent}  ↑ Chasing reference: {ref['title'][:45]}...")
            full_paper = fetch_arxiv_by_id(ref_id) if ref.get("arxiv_id") else None
            if full_paper:
                process_paper(full_paper, depth=depth+1, parent_id=arxiv_id)
            else:
                add_paper_node(ref_id, ref["title"])
                add_citation_edge(arxiv_id, ref_id)

def run_agent(research_query: str):
    """Main entry point: search for papers and chase citations."""
    print(f"\n🔍 Searching for: {research_query}\n")
    
    papers = search_arxiv(research_query, max_results=5)
    print(f"Found {len(papers)} papers\n")
    
    for i, paper in enumerate(papers):
        print(f"\n[{i+1}/{len(papers)}]")
        process_paper(paper, depth=0, parent_id=None)