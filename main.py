import os
import random
import asyncio
from telegram import Update, Poll
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    PollHandler,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN Railway Variables मध्ये add केलेला नाही!")

# ---- Personality ----
SYSTEM_PROMPT = """
You are a friendly Bigg Boss Marathi fan.
You talk like a real Marathi person in Marathi + Hinglish.
You discuss Bigg Boss Marathi topics:
eviction, wildcard entry, nominations, captaincy task, fights, gossip, predictions.
Be casual, funny, use emojis sometimes.
Never use technical language.
Never say you are an AI/bot.
"""

# ---- Fallback replies ----
BB_REPLIES = [
    "आजचं eviction कोणाचं होईल असं वाटतंय? 😬",
    "Wildcard entry येणार म्हणे, मजा येईल आता 🔥",
    "ह्या आठवड्याचा task एकदम झकास होता 😂",
    "त्या दोन जणांमध्ये पुन्हा भांडण होणार वाटतंय 😅",
    "कॅप्टनसी टास्क कोणी जिंकेल रे?",
    "आजचा एपिसोड फुल ड्रामा आहे 🔥",
]

def get_fallback_reply():
    return random.choice(BB_REPLIES)

# ---- Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "मी Big Boss Marathi Fan आहे 🤖🔥\nEviction, Wildcard, Drama सगळ्यावर गप्पा मारूया 😄"
    )

# 1️⃣ Reply to all messages
async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.lower()

    if "eviction" in text:
        reply = "Eviction खूपच shocking वाटतंय यावेळी 😬 कोण जाईल वाटतं?"
    elif "wildcard" in text:
        reply = "Wildcard आला तर गेमच बदलून जाईल 🔥"
    elif "nomination" in text:
        reply = "Nomination लिस्ट बघून धक्का बसलाय 😅"
    else:
        reply = get_fallback_reply()

    await update.message.reply_text(reply)

# 2️⃣ Poll वर comment
async def on_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll = update.poll
    await context.bot.send_message(
        chat_id=poll.chat.id,
        text="या poll वर मत द्या रे 😄 कोण जिंकणार वाटतंय?"
    )

# 3️⃣ Daily prediction
async def daily_prediction(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    predictions = [
        "आज मोठं भांडण होणार वाटतंय 🔥",
        "आज कोणीतरी रडणार असं वाटतं 😅",
        "आजचा task खूप मजेशीर असेल 😂",
        "आज eviction मध्ये धक्का बसणार 😬",
    ]
    await context.bot.send_message(chat_id=chat_id, text=random.choice(predictions))

# 4️⃣ Episode recap
async def episode_recap(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text="कालचा एपिसोड फुल ड्रामा होता 🔥 तुमचं काय मत आहे?"
    )

# 5️⃣ MVP Question
async def mvp_question(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text="आजचा MVP कोण? 👑 नाव सांगा!"
    )

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.add_handler(PollHandler(on_poll))

    # Scheduled jobs (group मध्ये bot add केल्यावर /start केलास की चालतील)
    app.job_queue.run_repeating(daily_prediction, interval=3600, first=30, chat_id=None)
    app.job_queue.run_repeating(episode_recap, interval=7200, first=60, chat_id=None)
    app.job_queue.run_repeating(mvp_question, interval=10800, first=90, chat_id=None)

    print("🤖 Big Boss Marathi Bot Started...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
