import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
# Load environment variables
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Flask server for Render health checks
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

load_dotenv()
BOT_TOKEN = os.getenv("bot_token")

# Configuration
TOKEN = BOT_TOKEN # Replace with your bot token
WEBHOOK_URL = "https://nova-test.onrender.com"  # Replace with your HTTPS URL
PORT = 10000  # Port to listen on (typically 443, 80, 88, or 8443)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text("Hello! I'm a bot with webhook support!")

async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all other commands"""
    command = update.message.text.split()[0].lower()
    await update.message.reply_text(f"Received command: {command}")

def main():
    # Create Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.COMMAND, handle_commands))

    # Run webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    Thread(target=run_flask).start()
    main()
