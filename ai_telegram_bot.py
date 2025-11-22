# ai_telegram_bot.py

import os
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# --------------------------
# Get keys from environment
# --------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# --------------------------
# Conversation memory
# --------------------------
user_memory = {}

# --------------------------
# Command Handlers
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("Reset Chat", callback_data="reset")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello! I am your AI bot. Send me a message to start chatting.",
        reply_markup=reply_markup
    )

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "Send any message to chat with me.\nClick 'Reset Chat' to clear memory."
    )

async def reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    user_memory[user_id] = []
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Conversation memory has been reset.")

# --------------------------
# Message Handler
# --------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Initialize user memory
    if user_id not in user_memory:
        user_memory[user_id] = []

    # Append user message
    user_memory[user_id].append({"role": "user", "content": user_text})

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=user_memory[user_id]
    )

    bot_reply = response.choices[0].message.content

    # Save bot reply
    user_memory[user_id].append({"role": "assistant", "content": bot_reply})

    await update.message.reply_text(bot_reply)

# --------------------------
# Main function
# --------------------------
def main():
    print("Starting bot...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Callback buttons
    app.add_handler(CallbackQueryHandler(help_callback, pattern="help"))
    app.add_handler(CallbackQueryHandler(reset_callback, pattern="reset"))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

# --------------------------
# Run the bot
# --------------------------
if __name__ == "__main__":
    main()
