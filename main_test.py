import os
import logging
import asyncio
from quart import Quart, request, jsonify
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Load environment variables
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("bot_token")

# Initialize Quart app
app = Quart(__name__)

# Initialize Telegram bot application
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Webhook URL (Replace with your actual URL)
WEBHOOK_URL = "https://nova-test.onrender.com/webhook"

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    welcome_msg = """
    🌠 Welcome to Nova!
    The fastest Telegram Bot on Solana.
    Nova allows you to buy or sell tokens in lightning-fast speed and also has many features including:
    Migration Sniping, Copy-trading, Limit Orders & a lot more.

    💡 Have an access code?
    • Enter it below to unlock instant access.

    ⏳ No access code?
    • Tap the button below to join the queue and be the first to experience lightning-fast transactions.

    🚀 Let's get started!
    """

    keyboard = [
        [InlineKeyboardButton("Join Queue", callback_data="join_queue")],
        [InlineKeyboardButton("Enter Access Code", callback_data="enter_code")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id, welcome_msg, reply_markup=reply_markup)

# Callback for button presses
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if query.data == "enter_code":
        await context.bot.send_message(chat_id, "Please enter your access or referral code.")
        context.user_data["awaiting_code"] = True

# Handle user access code input
async def handle_access_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_code"):
        chat_id = update.effective_chat.id
        access_code = update.message.text.strip()

        if access_code.lower() == "bullish":
            confirmation_msg = """
            🎉 Congratulations! Your access code has been successfully approved!

            Welcome to Nova — the Fastest All-In-One Trading Platform. Effortlessly trade any token on Solana with complete control at your fingertips.

            ✅ Access Granted: Nova Phase 1

            Don't forget to join our Support channel and explore the guide below for a smooth start:

            👉 [Join Support](https://t.me/TradeonNova)
            👉 Nova Guide
            👉 YouTube

            💡 Ready to begin? Press Continue below to start using Nova.
            """
            await context.bot.send_message(chat_id, confirmation_msg, parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id, "❌ Invalid access code. Please try again.")

        context.user_data["awaiting_code"] = False

# Quart route to handle Telegram webhook updates
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = await request.get_json()
        update = Update.de_json(data, bot_app.bot)

        # Ensure the bot is running
        if not bot_app.running:
            await bot_app.initialize()

        # Process the update
        asyncio.create_task(bot_app.process_update(update))
        return jsonify({"status": "ok"})

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Quart route for health check
@app.route("/healthcheck", methods=["GET"])
async def healthcheck():
    return jsonify({"status": "ok", "message": "The bot is running fine!"})

# Function to set the Telegram webhook
async def set_webhook():
    await bot_app.bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    # Add handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_access_code))

    # Run the bot and Quart app
    async def run():
        await bot_app.initialize()
        await set_webhook()
        await bot_app.start()
        await app.run_task(host="0.0.0.0", port=443)  # Render auto-assigns HTTPS

    asyncio.run(run())
