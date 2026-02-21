import os
import random
import asyncio
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

GROUP_CHAT_ID = None

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GROUP_CHAT_ID
    GROUP_CHAT_ID = update.effective_chat.id

    await update.message.reply_text(
        "मी Bigg Boss Marathi Fan आहे 🔥\n"
        "Eviction, Wildcard, Drama सगळ्यावर गप्पा मारूया 😄"
    )

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

async def on_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll = update.poll
    await context.bot.send_message(
        chat_id=poll.chat.id,
        text="या poll वर मत द्या रे 😄 कोण जिंकणार वाटतंय?"
    )

async def daily_prediction(context: ContextTypes.DEFAULT_TYPE):
    predictions = [
        "आज मोठं भांडण होणार वाटतंय 🔥",
        "आज कोणीतरी रडणार असं वाटतं 😅",
        "आजचा task खूप मजेशीर असेल 😂",
        "आज eviction मध्ये धक्का बसणार 😬",
    ]
    await context.bot.send_message(context.job.chat_id, random.choice(predictions))

async def episode_recap(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        context.job.chat_id,
        "कालचा एपिसोड फुल ड्रामा होता 🔥 तुमचं काय मत आहे?"
    )

async def mvp_question(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        context.job.chat_id,
        "आजचा MVP कोण? 👑 नाव सांगा!"
    )

async def weekly_elimination_prediction(context: ContextTypes.DEFAULT_TYPE):
    guesses = [
        "या आठवड्यात बाहेर जाणार असं वाटतंय अमुक-तमुक 😬",
        "Voting trend बघता ह्यावेळी धक्का बसेल 🔥",
        "Strong contestant पण danger zone मध्ये आहे वाटतं 😅",
    ]
    await context.bot.send_message(context.job.chat_id, random.choice(guesses))

async def start_jobs(context: ContextTypes.DEFAULT_TYPE):
    if GROUP_CHAT_ID:
        context.job_queue.run_repeating(daily_prediction, interval=3600, first=30, chat_id=GROUP_CHAT_ID)
        context.job_queue.run_repeating(episode_recap, interval=7200, first=60, chat_id=GROUP_CHAT_ID)
        context.job_queue.run_repeating(mvp_question, interval=10800, first=90, chat_id=GROUP_CHAT_ID)
        context.job_queue.run_repeating(weekly_elimination_prediction, interval=604800, first=120, chat_id=GROUP_CHAT_ID)

async def main():
    app = ApplicationBuilder().token(TOKEN).job_queue(True).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.add_handler(PollHandler(on_poll))

    app.job_queue.run_once(start_jobs, 15)

    print("🤖 Bigg Boss Marathi Bot Started...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
