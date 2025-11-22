# ------------------------- IMPORTS -------------------------
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters

# ------------------------- CONFIG -------------------------
# Your keys (already filled)
TELEGRAM_TOKEN = "8498168248:AAF2W_NDuy_sv2VcpAib684gTVL4bc4EbEg"
OPENAI_API_KEY = "sk-proj-A0alIYJ9KXhnOzjPGynUAyLTo96W_L9Wli__tQfJ4aq4vJBHMldrHZqB7dRyQaqZ7ziEA"

openai.api_key = OPENAI_API_KEY

# ------------------------- CONVERSATION MEMORY -------------------------
chat_history = {}  # Stores messages per chat_id

# ------------------------- /START COMMAND -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 🤖 I am your AI bot.\nSend me any message and I will reply!\nType /menu to see options."
    )

# ------------------------- CHAT HANDLER -------------------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    if not user_message.strip():
        return

    # Initialize chat history if first message
    if chat_id not in chat_history:
        chat_history[chat_id] = []

    # Add user message to history
    chat_history[chat_id].append({"role": "user", "content": user_message})

    try:
        # Call OpenAI GPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=chat_history[chat_id]
        )
        reply = response['choices'][0]['message']['content']
    except Exception as e:
        reply = "Oops! Something went wrong 🤯"

    # Add AI reply to history
    chat_history[chat_id].append({"role": "assistant", "content": reply})

    await update.message.reply_text(reply)

# ------------------------- /MENU COMMAND -------------------------
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Help", callback_data='help')],
        [InlineKeyboardButton("Reset Chat", callback_data='reset')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

# ------------------------- BUTTON HANDLER -------------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "help":
        await query.edit_message_text("Send any message and I will reply using AI!")
    elif query.data == "reset":
        chat_history[chat_id] = []  # clear conversation
        await query.edit_message_text("Chat history cleared ✅")

# ------------------------- MAIN FUNCTION -------------------------
def main():
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("menu", menu))

        # Add message handler for normal text
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

        # Add button handler
        app.add_handler(CallbackQueryHandler(button))

        print("Bot is running...")
        app.run_polling()
    except Exception as e:
        print("Error:", e)

# ------------------------- START BOT -------------------------
if __name__ == "__main__":
    print("Starting bot...")
    main()
