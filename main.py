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

GROUP_CHAT_ID = None
LAST_REPLY_TIME = {}

# ---- Replies ----
BB_REPLIES = [
    "आजचं eviction कोणाचं होईल असं वाटतंय? 😬",
    "Wildcard entry आला तर गेमच बदलून जाईल 🔥",
    "आजचा episode full drama वाटतोय 😂",
    "Nomination लिस्ट बघून धक्का बसलाय 😅",
    "Captaincy task कोण जिंकणार असं वाटतंय?",
    "त्या दोघांमध्ये पुन्हा भांडण होणार वाटतंय 😆",
]

MEMES = [
    "Bigg Boss घरात शांतता = वादळ येण्याआधीची शांतता 😂",
    "Nomination आला की सगळे suddenly innocent होतात 😇",
    "Task हरला की reason: 'माझा mood नव्हता' 😆",
    "Wildcard आला की जुने contestant: 😐🔥",
    "Eviction च्या दिवशी सगळे emotional mode मध्ये 😭",
]

# ---- Utils ----
def cooldown_ok(chat_id, seconds=10):
    now = time.time()
    last = LAST_REPLY_TIME.get(chat_id, 0)
    if now - last < seconds:
        return False
    LAST_REPLY_TIME[chat_id] = now
    return True

def random_reply():
    return random.choice(BB_REPLIES)

# ---- Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GROUP_CHAT_ID
    GROUP_CHAT_ID = update.effective_chat.id

    await update.message.reply_text(
        "मी Bigg Boss Marathi Fan आहे 🔥\n"
        "Eviction, Wildcard, Drama, Memes सगळ्यावर गप्पा मारूया 😄"
    )

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id

    # Spam control: 10 सेकंदात एक reply
    if not cooldown_ok(chat_id, seconds=10):
        return

    text = update.message.text.lower()

    if "eviction" in text or "बाहेर" in text:
        reply = "Eviction खूपच shocking वाटतंय यावेळी 😬 कोण जाईल वाटतं?"
    elif "wildcard" in text:
        reply = "Wildcard आला तर गेमच बदलून जाईल 🔥"
    elif "nomination" in text:
        reply = "Nomination लिस्ट बघून धक्का बसलाय 😅"
    elif "meme" in text or "मिम" in text:
        reply = random.choice(MEMES)
    else:
        # 30% वेळा meme टाका
        if random.random() < 0.3:
            reply = random.choice(MEMES)
        else:
            reply = random_reply()

    await update.message.reply_text(reply)

async def on_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll = update.poll
    await context.bot.send_message(
        chat_id=poll.chat.id,
        text="या poll वर मत द्या रे 😄 कोण जिंकणार वाटतंय?"
    )

# ---- Scheduled Messages ----
async def daily_prediction(context: ContextTypes.DEFAULT_TYPE):
    predictions = [
        "आज मोठं भांडण होणार वाटतंय 🔥",
        "आज कोणीतरी रडणार वाटतंय 😅",
        "आजचा task एकदम मजेशीर असेल 😂",
        "आज eviction मध्ये धक्का बसेल 😬",
    ]
    await context.bot.send_message(context.job.chat_id, random.choice(predictions))

async def episode_recap(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        context.job.chat_id,
        "कालचा एपिसोड full drama होता 🔥 तुमचं काय मत आहे?"
    )

async def weekly_elimination_prediction(context: ContextTypes.DEFAULT_TYPE):
    guesses = [
        "या आठवड्यात unexpected eviction होऊ शकतं 😬",
        "Strong contestant पण danger zone मध्ये वाटतोय 🔥",
        "Voting trend बघता धक्का बसणार वाटतोय 😅",
    ]
    await context.bot.send_message(context.job.chat_id, random.choice(guesses))

async def start_jobs(context: ContextTypes.DEFAULT_TYPE):
    if GROUP_CHAT_ID:
        context.job_queue.run_repeating(daily_prediction, interval=3600, first=30, chat_id=GROUP_CHAT_ID)
        context.job_queue.run_repeating(episode_recap, interval=7200, first=60, chat_id=GROUP_CHAT_ID)
        context.job_queue.run_repeating(weekly_elimination_prediction, interval=604800, first=120, chat_id=GROUP_CHAT_ID)

# ---- Main ----
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.add_handler(PollHandler(on_poll))

    app.job_queue.run_once(start_jobs, 20)

    print("🤖 Bigg Boss Marathi Bot Started...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
