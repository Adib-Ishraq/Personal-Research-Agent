from groq import Groq
from memory import search_memory
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a research assistant with access to a collection of academic papers 
on LLMs in healthcare. You help researchers understand, compare, and synthesize findings 
across papers. Be analytical, honest about gaps, and cite specific papers when making claims.
If you don't know something or it's not in the provided papers, say so clearly."""

def chat_with_papers():
    """
    Multi-turn conversational interface over the paper memory.
    """
    print("\n💬 Chat with your paper collection")
    print("   Type 'exit' to return to main menu")
    print("   Type 'clear' to reset conversation history")
    print("-" * 50)

    conversation_history = []

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Returning to main menu...")
            break
        if user_input.lower() == "clear":
            conversation_history = []
            print("🔄 Conversation history cleared.")
            continue

        # Semantic search over memory to get relevant papers
        relevant_papers = search_memory(user_input, n_results=4)

        if relevant_papers:
            context = "\n\n---\n\n".join([
                f"[Paper {i+1}] {p['content'][:600]}"
                for i, p in enumerate(relevant_papers)
            ])
            context_msg = f"""Relevant papers from your collection:

{context}

---
Use these papers to answer the question. If they are not relevant, say so."""
        else:
            context_msg = "No papers found in memory relevant to this query. Let the user know they should fetch papers first."

        # Build messages: system + context injection + history + new user message
        messages = [
            {
                "role": "user",
                "content": context_msg
            },
            {
                "role": "assistant",
                "content": "Understood. I have the paper context. What would you like to know?"
            }
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current question
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=900
        )

        assistant_reply = response.choices[0].message.content

        # Save to history for multi-turn context
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": assistant_reply})

        # Keep history from growing too long (last 10 turns)
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]

        print(f"\n🤖 Agent: {assistant_reply}")