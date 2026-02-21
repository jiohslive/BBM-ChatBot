import os
import random
import time
import requests
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

# ---- Memory for spam control ----
LAST_REPLY = {}
REPLY_COOLDOWN = 30  # seconds

# ---- Text memes & replies ----
BB_REPLIES = [
    "आज eviction कोणाचं होईल वाटतंय? 😬",
    "Wildcard आला तर गेमच बदलून जाईल 🔥",
    "आजचा episode full drama असणार वाटतो 😂🔥",
    "त्या दोघांचं भांडण आज पेटणार वाटतं 😅",
    "Captaincy task मस्त रंगणार वाटतो 👑",
]

TEXT_MEMES = [
    "Bigg Boss घरात शांतता म्हणजे वादळ येण्याआधीची शांतता 😂",
    "Nomination आला की सगळे suddenly साधू बनतात 😆",
    "आज episode पाहून झोप जाणार नाही 🤣",
    "घरात drama नसेल तर मजाच नाही 😎🔥",
]

# ---- Random meme image API ----
def get_random_meme_image():
    try:
        r = requests.get("https://meme-api.com/gimme", timeout=10)
        data = r.json()
        return data.get("url")
    except:
        return None

def should_reply(chat_id):
    now = time.time()
    last = LAST_REPLY.get(chat_id, 0)
    if now - last > REPLY_COOLDOWN:
        LAST_REPLY[chat_id] = now
        return True
    return False

# ---- Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "मी Bigg Boss Marathi Fan आहे 🔥\nEviction, Wildcard, Drama सगळ्यावर गप्पा मारूया 😄"
    )

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id

    # Admin / bot messages skip
    if update.message.from_user.is_bot:
        return

    # Spam control
    if not should_reply(chat_id):
        return

    text = update.message.text.lower()

    # Meme command
    if "meme" in text:
        meme_url = get_random_meme_image()
        if meme_url:
            await update.message.reply_photo(meme_url, caption="😂🔥 Bigg Boss style meme")
        else:
            await update.message.reply_text(random.choice(TEXT_MEMES))
        return

    if "eviction" in text:
        reply = "Eviction यावेळी खूपच shocking जाणार वाटतंय 😬 कोण जाईल वाटतं?"
    elif "wildcard" in text:
        reply = "Wildcard आला तर घरात आग लागेल 🔥😂"
    elif "nomination" in text:
        reply = "Nomination लिस्ट पाहून धक्का बसलाय 😅"
    elif "fight" in text or "भांडण" in text:
        reply = "आज भांडण झालंच पाहिजे नाहीतर episode फिक्का 😂🔥"
    else:
        reply = random.choice(BB_REPLIES)

    await update.message.reply_text(reply)

async def on_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll = update.poll
    if not poll:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="या poll वर मत द्या रे 😄 कोण जिंकणार वाटतंय?"
    )

# ---- Main ----
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.add_handler(PollHandler(on_poll))

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
