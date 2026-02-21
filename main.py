import os
import random
import sqlite3
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ====== CONFIG (Railway Variables वापर) ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

DB_FILE = "memes.db"

# ====== DB SETUP ======
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS memes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT NOT NULL
)
""")
conn.commit()

# ====== HELPERS ======
def save_meme(file_id: str):
    cur.execute("INSERT INTO memes (file_id) VALUES (?)", (file_id,))
    conn.commit()

def get_random_meme():
    cur.execute("SELECT file_id FROM memes ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    return row[0] if row else None

def get_latest_meme():
    cur.execute("SELECT file_id FROM memes ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    return row[0] if row else None

def get_count():
    cur.execute("SELECT COUNT(*) FROM memes")
    return cur.fetchone()[0]

# ====== COMMANDS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bigg Boss Marathi Fan Bot Started!\n\n"
        "👉 'meme de' लिहिलं की memes मिळतील\n"
        "👉 Admin ने आधी memes forward किंवा direct पाठवावेत\n\n"
        "Commands:\n"
        "/stats – किती memes आहेत\n"
        "/random – random meme\n"
        "/latest – latest meme"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = get_count()
    await update.message.reply_text(f"📊 Total memes: {count}")

async def random_meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = get_random_meme()
    if not file_id:
        await update.message.reply_text("❌ अजून memes नाहीत. आधी /syncmemes किंवा direct पाठव.")
        return
    await update.message.reply_photo(file_id)

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = get_latest_meme()
    if not file_id:
        await update.message.reply_text("❌ अजून memes नाहीत.")
        return
    await update.message.reply_photo(file_id)

# ====== TEXT TRIGGER ======
async def meme_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "meme de" in text:
        file_id = get_random_meme()
        if not file_id:
            await update.message.reply_text("❌ अजून memes नाहीत.")
            return
        await update.message.reply_photo(file_id)

# ====== SYNC (FORWARDED + DIRECT BOTH) ======
async def sync_memes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ तू admin नाहीस.")
        return
    await update.message.reply_text(
        "📥 Channel मधले memes forward कर किंवा थेट इथे photo/video पाठव.\n"
        "सगळं झाल्यावर 'done' लिही."
    )

async def collect_memes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    msg = update.message

    file_id = None

    if msg.photo:
        file_id = msg.photo[-1].file_id
    elif msg.video:
        file_id = msg.video.file_id
    elif msg.document and msg.document.mime_type.startswith("image"):
        file_id = msg.document.file_id

    if file_id:
        save_meme(file_id)
        await update.message.reply_text("✅ Meme saved!")

    if msg.text and msg.text.lower() == "done":
        await update.message.reply_text("🔥 Sync complete!")

# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("random", random_meme))
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(CommandHandler("syncmemes", sync_memes))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, meme_de))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.IMAGE, collect_memes))
    app.add_handler(MessageHandler(filters.TEXT, collect_memes))

    print("🤖 Bigg Boss Marathi Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
