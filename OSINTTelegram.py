import os, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Load secrets from environment
API_URL  = os.getenv("API_URL")
API_KEY  = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Utility ===
def safe_get(d, key): return d.get(key, "N/A") if isinstance(d, dict) else "N/A"

def clean_address(addr):
    if not addr or addr == "N/A": return "N/A"
    addr = addr.replace("!!", ", ").replace("!", ", ")
    return ", ".join(part.strip() for part in addr.split(",") if part.strip())

# === Results Card ===
def format_results(data, query, telegram=False):
    if isinstance(data, dict): 
        data = [data]

    results = [f"🔍 <b>Search Results for:</b> <code>{query}</code>\n"] if telegram else []
    
    for idx, person in enumerate(data, 1):
        block = f"""
<b>━━━━━━━━━━━━━━━ 🟢 Person {idx} ━━━━━━━━━━━━━━━</b>
👤 <b>Name</b>        : <code>{safe_get(person,'name')}</code>
👔 <b>Father</b>      : <code>{safe_get(person,'fname')}</code>
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

# === Commands ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ <b>Welcome to HARSH - HAXCER OSINT Tool</b>\n\n"
        "✅ <i>Session Opened Successfully</i>\n\n"
        "📌 Use the format:\n"
        "   ➤ <code>/mobile_number</code>\n"
        "   ➤ <code>/aadhaar_number</code>\n"
        "   ➤ <code>/email@example.com</code>\n\n"
        "🚀 I will fetch detailed results for you.",
        parse_mode="HTML"
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = (update.message.text or "").strip()

    if not query.startswith("/"):
        await update.message.reply_text(
            "⚠️ <b>Invalid format!</b>\n\n"
            "👉 Please start queries with <code>/</code>\n"
            "   Example: <code>/9876543210</code>",
            parse_mode="HTML"
        )
        return

    query = query.lstrip("/")  # remove slash for API

    await update.message.reply_text("⏳ <i>Fetching results, please wait...</i>", parse_mode="HTML")

    try:
        resp = requests.get(f"{API_URL}?apikey={API_KEY}&query={query}", timeout=30)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        await update.message.reply_text(f"❌ <b>Error:</b> <code>{e}</code>\n🔒 Session Closed", parse_mode="HTML")
        return

    if not payload:
        await update.message.reply_text("❌ <b>No results found.</b>\n🔒 Session Closed", parse_mode="HTML")
        return

    result_text = format_results(payload, query, telegram=True)
    await update.message.reply_text(result_text + "\n\n🔒 <i>Session Closed — Thank you for using</i> @H4RSHB0Y", parse_mode="HTML")

# === Bot Runner ===
def telegram_mode():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    print("✅ Telegram Bot Running with Stylish UI...")
    app.run_polling()

if __name__ == "__main__":
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN missing")
    telegram_mode()
