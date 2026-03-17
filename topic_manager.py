"""Manage research topics dynamically."""
import json
import os

TOPICS_FILE = "topics.json"

def load_topics():
    """Load topics from file."""
    try:
        with open(TOPICS_FILE) as f:
            return json.load(f).get("topics", [])
    except FileNotFoundError:
        return []

def save_topics(topics):
    """Save topics to file."""
    with open(TOPICS_FILE, "w") as f:
        json.dump({"topics": topics}, f, indent=2)
    print("✅ Topics saved!")

def view_topics():
    """Display all current topics."""
    topics = load_topics()
    if not topics:
        print("No topics found.")
        return
    
    print("\n📋 Current Research Topics:")
    for i, topic in enumerate(topics, 1):
        print(f"  [{i}] {topic}")

def add_topic():
    """Add a new topic."""
    topic = input("Enter new topic: ").strip()
    if not topic:
        print("❌ Topic cannot be empty.")
        return
    
    topics = load_topics()
    if topic in topics:
        print("❌ Topic already exists.")
        return
    
    topics.append(topic)
    save_topics(topics)
    print(f"✅ Added: {topic}")

def remove_topic():
    """Remove a topic by number."""
    topics = load_topics()
    if not topics:
        print("No topics to remove.")
        return
    
    view_topics()
    try:
        idx = int(input("\nEnter topic number to remove: ")) - 1
        if 0 <= idx < len(topics):
            removed = topics.pop(idx)
            save_topics(topics)
            print(f"✅ Removed: {removed}")
        else:
            print("❌ Invalid number.")
    except ValueError:
        print("❌ Please enter a valid number.")

def clear_topics():
    """Clear all topics."""
    confirm = input("⚠️  Delete ALL topics? (yes/no): ").strip().lower()
    if confirm == "yes":
        save_topics([])
        print("✅ All topics cleared!")
    else:
        print("Cancelled.")
