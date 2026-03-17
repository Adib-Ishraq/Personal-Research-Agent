import schedule
import time
import json
from agent import process_paper
from tools import search_arxiv
from memory import paper_exists
from notifier import notify_new_papers, notify_daily_summary, send_notification
from dotenv import load_dotenv

load_dotenv()

def load_topics():
    with open("topics.json") as f:
        return json.load(f)["topics"]

def run_daily_update():
    print("\n🔄 Running scheduled update...\n")
    send_notification("🔄 *Daily update started...*")

    topics = load_topics()
    total_new = 0

    for topic in topics:
        print(f"\n📡 Checking: {topic}")
        papers = search_arxiv(topic, max_results=5)

        new_papers = []
        for paper in papers:
            if not paper_exists(paper["arxiv_id"]):
                new_papers.append(paper)
                process_paper(paper, depth=1, parent_id=None)  # depth=1 for scheduled runs
                total_new += 1

        notify_new_papers(topic, new_papers)

        if not new_papers:
            print(f"  No new papers for: {topic}")

    notify_daily_summary(total_new, len(topics))
    print(f"\n✅ Update complete. {total_new} new papers added.")

def run_scheduler():
    print("🚀 Research Agent Scheduler started")
    print("   Runs daily at 08:00")
    print("   Press Ctrl+C to stop\n")

    # Run once immediately on start
    run_daily_update()

    # Then schedule daily
    schedule.every().day.at("08:00").do(run_daily_update)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()