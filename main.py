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

LAST_REPLY = {}
REPLY_COOLDOWN = 20  # seconds

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

def get_random_meme_image():
    try:
        r = requests.get("https://meme-api.com/gimme", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("url")
    except Exception as e:
        print("Meme API error:", e)
    return None

def should_reply(chat_id):
    now = time.time()
    last = LAST_REPLY.get(chat_id, 0)
    if now - last > REPLY_COOLDOWN:
        LAST_REPLY[chat_id] = now
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "मी Bigg Boss Marathi Fan Bot आहे 🔥\n'meme de' लिहिलं की image meme येईल 😄"
    )

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if update.message.from_user.is_bot:
        return

    chat_id = update.effective_chat.id

    if not should_reply(chat_id):
        return

    text = update.message.text.lower().strip()

    # ---- FORCE IMAGE MEME ----
    if "meme" in text:
        meme_url = get_random_meme_image()
        if meme_url:
            await update.message.reply_photo(
                photo=meme_url,
                caption="😂🔥 Bigg Boss Meme"
            )
        else:
            await update.message.reply_text("आज meme API down आहे 😭 नंतर try कर")
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
    if not update.poll:
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="या poll वर मत द्या रे 😄 कोण जिंकणार वाटतंय?"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.add_handler(PollHandler(on_poll))

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
