import os
import requests
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_TOKEN = os.getenv("MISTRAL_API_TOKEN")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-medium-latest")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

DELAY_SECONDS = 1.5  # час очікування після останнього повідомлення

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    if "buffer" not in context.user_data:
        context.user_data["buffer"] = []

    context.user_data["buffer"].append(user_msg)

    # Скасувати попередню задачу
    if "task" in context.user_data:
        context.user_data["task"].cancel()

    # Запустити нову задачу з таймером
    async def delayed_send():
        await asyncio.sleep(DELAY_SECONDS)
        combined_text = "\n".join(context.user_data["buffer"])
        context.user_data["buffer"] = []

        headers = {
            "Authorization": f"Bearer {MISTRAL_TOKEN}",
        }

        json_data = {
            "model": MISTRAL_MODEL,
            "messages": [
                {"role": "user", "content": combined_text}
            ],
        }

        try:
            resp = requests.post(MISTRAL_URL, headers=headers, json=json_data)
            resp.raise_for_status()
            reply = resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"🔴 Error: {e}"

        await update.message.reply_text(reply)

    context.user_data["task"] = asyncio.create_task(delayed_send())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot running")
    app.run_polling()
