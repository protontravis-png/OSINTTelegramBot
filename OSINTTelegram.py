import os, json, time, sys, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

API_URL  = os.getenv("API_URL")
API_KEY  = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Colors (optional)
GREEN = "\033[92m"; BOLD="\033[1m"; RESET="\033[0m"

def safe_get(d, key): return d.get(key, "N/A") if isinstance(d, dict) else "N/A"

def clean_address(addr):
    if not addr or addr == "N/A": return "N/A"
    addr = addr.replace("!!", ", ").replace("!", ", ")
    return ", ".join(part.strip() for part in addr.split(",") if part.strip())

def format_results(data, query, telegram=False):
    if isinstance(data, dict): data = [data]
    results = [f"🔍 Results for: {query}\n"] if telegram else []
    for idx, person in enumerate(data, 1):
        name = safe_get(person, "name")
        father = safe_get(person, "fname")
        address = clean_address(safe_get(person, "address"))
        circle = safe_get(person, "circle")
        mobile = safe_get(person, "mobile")
        alt_mobile = safe_get(person, "alt")
        aadhaar = safe_get(person, "id")
        email = safe_get(person, "email")
        block = f"""
👤 Person {idx}
📝 Name        : {name}
👔 Father's    : {father}
🏡 Address     : {address}
🌍 Circle      : {circle}
📱 Mobile      : {mobile}
📞 Alt Mobile  : {alt_mobile}
🆔 Aadhaar     : {aadhaar}
📧 Email       : {email}
⚡ Credit      : @H4RSHB0Y
""".strip()
        results.append(block)
    return "\n\n".join(results)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to HARSH - HAXCER OSINT Tool\n\n"
        "✅ Session Opened\n"
        "🔹 Send me a Mobile / Aadhaar / Email and I’ll fetch results."
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    result_text = format_results(payload, query, telegram=True)
    await update.message.reply_text(result_text + "\n\n🔒 Session Closed — Thanks for using @H4RSHB0Y")

def telegram_mode():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    print(f"{GREEN}{BOLD}✅ Telegram Bot Running...{RESET}")
    app.run_polling()

if __name__ == "__main__":
    # Simple sanity checks so it fails clearly in logs if vars are missing
    missing = [k for k in ["API_URL","API_KEY","BOT_TOKEN"] if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
    telegram_mode()
