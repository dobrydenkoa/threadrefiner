import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_TOKEN = os.getenv("MISTRAL_API_TOKEN")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-medium-latest")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    headers = {
        "Authorization": f"Bearer {MISTRAL_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"model": MISTRAL_MODEL, "messages":[{"role":"user","content":user_msg}]}
    try:
        resp = requests.post(MISTRAL_URL, headers=headers, json=payload)
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"🔴 Error: {e}"
    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot running")
    app.run_polling()
