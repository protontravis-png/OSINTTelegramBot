import os, requests, sys, json, time
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
    if isinstance(data, dict): 
        data = [data]

    results = [f"🟢 <b>OSINT Intelligence Report</b>\n══════════════════════════════\n\n📂 <b>Case ID</b> : #{idx}\n🔍 <b>Query</b>   : <code>{query}</code>\n"] if telegram else []

    for idx, person in enumerate(data, 1):
        block = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>Identity</b>
   • Name       : <code>{safe_get(person,'name')}</code>
   • Father     : <code>{safe_get(person,'fname')}</code>

🏠 <b>Location</b>
   • Address    : <code>{clean_address(safe_get(person,'address'))}</code>
   • Circle     : <code>{safe_get(person,'circle')}</code>

📞 <b>Communication</b>
   • Mobile     : <code>{safe_get(person,'mobile')}</code>
   • Alt Mobile : <code>{safe_get(person,'alt')}</code>
   • Email      : <code>{safe_get(person,'email')}</code>

🆔 <b>Identification</b>
   • Aadhaar    : <code>{safe_get(person,'id')}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Status</b> : Scan Completed  
🔒 <i>Session Closed</i>  
⚡ Powered by @H4RSHB0Y
""".strip()
        results.append(block)

    return "\n\n".join(results)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛰️ <b>[ ACCESS GRANTED ]</b>\n"
        "══════════════════════════════\n\n"
        "👋 <b>Welcome, Agent</b>\n"
        "You are now connected to the <i>HARSH - HAXCER Intelligence Grid</i>.\n\n"
        "📂 <b>Available Operations:</b>\n"
        "   • <code>Mobile</code>  → Trace mobile owner\n"
        "   • <code>Aadhaar</code> → Fetch Aadhaar details\n"
        "   • <code>Email</code>   → Lookup linked identity\n\n"
        "💡 <i>Tip:</i> Just send the value (e.g. <code>9876543210</code>) and I’ll run the scan.\n\n"
        "🔒 <b>Session Status:</b> ACTIVE\n"
        "⚡ Powered by @H4RSHB0Y",
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

def telegram_mode():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    print("✅ Telegram Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN missing")
    telegram_mode()
