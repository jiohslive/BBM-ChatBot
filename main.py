import os
import random
import time
import asyncio
from datetime import datetime, time as dtime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, PollHandler, filters
)

# ====== RAILWAY VARIABLES ======
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables मध्ये add केलेला नाही!")
if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID Railway Variables मध्ये add केलेला नाही!")
if not TARGET_CHAT_ID:
    raise RuntimeError("TARGET_CHAT_ID Railway Variables मध्ये add केलेला नाही!")

# ====== GLOBALS ======
MEME_CACHE = []
LAST_REPLY = {}
REPLY_COOLDOWN = 10  # seconds

CONTESTANTS = ["अभिजीत", "सूरज", "निकिता", "अपूर्वा", "वैभव", "आर्या"]

BB_REPLIES = [
    "आज eviction कोणाचं होईल वाटतंय? 😬",
    "Wildcard आला तर गेम बदलणार 🔥",
    "आजचा episode full drama 😂🔥",
    "घरात आज tension आहे 😅",
    "Captaincy task रंगणार 👑",
    "आज nomination मध्ये twist येईल का? 👀"
]

QUIZ_QUESTIONS = [
    ("Bigg Boss Marathi चा host कोण आहे?", "महेश मांजरेकर"),
    ("आज घरात कोण dominate करतोय?", "जो जास्त भांडतो 😂"),
    ("तुझा favourite contestant कोण?", "तुझाच favourite 😎"),
]

MEME_CAPTIONS = [
    "😂 Bigg Boss Marathi Mood!",
    "🔥 आजचा Bigg Boss Vibe",
    "😆 House मधला Drama!",
    "👀 कोणाचं नाव येणार?",
    "🤣 हा बघ आजचा meme!"
]

EPISODE_HIGHLIGHTS = [
    "🔥 आजचा Highlight: मोठा भांडण आणि धमाल task!",
    "😱 आजच्या episode मध्ये जबरदस्त twist!",
    "😂 आज घरात comedy + drama दोन्ही!",
    "👑 आज captain बदलला!",
]

# ====== HELPERS ======
def should_reply(chat_id):
    now = time.time()
    last = LAST_REPLY.get(chat_id, 0)
    if now - last > REPLY_COOLDOWN:
        LAST_REPLY[chat_id] = now
        return True
    return False

def contestant_reply(text):
    for name in CONTESTANTS:
        if name.lower() in text:
            return f"👀 {name} बद्दल बोलतोयस का? आज तो/ती full highlight मध्ये आहे 😄🔥"
    return None

# ====== COMMANDS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙏 नमस्कार! मी Bigg Boss Marathi Fan Bot आहे 🔥\n\n"
        "📌 Commands:\n"
        "/latest – Latest meme\n"
        "/random – Random meme\n"
        "/stats – Bot stats\n"
        "/quiz – Bigg Boss quiz\n"
        "/syncmemes – Admin only\n\n"
        "माझ्याशी गप्पा मार 😄"
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MEME_CACHE:
        await update.message.reply_photo(random.choice(MEME_CACHE), caption=random.choice(MEME_CAPTIONS))
    else:
        await update.message.reply_text("Channel मध्ये अजून memes नाहीत 😭")

async def random_meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MEME_CACHE:
        await update.message.reply_photo(random.choice(MEME_CACHE), caption=random.choice(MEME_CAPTIONS))
    else:
        await update.message.reply_text("अजून memes नाहीत 😅")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 Total Memes Stored: {len(MEME_CACHE)}")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, _ = random.choice(QUIZ_QUESTIONS)
    await update.message.reply_text(f"🧠 Bigg Boss Quiz:\n{q}")

async def syncmemes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ हा command फक्त admin साठी आहे!")
    MEME_CACHE.clear()
    await update.message.reply_text("📥 Channel मधले memes bot ला forward कर. झाले की 'done' लिही.")

# ====== HANDLERS ======
async def receive_memes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        MEME_CACHE.append(update.message.photo[-1].file_id)

async def done_sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"✅ {len(MEME_CACHE)} memes sync झाले 🔥")

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if update.message.from_user.is_bot:
        return

    chat_id = update.effective_chat.id
    if not should_reply(chat_id):
        return

    text = update.message.text.lower()

    # Meme मागितला तर
    if "meme" in text:
        if MEME_CACHE:
            await update.message.reply_photo(random.choice(MEME_CACHE), caption=random.choice(MEME_CAPTIONS))
        else:
            await update.message.reply_text("अजून memes नाहीत 😭")
        return

    # Contestant नावावर smart reply
    c_reply = contestant_reply(text)
    if c_reply:
        await update.message.reply_text(c_reply)
        return

    await update.message.reply_text(random.choice(BB_REPLIES))

async def on_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🗳️ Vote केलास का? खाली comment टाक 👇"
    )

# ====== AUTO JOBS ======
async def daily_quiz(context: ContextTypes.DEFAULT_TYPE):
    q, _ = random.choice(QUIZ_QUESTIONS)
    await context.bot.send_message(TARGET_CHAT_ID, f"🧠 Daily Bigg Boss Quiz:\n{q}")

async def episode_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(TARGET_CHAT_ID, "🔔 आज 7:30 PM ला Bigg Boss Marathi episode आहे! 🔥📺")

async def episode_highlights(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(TARGET_CHAT_ID, f"🎬 Episode Highlights:\n{random.choice(EPISODE_HIGHLIGHTS)}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(CommandHandler("random", random_meme))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("syncmemes", syncmemes))

    app.add_handler(MessageHandler(filters.PHOTO, receive_memes))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^done$"), done_sync))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.add_handler(PollHandler(on_poll))

    jq = app.job_queue

    jq.run_daily(episode_reminder, time=dtime(hour=19, minute=30))
    jq.run_daily(daily_quiz, time=dtime(hour=21, minute=30))
    jq.run_daily(episode_highlights, time=dtime(hour=22, minute=0))

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
