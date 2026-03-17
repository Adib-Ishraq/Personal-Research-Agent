"""Telegram bot for interactive research agent."""
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from memory import list_all_papers, search_memory, delete_paper, delete_all_papers
from topic_manager import view_topics, add_topic, remove_topic, load_topics
from citation_graph import print_citation_tree
from agent import run_agent
import json

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))

# Store state for multi-step interactions
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show main menu."""
    keyboard = [
        [InlineKeyboardButton("🔍 Search ArXiv", callback_data="search_arxiv")],
        [InlineKeyboardButton("📚 Search Papers", callback_data="search_papers"),
         InlineKeyboardButton("📋 List Papers", callback_data="list_papers")],
        [InlineKeyboardButton("🌳 Citation Graph", callback_data="view_graph"),
         InlineKeyboardButton("🔗 Add Citation", callback_data="add_citation")],
        [InlineKeyboardButton("📝 Manage Papers", callback_data="manage_papers")],
        [InlineKeyboardButton("🎯 Manage Topics", callback_data="manage_topics")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🧠 *Research Agent Menu*\n\n"
        "Choose an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "search_arxiv":
        user_state[query.from_user.id] = "search_arxiv"
        await query.edit_message_text(
            "📡 Enter search topic:\n(e.g., 'LLM healthcare')",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
        )
    
    elif query.data == "search_papers":
        user_state[query.from_user.id] = "search_papers"
        await query.edit_message_text(
            "🔍 Enter search query:\n(e.g., 'neural networks')",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
        )
    
    elif query.data == "list_papers":
        # Capture stdout to get list output
        import io
        import sys
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            from memory import list_all_papers as list_papers_func
            list_papers_func()
        
        output = f.getvalue() or "No papers in memory yet."
        
        # Format nicely
        message = "📚 *Papers in Memory*\n\n" + output
        await query.edit_message_text(
            message[:4000],  # Telegram limit
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]]),
            parse_mode="Markdown"
        )
    
    elif query.data == "view_graph":
        await query.edit_message_text(
            "🌳 Citation graph visualization coming soon!\n"
            "Currently available in main.py",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
        )
    
    elif query.data == "add_citation":
        user_state[query.from_user.id] = "add_citation_parent"
        await query.edit_message_text(
            "🔗 Enter PARENT paper ID:\n(the paper that cites)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
        )
    
    elif query.data == "manage_papers":
        keyboard = [
            [InlineKeyboardButton("🗑️ Delete Paper", callback_data="delete_one_paper")],
            [InlineKeyboardButton("🗑️ Clear ALL Papers", callback_data="delete_all_papers")],
            [InlineKeyboardButton("« Back", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "📝 *Paper Management*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    elif query.data == "delete_one_paper":
        user_state[query.from_user.id] = "delete_paper"
        await query.edit_message_text(
            "🗑️ Enter arxiv ID to delete:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
        )
    
    elif query.data == "delete_all_papers":
        keyboard = [
            [InlineKeyboardButton("✅ Yes, delete all", callback_data="confirm_delete_all"),
             InlineKeyboardButton("❌ Cancel", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "⚠️ Are you sure? This cannot be undone!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == "confirm_delete_all":
        delete_all_papers()
        await query.edit_message_text(
            "✅ All papers deleted!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
        )
    
    elif query.data == "manage_topics":
        keyboard = [
            [InlineKeyboardButton("👁️ View Topics", callback_data="view_topics_list")],
            [InlineKeyboardButton("➕ Add Topic", callback_data="add_topic_btn")],
            [InlineKeyboardButton("➖ Remove Topic", callback_data="remove_topic_btn")],
            [InlineKeyboardButton("🗑️ Clear Topics", callback_data="clear_topics_btn")],
            [InlineKeyboardButton("« Back", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "🎯 *Topic Management*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    elif query.data == "view_topics_list":
        topics = load_topics()
        if topics:
            topic_list = "\n".join([f"  {i}. {t}" for i, t in enumerate(topics, 1)])
            message = f"🎯 *Current Topics*:\n\n{topic_list}"
        else:
            message = "No topics configured yet."
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="manage_topics")]]),
            parse_mode="Markdown"
        )
    
    elif query.data == "add_topic_btn":
        user_state[query.from_user.id] = "add_topic"
        await query.edit_message_text(
            "➕ Enter new topic:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
        )
    
    elif query.data == "remove_topic_btn":
        topics = load_topics()
        if not topics:
            await query.edit_message_text(
                "No topics to remove.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
            )
        else:
            user_state[query.from_user.id] = "remove_topic"
            topic_list = "\n".join([f"  {i}. {t}" for i, t in enumerate(topics, 1)])
            await query.edit_message_text(
                f"➖ *Topics*:\n\n{topic_list}\n\nEnter number to remove:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]]),
                parse_mode="Markdown"
            )
    
    elif query.data == "clear_topics_btn":
        keyboard = [
            [InlineKeyboardButton("✅ Yes, clear all", callback_data="confirm_clear_topics"),
             InlineKeyboardButton("❌ Cancel", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "⚠️ Clear all topics?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == "confirm_clear_topics":
        from topic_manager import clear_topics
        clear_topics()
        await query.edit_message_text(
            "✅ Topics cleared!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_menu")]])
        )
    
    elif query.data == "back_menu":
        await start(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input based on user state."""
    user_id = update.message.from_user.id
    text = update.message.text
    state = user_state.get(user_id)
    
    if state == "search_arxiv":
        try:
            await update.message.reply_text(f"🔍 Searching for: {text}\n\nProcessing... (may take 1-2 min)")
            run_agent(text)
            await update.message.reply_text("✅ Done! Papers saved to memory.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        user_state[user_id] = None
    
    elif state == "search_papers":
        try:
            results = search_memory(text, n_results=3)
            if results:
                message = f"🔍 Found {len(results)} papers:\n\n"
                for i, r in enumerate(results, 1):
                    preview = r["content"][:200].replace("\n", " ")
                    message += f"*{i}. {r['metadata'].get('title', 'Unknown')[:50]}*\n{preview}...\n\n"
                await update.message.reply_text(message[:4000], parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ No papers found.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        user_state[user_id] = None
    
    elif state == "delete_paper":
        try:
            delete_paper(text)
            await update.message.reply_text("✅ Paper deleted!")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        user_state[user_id] = None
    
    elif state == "add_topic":
        try:
            topics = load_topics()
            if text not in topics:
                topics.append(text)
                from topic_manager import save_topics
                save_topics(topics)
                await update.message.reply_text(f"✅ Added: {text}")
            else:
                await update.message.reply_text("❌ Topic already exists.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        user_state[user_id] = None
    
    elif state == "remove_topic":
        try:
            idx = int(text) - 1
            topics = load_topics()
            if 0 <= idx < len(topics):
                removed = topics.pop(idx)
                from topic_manager import save_topics
                save_topics(topics)
                await update.message.reply_text(f"✅ Removed: {removed}")
            else:
                await update.message.reply_text("❌ Invalid number.")
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number.")
        user_state[user_id] = None
    
    elif state == "add_citation_parent":
        user_state[user_id] = {"add_citation": text}
        await update.message.reply_text("Enter CHILD paper ID:\n(the paper being cited)")
    
    elif isinstance(state, dict) and "add_citation" in state:
        try:
            from citation_graph import add_citation_edge
            parent = state["add_citation"]
            add_citation_edge(parent, text)
            await update.message.reply_text(f"✅ Citation added: {parent} → {text}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        user_state[user_id] = None

async def daily_update(context: ContextTypes.DEFAULT_TYPE):
    """Send daily summary (called by scheduler)."""
    # Note: This is called by scheduler_cloud.py
    pass

def telegram_bot():
    """Start the Telegram bot."""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 Telegram bot started! Send /start to begin.")
    app.run_polling()

if __name__ == "__main__":
    telegram_bot()
