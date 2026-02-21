import os
import random
import time
from datetime import datetime, time as dtime

from telegram import Update, ChatMemberUpdated
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, PollHandler, ChatMemberHandler, filters
)

# ====== RAILWAY VARIABLES ======
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables मध्ये add केलेला नाही!")
if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID Railway Variables मध्ये add केलेला नाही!")
if not TARGET_CHAT_ID:
    raise RuntimeError("TARGET_CHAT_ID Railway Variables मध्ये add केलेला नाही!")

# ====== GLOBALS ======
MEME_CACHE = []  # list of (file_id, caption)
LAST_REPLY = {}
REPLY_COOLDOWN = 10
MAINTENANCE_MODE = False

REMINDER_TIME = dtime(19, 30)  # default 7:30 PM
QUIZ_TIME = dtime(21, 30)      # default 9:30 PM

BB_REPLIES = [
    "आज eviction कोणाचं होईल वाटतंय? 😬",
    "Wildcard आला तर गेमच बदलून जाईल 🔥",
    "आजचा episode full drama असणार वाटतो 😂🔥",
    "त्या दोघांचं भांडण आज पेटणार वाटतं 😅",
    "Captaincy task मस्त रंगणार वाटतो 👑",
    "तुला आज कोण strongest वाटतो? 🤔",
]

QUIZ_QUESTIONS = [
    ("Bigg Boss Marathi चा host कोण आहे?", "महेश मांजरेकर"),
    ("आजच्या episode मध्ये काय twist येईल?", "कोणी तरी रडणार 😂"),
    ("तुझा favourite contestant कोण?", "तुझाच favourite 😎"),
]

AUTO_CAPTIONS = [
    "😂 Bigg Boss Marathi Mood!",
    "🔥 आजचा Bigg Boss Vibe",
    "😆 House मधला Drama!",
    "👀 कोणाचं नाव येणार?",
    "🤣 हा बघ आजचा meme!"
]

# ====== HELPERS ======
def should_reply(chat_id):
    now = time.time()
    last = LAST_REPLY.get(chat_id, 0)
    if now - last > REPLY_COOLDOWN:
        LAST_REPLY[chat_id] = now
        return True
    return False

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# ====== COMMANDS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙏 नमस्कार! मी Bigg Boss Marathi Fan Bot आहे 🔥\n\n"
        "📌 Commands:\n"
        "/latest – Latest meme\n"
        "/random – Random meme\n"
        "/stats – Bot stats\n"
        "/quiz – Bigg Boss quiz\n\n"
        "माझ्याशी गप्पा मार, मी reply देतो 😄"
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MEME_CACHE:
        file_id, caption = random.choice(MEME_CACHE)
        await update.message.reply_photo(file_id, caption=caption)
    else:
        await update.message.reply_text("अजून memes नाहीत 😭 आधी upload कर!")

async def random_meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await latest(update, context)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 Total Memes Stored: {len(MEME_CACHE)}")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, _ = random.choice(QUIZ_QUESTIONS)
    await update.message.reply_text(f"🧠 Bigg Boss Quiz:\n{q}\n\nउत्तर दे बघू 😄")

# ====== ADMIN PANEL ======
async def setreminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global REMINDER_TIME
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Admin only!")
    try:
        t = context.args[0]  # HH:MM
        h, m = map(int, t.split(":"))
        REMINDER_TIME = dtime(h, m)
        await update.message.reply_text(f"✅ Reminder time set to {t}")
    except Exception:
        await update.message.reply_text("❌ Format: /setreminder 19:30")

async def setquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUIZ_TIME
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Admin only!")
    try:
        t = context.args[0]
        h, m = map(int, t.split(":"))
        QUIZ_TIME = dtime(h, m)
        await update.message.reply_text(f"✅ Quiz time set to {t}")
    except Exception:
        await update.message.reply_text("❌ Format: /setquiz 21:30")

async def addmeme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Admin only!")
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("❌ फोटोला reply करून /addmeme <caption> वापर.")
    caption = " ".join(context.args) if context.args else random.choice(AUTO_CAPTIONS)
    file_id = update.message.reply_to_message.photo[-1].file_id
    MEME_CACHE.append((file_id, caption))
    await update.message.reply_text("✅ Meme add झाला 🔥")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Admin only!")
    msg = " ".join(context.args)
    if not msg:
        return await update.message.reply_text("❌ /broadcast <message>")
    await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=msg)
    await update.message.reply_text("✅ Broadcast sent")

async def maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Admin only!")
    if context.args and context.args[0].lower() == "on":
        MAINTENANCE_MODE = True
        await update.message.reply_text("🛠️ Maintenance ON (bot mute)")
    elif context.args and context.args[0].lower() == "off":
        MAINTENANCE_MODE = False
        await update.message.reply_text("✅ Maintenance OFF")
    else:
        await update.message.reply_text("❌ Use: /maintenance on | off")

# ====== HANDLERS ======
async def receive_memes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo and is_admin(update.effective_user.id):
        file_id = update.message.photo[-1].file_id
        caption = random.choice(AUTO_CAPTIONS)
        MEME_CACHE.append((file_id, caption))

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MAINTENANCE_MODE:
        return
    if not update.message or not update.message.text:
        return
    if update.message.from_user.is_bot:
        return
    chat_id = update.effective_chat.id
    if not should_reply(chat_id):
        return

    text = update.message.text.lower()
    if "meme" in text and MEME_CACHE:
        file_id, caption = random.choice(MEME_CACHE)
        return await update.message.reply_photo(file_id, caption=caption)

    await update.message.reply_text(random.choice(BB_REPLIES))

async def on_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🗳️ Vote टाका! कोण जिंकणार वाटतंय?"
    )

async def welcome_new_member(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE):
    if update.new_chat_member and update.new_chat_member.status == "member":
        name = update.new_chat_member.user.first_name
        msg = f"👋 Welcome {name}! Bigg Boss Marathi family मध्ये तुझं स्वागत आहे 🔥"
        if CHANNEL_LINK:
            msg += f"\n🔗 Channel: {CHANNEL_LINK}"
        await context.bot.send_message(chat_id=update.chat.id, text=msg)

# ====== JOBS ======
async def daily_quiz(context: ContextTypes.DEFAULT_TYPE):
    q, _ = random.choice(QUIZ_QUESTIONS)
    await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=f"🧠 Daily Quiz:\n{q}")

async def episode_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text="🔔 आज रात्री Bigg Boss Marathi चा episode आहे! विसरू नको 🔥📺"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(CommandHandler("random", random_meme))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("quiz", quiz))

    # Admin panel
    app.add_handler(CommandHandler("setreminder", setreminder))
    app.add_handler(CommandHandler("setquiz", setquiz))
    app.add_handler(CommandHandler("addmeme", addmeme))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("maintenance", maintenance))

    app.add_handler(MessageHandler(filters.PHOTO, receive_memes))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.add_handler(PollHandler(on_poll))
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

    # Jobs (JobQueue must be installed)
    jq = app.job_queue
    jq.run_daily(episode_reminder, time=REMINDER_TIME)
    jq.run_daily(daily_quiz, time=QUIZ_TIME)

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
