"""Cloud-based scheduler using Supabase — runs on GitHub Actions."""
import json
import os
from dotenv import load_dotenv
from agent import process_paper
from tools import search_arxiv
from supabase_db import paper_exists
from notifier import send_notification

load_dotenv()

def load_topics():
    """Load research topics from config file."""
    try:
        with open("topics.json") as f:
            return json.load(f)["topics"]
    except FileNotFoundError:
        print("topics.json not found. Using default topics.")
        return [
            "LLMs healthcare foundation model",
            "large language models clinical decision support"
        ]

def run_daily_update():
    """Run scheduled update and save new papers to cloud."""
    print("\n🔄 Running scheduled cloud update...\n")
    send_notification("🔄 *Cloud update started...*")
    
    topics = load_topics()
    total_new = 0
    
    for topic in topics:
        print(f"\n📡 Checking: {topic}")
        try:
            papers = search_arxiv(topic, max_results=5)
            
            new_papers = []
            for paper in papers:
                if not paper_exists(paper["arxiv_id"]):
                    new_papers.append(paper)
                    process_paper(paper, depth=1, parent_id=None)
                    total_new += 1
            
            if new_papers:
                print(f"  ✅ Found {len(new_papers)} new papers")
            else:
                print(f"  ℹ️  No new papers for: {topic}")
        
        except Exception as e:
            print(f"  ❌ Error checking {topic}: {e}")
            send_notification(f"⚠️ Error checking topic: {topic}\n{str(e)}")
    
    # Send summary
    summary_msg = (
        f"✅ *Cloud Update Complete*\n\n"
        f"Topics checked: {len(topics)}\n"
        f"New papers added: {total_new}\n\n"
        f"Your research collection is now up to date."
    )
    send_notification(summary_msg)
    print(f"\n✅ Update complete. {total_new} new papers added.")

if __name__ == "__main__":
    run_daily_update()
