import os
import random
import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

# ====== Railway Variables ======
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN Railway Variables मध्ये add केलेला नाही!")

# Optional: Admin ID variable (नको असेल तर Railway मध्ये ADMIN_ID add करू नकोस)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

MEME_CACHE = []
LAST_REPLY = {}
REPLY_COOLDOWN = 10

BB_REPLIES = [
    "आज eviction कोणाचं होईल वाटतंय? 😬",
    "Wildcard आला तर गेमच बदलून जाईल 🔥",
    "आजचा episode full drama असणार वाटतो 😂🔥",
    "त्या दोघांचं भांडण आज पेटणार वाटतं 😅",
    "Captaincy task मस्त रंगणार वाटतो 👑",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bigg Boss Marathi Fan Bot Started!\n\n"
        "👉 'meme de' लिहिलं की memes मिळतील\n"
        "👉 Admin ने आधी /syncmemes करायचं"
    )

def should_reply(chat_id):
    now = time.time()
    last = LAST_REPLY.get(chat_id, 0)
    if now - last > REPLY_COOLDOWN:
        LAST_REPLY[chat_id] = now
        return True
    return False

# 👉 Admin manually sync memes (forward channel memes to bot)
async def sync_memes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID != 0 and update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("हे command फक्त admin साठी आहे ❌")
        return

    MEME_CACHE.clear()
    await update.message.reply_text(
        "📥 Channel मधले memes bot ला forward कर.\n"
        "सगळे forward झाले की 'done' लिही."
    )

async def receive_forwarded_memes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        MEME_CACHE.append(update.message.photo[-1].file_id)

async def done_sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID != 0 and update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(f"✅ {len(MEME_CACHE)} memes sync झाले 🔥")

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if update.message.from_user.is_bot:
        return

    chat_id = update.effective_chat.id
    if not should_reply(chat_id):
        return

    text = update.message.text.lower().strip()

    if "meme" in text:
        if MEME_CACHE:
            await update.message.reply_photo(
                photo=random.choice(MEME_CACHE),
                caption="😂🔥 Bigg Boss Marathi Meme"
            )
        else:
            await update.message.reply_text("Channel मध्ये अजून memes नाहीत 😭 आधी upload कर!")
        return

    if "eviction" in text:
        reply = "Eviction यावेळी खूपच shocking जाणार वाटतंय 😬"
    elif "wildcard" in text:
        reply = "Wildcard आला तर घरात आग लागेल 🔥😂"
    elif "nomination" in text:
        reply = "Nomination लिस्ट पाहून धक्का बसलाय 😅"
    elif "fight" in text or "भांडण" in text:
        reply = "आज भांडण झालंच पाहिजे नाहीतर episode फिक्का 😂🔥"
    else:
        reply = random.choice(BB_REPLIES)

    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("syncmemes", sync_memes))
    app.add_handler(MessageHandler(filters.PHOTO, receive_forwarded_memes))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^done$"), done_sync))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
