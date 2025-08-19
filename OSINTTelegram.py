import os, requests, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Load secrets from environment
API_URL  = os.getenv("API_URL")
API_KEY  = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

def safe_get(d, key): return d.get(key, "N/A") if isinstance(d, dict) else "N/A"

def clean_address(addr):
    if not addr or addr == "N/A": return "N/A"
    addr = addr.replace("!!", ", ").replace("!", ", ")
    return ", ".join(part.strip() for part in addr.split(",") if part.strip())

def format_results(data, query, telegram=False):
    if isinstance(data, dict): data = [data]
    results = [f"🔍 <b>Results for:</b> <code>{query}</code>\n"] if telegram else []
    for idx, person in enumerate(data, 1):
        block = f"""
<b>━━━━━━━━━━━━━━━ 🟢 Person {idx} ━━━━━━━━━━━━━━━</b>
👤 <b>Name</b>        : <code>{safe_get(person,'name')}</code>
👔 <b>Father's</b>    : <code>{safe_get(person,'fname')}</code>
🏡 <b>Address</b>     : <code>{clean_address(safe_get(person,'address'))}</code>
🌍 <b>Circle</b>      : <code>{safe_get(person,'circle')}</code>
📱 <b>Mobile</b>      : <code>{safe_get(person,'mobile')}</code>
📞 <b>Alt Mobile</b>  : <code>{safe_get(person,'alt')}</code>
🆔 <b>Aadhaar</b>     : <code>{safe_get(person,'id')}</code>
📧 <b>Email</b>       : <code>{safe_get(person,'email')}</code>
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
⚡ <i>Powered by @H4RSHB0Y</i>
""".strip()
        results.append(block)
    return "\n\n".join(results)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ <b>Welcome to HARSH - HAXCER OSINT Tool</b>\n\n"
        "✅ <i>Session Opened</i>\n"
        "📌 Send me a <b>Mobile</b>, <b>Aadhaar</b>, or <b>Email</b>\n"
        "and I’ll fetch results instantly. 🚀",
        parse_mode="HTML"
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = (update.message.text or "").strip()
    await update.message.reply_text("⏳ <i>Fetching results...</i>", parse_mode="HTML")
    try:
        resp = requests.get(f"{API_URL}?apikey={API_KEY}&query={query}", timeout=30)
        payload = resp.json()
    except Exception as e:
        await update.message.reply_text(f"❌ <b>Error:</b> <code>{e}</code>\n🔒 Session Closed", parse_mode="HTML")
        return
    if not payload:
        await update.message.reply_text("❌ <b>No results found.</b>\n🔒 Session Closed", parse_mode="HTML")
        return
    result_text = format_results(payload, query, telegram=True)
    await update.message.reply_text(result_text + "\n\n🔒 <i>Session Closed — Thanks for using</i> @H4RSHB0Y", parse_mode="HTML")

def start_telegram_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    print("✅ Telegram Bot Running...")
    app.run_polling()

# ------------------- Flask Dummy Server -------------------
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

@app.route("/")
def index():
    return "🔹 Bot is running! 🔹"

if __name__ == "__main__":
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN missing")

    # Run Telegram polling in a separate thread
    threading.Thread(target=start_telegram_bot).start()

    # Run Flask web server (required by Render Web Service)
    app.run(host="0.0.0.0", port=PORT)
