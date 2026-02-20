import os
import random
import asyncio
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

GENERAL_REPLIES = [
    "अरे {name}, भारी बोललास रे 😆",
    "{name}, ह्यावर तर वेगळीच मजा आहे 😂",
    "हाहा {name}, तू full form मध्ये आहेस आज 🔥",
    "{name}, हे ऐकून episode आठवला 🤭",
    "मस्त मुद्दा काढलास {name} 😎",
    "ओके ओके 😄",
    "👀",
    "😂🔥",
]

KEYWORD_REPLIES = {
    "nomination": [
        "या आठवड्यात नॉमिनेशन तिखट आहेत 😬",
        "नॉमिनेशन मध्ये drama होणारच 🔥",
    ],
    "एपिसोड": [
        "आजचा episode full masala वाटतोय 🔥",
        "एपिसोड मध्ये आज भांडण होणार वाटतं 😆",
    ],
    "कॅप्टन": [
        "कॅप्टन पदासाठी fight जोरदार होईल 💪",
    ],
    "भांडण": [
        "भांडणांशिवाय Bigg Boss कसला 😅",
    ],
    "winner": [
        "Winner कोण होणार यावर सगळ्यांचे वेगवेगळे मत आहेत 😎",
    ]
}

JOKES = [
    "Bigg Boss घरात शांतता म्हणजे वादळ येण्याआधीची शांतता 😂",
    "घरातले भांडण पाहून popcorn संपत नाही 🤭",
    "आज episode पाहून उशीरापर्यंत झोप लागणार नाही 😆",
]

last_reply_time = {}
last_user_replied = None
bot_muted_until = 0

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_user_replied, bot_muted_until

    if not update.message or not update.message.text:
        return

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name or "दोस्त"
    text = update.message.text.lower()
    now = time.time()

    # 20% वेळा bot शांत
    if random.random() < 0.2:
        return

    # Human-like delay
    await asyncio.sleep(random.uniform(1.5, 3.5))

    # Poll feature
    if "poll" in text or "मतदान" in text:
        await update.message.reply_poll(
            question="आजचा Best Performer कोण?",
            options=["Contestant A", "Contestant B", "Contestant C", "Contestant D"],
            is_anonymous=False
        )
        return

    # Joke feature
    if "joke" in text or "विनोद" in text:
        await update.message.reply_text(random.choice(JOKES))
        return

    for keyword, responses in KEYWORD_REPLIES.items():
        if keyword.lower() in text:
            msg = random.choice(responses)
            break
    else:
        msg = random.choice(GENERAL_REPLIES).format(name=name)

    await update.message.reply_text(msg)

def main():
    TOKEN = os.environ.get("8224981554:AAFvfBIyGGtKaeqT7LZR4AoIXAgnP9id5Pc")
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN Railway Variables मध्ये add केलेला नाही!")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.run_polling()

if __name__ == "__main__":
    main()
