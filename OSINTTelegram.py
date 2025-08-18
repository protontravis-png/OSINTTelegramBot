import os
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === Load Secrets from Environment ===
API_URL   = os.getenv("API_URL")
API_KEY   = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))   # Admin Telegram Chat ID

# === CLI Colors (for logs only) ===
GREEN  = "\033[92m"
RESET  = "\033[0m"

# === Utility Functions ===
def safe_get(d, key):
    return d.get(key, "N/A") if isinstance(d, dict) else "N/A"

def clean_address(addr):
    if not addr or addr == "N/A":
        return "N/A"
    addr = addr.replace("!!", ", ").replace("!", ", ")
    return ", ".join(part.strip() for part in addr.split(",") if part.strip())

def format_results(data, query, telegram=False):
    if isinstance(data, dict):
        data = [data]

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
"""
        results.append(block.strip())
    return "\n\n".join(results)

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to HARSH - HAXCER OSINT Tool\n\n"
        "✅ Session Opened\n"
        "🔹 Send queries like:\n"
        "   /9876543210 (mobile)\n"
        "   /example@mail.com (email)\n"
        "   /123456789012 (Aadhaar)"
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not query.startswith("/"):
        await update.message.reply_text("⚠️ Please start queries with `/` (e.g. `/9876543210`).")
        return

    query = query[1:]  # remove "/"
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

# === Main Bot Runner ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

    print(f"{GREEN}✅ Telegram Bot Running...{RESET}")
    app.run_polling()

if __name__ == "__main__":
    main()
