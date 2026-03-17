# 🤖 Telegram Bot Guide

Your Research Agent now has a **full-featured Telegram bot** with an interactive menu!

---

## **Start the Bot**

```powershell
python telegram_bot.py
```

Then in Telegram:
1. Find your bot (search for the name you gave it in @BotFather)
2. Send `/start`
3. You get a menu with all options!

---

## **Features in Telegram**

### **🔍 Search & Fetch**
- **Search ArXiv** → Find new papers and process them
- **Search Papers** → Search your collection
- **List Papers** → See all papers you have

### **📚 Manage Papers**
- **Delete Paper** → Remove one paper by ID
- **Clear ALL Papers** → Delete entire collection

### **🎯 Manage Topics**
- **View Topics** → See current search topics
- **Add Topic** → Add new research interest
- **Remove Topic** → Remove a topic
- **Clear Topics** → Reset all topics

### **🔗 Citation Management**
- **Add Citation** → Link papers together
- **Citation Graph** → View relationships

---

## **Daily Updates in Telegram**

Every day at 08:00 UTC, you get:

```
✅ Cloud Update Complete

Topics checked: 5
New papers added: 12

Your research collection is now up to date.
```

---

## **How to Use**

### **Example: Search ArXiv**
```
You: /start
Bot: Shows menu
You: Click "🔍 Search ArXiv"
You: Type "LLM healthcare"
Bot: Searches, downloads, summarizes papers
Bot: "✅ Done! 5 papers saved"
```

### **Example: Search Your Papers**
```
You: Click "📚 Search Papers"
You: Type "neural networks"
Bot: Shows matching papers (first 200 chars)
```

### **Example: Add Topic**
```
You: Click "🎯 Manage Topics"
You: Click "➕ Add Topic"
You: Type "machine learning drug discovery"
Bot: "✅ Added!"
```

---

## **Run Mode**

You can run the bot in two ways:

### **Option 1: Manual (Interactive)**
```powershell
python telegram_bot.py
```
Bot runs and responds to your messages in real-time.

### **Option 2: Background (Run 24/7)**
```powershell
# In PowerShell (run in background)
Start-Process python "telegram_bot.py" -WindowStyle Hidden
```

---

## **Keyboard Shortcuts**

| Button | Action |
|--------|--------|
| 🔍 Search ArXiv | Search and fetch papers |
| 📚 Search Papers | Search existing collection |
| 📋 List Papers | Show all papers |
| 🌳 Citation Graph | View paper relationships |
| 📝 Manage Papers | Delete papers |
| 🎯 Manage Topics | Add/remove topics |
| « Back | Return to main menu |

---

## **Requirements**

- .env file with `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- `python-telegram-bot` installed (done automatically)

---

## **Troubleshooting**

| Issue | Solution |
|-------|----------|
| "Bot not responding" | Check BOT_TOKEN in .env |
| "No menu appears" | Send `/start` command |
| "Search takes long" | Large searches take 1-2 min (normal) |
| "Error on delete" | Make sure arxiv_id is correct |

---

**Enjoy your interactive research agent in Telegram!** 🚀
