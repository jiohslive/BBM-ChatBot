import os
import random
import asyncio
import time
from telegram import Update
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

# 👉 Group ID optional (नसला तरी चालेल)
GROUP_CHAT_ID = None

# ---- Season 6 Contestants (example names - तू बदलू शकतोस) ----
SEASON6_CONTESTANTS = [
    "दीपाली", "विशाल", "राकेश", "तन्वी", "प्रभु",
    "रुचिता", "रोशन", "सागर", "अनुश्री", "सचिन कुमावत"
]

# ---- Replies ----
BB_REPLIES = [
    "आज eviction कोणाचं होईल असं वाटतंय? 😬",
    "Wildcard आला तर गेमच बदलून जाईल 🔥",
    "आजचा task भारी होता रे 😂",
    "पुन्हा भांडण होणार वाटतंय 😅",
    "आजचा एपिसोड फुल ड्रामा 🔥",
]

MEMES = [
    "Bigg Boss घरात शांतता म्हणजे वादळ येण्याआधीची शांतता 😂",
    "आज episode पाहून झोप येणार नाही 🤣",
    "घरात drama नसेल तर मजाच नाही 😎🔥",
    "Nomination आला की सगळे serious होतात 😆",
]

# ---- Simple spam control ----
last_reply_time = {}

def can_reply(chat_id: int, cooldown=5):
    now = time.time()
    last = last_reply_time.get(chat_id, 0)
    if now - last > cooldown:
        last_reply_time[chat_id] = now
        return True
    return False

# ---- Commands ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Bigg Boss Marathi Fan Bot Ready!\n"
        "Eviction, Wildcard, Drama, Memes सगळं बोलेन 😄"
    )

# ---- Reply to all messages ----
async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    if not can_reply(chat_id):
        return

    if "eviction" in text or "eliminate" in text:
        reply = f"या आठवड्यात {random.choice(SEASON6_CONTESTANTS)} ला धोका वाटतोय 😬"
    elif "wildcard" in text:
        reply = "Wildcard आला तर गेमच उलटा होईल 🔥"
    elif "nomination" in text:
        reply = "Nomination लिस्ट बघून धक्का बसलाय 😅"
    elif "meme" in text or "memes" in text:
        reply = random.choice(MEMES)
    else:
        reply = random.choice(BB_REPLIES)

    await update.message.reply_text(reply)

# ---- Poll react ----
async def on_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll = update.poll
    if poll and poll.options:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="या poll वर मत द्या रे 😄 कोण जिंकणार वाटतंय?"
        )

# ---- Jobs ----
async def daily_prediction(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    msg = random.choice([
        "आज मोठं भांडण होणार वाटतंय 🔥",
        "आज कोणीतरी रडणार असं वाटतं 😅",
        "आजचा task खूप मजेशीर असेल 😂",
    ])
    await context.bot.send_message(chat_id=chat_id, text=msg)

async def weekly_elimination_prediction(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    loser = random.choice(SEASON6_CONTESTANTS)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"माझ्या मते या आठवड्यात {loser} eliminate होऊ शकतो 😬"
    )

# ---- Start jobs after /start ----
async def start_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    context.job_queue.run_repeating(daily_prediction, interval=3600, first=60, chat_id=chat_id)
    context.job_queue.run_repeating(weekly_elimination_prediction, interval=604800, first=120, chat_id=chat_id)

    await update.message.reply_text("Auto predictions सुरू केल्या आहेत 🔥")

# ---- Main ----
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", start_jobs))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.add_handler(PollHandler(on_poll))

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
