import os
import random
import time
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, PollHandler, filters
)

# ====== RAILWAY VARIABLES ======
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN Railway Variables मध्ये add केलेला नाही!")

MEME_CACHE = []
LAST_REPLY = {}
REPLY_COOLDOWN = 10

BB_REPLIES = [
    "आज eviction कोणाचं होईल वाटतंय? 😬",
    "Wildcard आला तर गेमच बदलून जाईल 🔥",
    "आजचा episode full drama असणार वाटतो 😂🔥",
    "त्या दोघांचं भांडण आज पेटणार वाटतं 😅",
    "Captaincy task मस्त रंगणार वाटतो 👑",
    "तुला आज कोण strongest वाटतो? 🤔"
]

QUIZ_QUESTIONS = [
    ("Bigg Boss Marathi चा host कोण आहे?", "महेश मांजरेकर"),
    ("घरातलं सगळ्यात मोठं भांडण कधी झालं?", "कालच्या episode मध्ये 😂"),
    ("तुला कोण जिंकावा असं वाटतं?", "तुझा favouriteच 😎")
]

def should_reply(chat_id):
    now = time.time()
    last = LAST_REPLY.get(chat_id, 0)
    if now - last > REPLY_COOLDOWN:
        LAST_REPLY[chat_id] = now
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙏 नमस्कार! मी Bigg Boss Marathi Fan Bot आहे 🔥\n\n"
        "📌 Commands:\n"
        "/latest – Latest meme\n"
        "/random – Random meme\n"
        "/stats – Bot stats\n"
        "/quiz – Bigg Boss quiz\n"
        "/syncmemes – Admin only\n\n"
        "माझ्याशी गप्पा मार, मी reply देतो 😄"
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MEME_CACHE:
        await update.message.reply_photo(random.choice(MEME_CACHE), caption="🔥 Latest Meme")
    else:
        await update.message.reply_text("Channel मध्ये अजून memes नाहीत 😭 आधी upload कर!")

async def random_meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MEME_CACHE:
        await update.message.reply_photo(random.choice(MEME_CACHE), caption="🤣 Random Meme")
    else:
        await update.message.reply_text("अजून memes नाहीत रे 😅 आधी upload कर!")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 Total Memes: {len(MEME_CACHE)}")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, a = random.choice(QUIZ_QUESTIONS)
    await update.message.reply_text(f"🧠 Quiz:\n{q}\n\nReply दे बघू!")

async def syncmemes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ हा command फक्त admin साठी आहे!")
    MEME_CACHE.clear()
    await update.message.reply_text("📥 Channel मधले memes bot ला forward कर. झाले की 'done' लिही.")

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

    if "meme" in text:
        if MEME_CACHE:
            await update.message.reply_photo(random.choice(MEME_CACHE), caption="😂 Bigg Boss Meme")
        else:
            await update.message.reply_text("अजून memes नाहीत 😭")
        return

    reply = random.choice(BB_REPLIES)
    await update.message.reply_text(reply)

async def on_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🗳️ Vote टाका! कोण जिंकणार वाटतंय?"
    )

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

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
