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

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN Railway Variables मध्ये add केलेला नाही!")

# 👉 तुझ्या channel चा username इथे टाक ( @ शिवाय )
MEME_CHANNEL_USERNAME = "BigBossMarathiMemes"  # example: BigBossMemes

LAST_REPLY = {}
REPLY_COOLDOWN = 10  # seconds

BB_REPLIES = [
    "आज eviction कोणाचं होईल वाटतंय? 😬",
    "Wildcard आला तर गेमच बदलून जाईल 🔥",
    "आजचा episode full drama असणार वाटतो 😂🔥",
    "त्या दोघांचं भांडण आज पेटणार वाटतं 😅",
    "Captaincy task मस्त रंगणार वाटतो 👑",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "मी Bigg Boss Marathi Fan Bot आहे 🔥\n'meme de' लिहिलं की Season 6 चे memes येतील 😎"
    )

def should_reply(chat_id):
    now = time.time()
    last = LAST_REPLY.get(chat_id, 0)
    if now - last > REPLY_COOLDOWN:
        LAST_REPLY[chat_id] = now
        return True
    return False

async def get_random_meme_from_channel(context: ContextTypes.DEFAULT_TYPE):
    try:
        chat = await context.bot.get_chat(f"@{MEME_CHANNEL_USERNAME}")
        messages = []
        async for msg in context.bot.get_chat_history(chat_id=chat.id, limit=50):
            if msg.photo:
                messages.append(msg)

        if not messages:
            return None

        return random.choice(messages)

    except Exception as e:
        print("Channel meme fetch error:", e)
        return None

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if update.message.from_user.is_bot:
        return

    chat_id = update.effective_chat.id
    if not should_reply(chat_id):
        return

    text = update.message.text.lower().strip()

    # 🔥 MEME COMMAND
    if "meme" in text:
        meme_msg = await get_random_meme_from_channel(context)
        if meme_msg:
            await update.message.reply_photo(
                photo=meme_msg.photo[-1].file_id,
                caption="😂🔥 Bigg Boss Marathi S6 Meme"
            )
        else:
            await update.message.reply_text("Channel मध्ये अजून memes नाहीत 😭 आधी upload कर!")
        return

    # NORMAL CHAT
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

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
