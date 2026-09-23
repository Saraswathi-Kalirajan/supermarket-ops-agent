import os

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.agent.agent import process_message


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# =========================================================
# /start COMMAND
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🛒 Welcome to Supermarket Ops Agent!\n\n"
        "You can talk to me naturally.\n\n"
        "Examples:\n\n"
        "📦 How much Maggi do we have?\n"
        "📦 Check Maggi\n"
        "📦 How many Maggi packets are left?\n"
        "📦 Do we have Maggi?"
    )


# =========================================================
# HANDLE NORMAL MESSAGES
# =========================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.message.text.strip()

    if not message:
        return

    # Show processing message
    processing_message = await update.message.reply_text(
        "🤖 Thinking..."
    )

    try:

        # -------------------------------------------------
        # SEND USER MESSAGE TO AI AGENT
        # -------------------------------------------------

        result = process_message(message)

        # -------------------------------------------------
        # CHECK RESULT
        # -------------------------------------------------

        if result["success"]:

            response = result["message"]

        else:

            response = (
                f"❌ {result['message']}"
            )

        # -------------------------------------------------
        # SEND AI RESPONSE
        # -------------------------------------------------

        await processing_message.edit_text(
            response
        )

    except Exception as e:

        await processing_message.edit_text(
            f"❌ Error: {str(e)}"
        )


# =========================================================
# MAIN
# =========================================================

def main():

    if not TOKEN:

        raise ValueError(
            "TELEGRAM_BOT_TOKEN is missing from .env"
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # /start

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Normal text messages

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print(
        "🤖 Telegram AI Supermarket Agent is running..."
    )

    app.run_polling()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()