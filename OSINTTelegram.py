import os, requests, json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === Load secrets from env ===
API_URL   = os.getenv("API_URL")
API_KEY   = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))

# === Credits system ===
user_credits = {}   # {chat_id: credits}

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
    chat_id = update.effective_user.id
    credits = user_credits.get(chat_id, 0)
    if chat_id == ADMIN_ID:
        msg = "👋 Welcome Admin! ✅ Unlimited access."
    else:
        msg = f"👋 Welcome! You currently have 💳 {credits} credits."
    await update.message.reply_text(msg)

async def add_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    if chat_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
    except:
        await update.message.reply_text("⚠️ Usage: /add chat_id amount")
        return

    user_credits[target_id] = user_credits.get(target_id, 0) + amount
    await update.message.reply_text(f"✅ Added {amount} credits to {target_id}. Total = {user_credits[target_id]}")

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    query = (update.message.text or "").strip()

    # Must start with "/"
    if not query.startswith("/"):
        await update.message.reply_text("⚠️ Please start your query with '/' (example: /9227344169)")
        return
    query = query[1:]  # remove slash

    # Admin bypass
    if chat_id != ADMIN_ID:
        credits = user_credits.get(chat_id, 0)
        if credits <= 0:
            await update.message.reply_text("❌ You have no credits left. Contact admin.")
            return
        user_credits[chat_id] = credits - 1

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
    if chat_id == ADMIN_ID:
        await update.message.reply_text(result_text + "\n\n👑 Unlimited Access")
    else:
        credits_left = user_credits.get(chat_id, 0)
        await update.message.reply_text(result_text + f"\n\n💳 Credits left: {credits_left}")

def telegram_mode():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_credits))  # admin command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    print("✅ Telegram Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN missing")
    telegram_mode()
