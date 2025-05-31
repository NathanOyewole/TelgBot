#!/usr/bin/env python3
"""
TelgBot - Main Entry Point
Author: Nathan Oyewole
Description: Automated Telegram bot for posting, replies, and profile management
"""

import os
import sys
import asyncio
# Corrected import: import the actual class name from src.bot
from src.bot import TelegramAutoBot # CHANGED: TelgBot to TelegramAutoBot
from src.config import Config
from src.utils.logger import setup_logger

def main():
    """Main function to start the bot"""
    # Setup logging
    logger = setup_logger()

    try:
        # Load configuration
        config = Config()

        # Validate required environment variables
        if not config.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN environment variable is required!")
            logger.error("💡 Create a bot with @BotFather and set BOT_TOKEN")
            sys.exit(1)

        if not config.USER_ID:
            logger.error("❌ USER_ID environment variable is required!")
            logger.error("💡 Get your user ID from @userinfobot and set USER_ID")
            sys.exit(1)

        # Create and start bot
        logger.info("🚀 Starting Telegram Auto Bot...")
        logger.info(f"📱 Bot Token: {config.BOT_TOKEN[:10]}...{config.BOT_TOKEN[-10:]}")
        logger.info(f"👤 Authorized User ID: {config.USER_ID}")

        # Corrected instantiation: use the correct class name
        bot = TelegramAutoBot(config.BOT_TOKEN, int(config.USER_ID)) # CHANGED: TelgBot to TelegramAutoBot, and passed arguments
        bot.run()

    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
