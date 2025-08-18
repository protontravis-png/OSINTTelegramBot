import os, requests, json, time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === Load secrets from env ===
API_URL   = os.getenv("API_URL")
API_KEY   = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))   # set your chat id in env

# === Usage tracking ===
user_usage = {}
DAILY_LIMIT = 3

def reset_usage():
    """Reset usage counts daily."""
    today = datetime.now().strftime("%Y-%m-%d")
    for uid in list(user_usage.keys()):
        if user_usage[uid]["date"] != today:
            user_usage[uid] = {"count": 0, "date": today}

def safe_get(d, key): return d.get(key, "N/A") if isinstance(d, dict) else "N/A"

def clean_address(addr):
    if not addr or addr == "N/A": return "N/A"
    addr = addr.replace("!!", ", ").replace("!", ", ")
    return ", ".join(part.strip() for part in addr.split(",") if part.strip())

def format_results(data, query):
    if isinstance(data, dict): data = [data]
    results = [f"🔍 Results for: {query}\n"]
    for idx, person in enumerate(data, 1):
        block = f"""
👤 Person {idx}
📝 Name        : {safe_get(person,'name')}
👔 Father's    : {safe_get(person,'fname')}
🏡 Address     : {clean_address(safe_get(person,'address'))}
🌍 Circle      : {safe_get(person,'circle')}
📱 Mobile      : {safe_get(person,'mobile')}
📞 Alt Mobile  : {safe_get(person,'alt')}
🆔 Aadhaar     : {safe_get(person,'id')}
📧 Email       : {safe_get(person,'email')}
⚡ Credit      : @H4RSHB0Y
""".strip()
        results.append(block)
    return "\n\n".join(results)

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to HARSH - HAXCER OSINT Tool\n\n"
        "✅ Session Opened\n"
        "🔹 Send me a Mobile / Aadhaar / Email to fetch results."
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    reset_usage()

    # Admin bypass
    if chat_id != ADMIN_ID:
        # Initialize usage record if new user
        if chat_id not in user_usage:
            user_usage[chat_id] = {"count": 0, "date": datetime.now().strftime("%Y-%m-%d")}
        # Check limit
        if user_usage[chat_id]["count"] >= DAILY_LIMIT:
            await update.message.reply_text("⚠️ Daily limit reached (3 queries per day). Please try again tomorrow.")
            return
        # Increment usage
        user_usage[chat_id]["count"] += 1

    query = (update.message.text or "").strip()
    if not query:
        await update.message.reply_text("Please send a query.")
        return

    await update.message.reply_text("⏳ Fetching results...")

    try:
        resp = requests.get(f"{API_URL}?apikey={API_KEY}&query={query}", timeout=30)
        payload = resp.json()
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\n🔒 Session Closed")
        return

    if not payload:
        await update.message.reply_text("❌ No results found.\n🔒 Session Closed")
        return

    result_text = format_results(payload, query)
    await update.message.reply_text(result_text + "\n\n🔒 Session Closed — Thanks for using @H4RSHB0Y")

def telegram_mode():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    print("✅ Telegram Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN missing")
    telegram_mode()
