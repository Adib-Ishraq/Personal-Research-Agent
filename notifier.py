import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_notification(message: str):
    """Send a message to your Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️  Telegram not configured. Skipping notification.")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Notification failed: {e}")

def notify_new_papers(topic: str, new_papers: list):
    if not new_papers:
        return
    lines = [f"📚 *New papers found for:* `{topic}`\n"]
    for p in new_papers:
        lines.append(f"• *{p['title'][:60]}*")
        lines.append(f"  {p['published']} | {p['url']}\n")
    send_notification("\n".join(lines))

def notify_daily_summary(total_new: int, topics_checked: int):
    msg = (
        f"🤖 *Daily Research Agent Update*\n\n"
        f"Topics checked: {topics_checked}\n"
        f"New papers added: {total_new}\n\n"
        f"Open your agent to chat with new findings."
    )
    send_notification(msg)