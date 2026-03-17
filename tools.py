import arxiv
import pdfplumber
import requests
import io
import time

def search_arxiv(query: str, max_results: int = 5):
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [a.name for a in result.authors[:3]],
            "abstract": result.summary,
            "pdf_url": result.pdf_url,
            "published": str(result.published.date()),
            "arxiv_id": result.entry_id
        })
    return papers

def fetch_pdf_text(pdf_url: str, max_pages: int = 6):
    try:
        response = requests.get(pdf_url, timeout=15)
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            text = ""
            for page in pdf.pages[:max_pages]:
                text += page.extract_text() or ""
        return text[:8000]
    except Exception as e:
        return f"Could not fetch PDF: {e}"

def get_references_semantic_scholar(title: str):
    """
    Given a paper title, fetch its references from Semantic Scholar.
    Returns list of {title, abstract, year, paperId}
    """
    try:
        # Step 1: Find the paper by title
        search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": title,
            "limit": 1,
            "fields": "paperId,title"
        }
        resp = requests.get(search_url, params=params, timeout=10)
        data = resp.json()

        if not data.get("data"):
            return []

        paper_id = data["data"][0]["paperId"]

        # Step 2: Fetch references for that paper
        ref_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
        params = {
            "fields": "title,abstract,year,externalIds",
            "limit": 20
        }
        time.sleep(1)  # polite rate limiting
        resp = requests.get(ref_url, params=params, timeout=10)
        refs = resp.json()

        references = []
        for item in refs.get("data", []):
            cited = item.get("citedPaper", {})
            if cited.get("title") and cited.get("abstract"):
                references.append({
                    "title": cited["title"],
                    "abstract": cited.get("abstract", ""),
                    "year": cited.get("year", "unknown"),
                    "paperId": cited.get("paperId", ""),
                    "arxiv_id": cited.get("externalIds", {}).get("ArXiv", None)
                })
        return references

    except Exception as e:
        print(f"  Semantic Scholar error: {e}")
        return []

def fetch_arxiv_by_id(arxiv_id: str):
    """Fetch a single paper from arxiv by its ID"""
    try:
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        for result in client.results(search):
            return {
                "title": result.title,
                "authors": [a.name for a in result.authors[:3]],
                "abstract": result.summary,
                "pdf_url": result.pdf_url,
                "published": str(result.published.date()),
                "arxiv_id": result.entry_id
            }
    except Exception as e:
        print(f"  Could not fetch arxiv ID {arxiv_id}: {e}")
    return None