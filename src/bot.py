import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import schedule

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramAutoBot:
    def __init__(self, bot_token: str, user_id: int):
        self.bot_token = bot_token
        self.user_id = user_id
        self.bot = Bot(token=bot_token)
        self.application = Application.builder().token(bot_token).build()

        # Bot configuration
        self.config = {
            "auto_post_enabled": False,
            "reply_guy_enabled": False,
            "away_message_enabled": False,
            "post_interval_hours": 2,
            "reply_probability": 0.3,  # 30% chance to reply
        }

        # Storage for posts, replies, and user data
        self.scheduled_posts = []
        self.reply_templates = [
            "That's interesting! 🤔",
            "Great point! 👍",
            "I agree with this 💯",
            "Thanks for sharing! 🙏",
            "This is really helpful 💡",
            "Couldn't agree more! ✨",
            "Love this perspective 🔥",
            "So true! 💯"
        ]

        self.away_messages = [
            "Hey! I'm currently away but will get back to you soon! 🚀",
            "Thanks for your message! I'll respond when I'm back online 💫",
            "Away from keyboard right now, but I'll catch up with you later! ⚡"
        ]

        # Track who we've sent away messages to (reset daily)
        self.away_message_sent = {}

        self.setup_handlers()

    def setup_handlers(self):
        """Set up command and message handlers"""
        # Admin commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("config", self.config_command))
        self.application.add_handler(CommandHandler("toggle_autopost", self.toggle_autopost))
        self.application.add_handler(CommandHandler("toggle_replyguy", self.toggle_replyguy))
        self.application.add_handler(CommandHandler("toggle_away", self.toggle_away))
        self.application.add_handler(CommandHandler("add_post", self.add_scheduled_post))
        self.application.add_handler(CommandHandler("list_posts", self.list_posts))
        self.application.add_handler(CommandHandler("add_reply", self.add_reply_template))
        self.application.add_handler(CommandHandler("status", self.status_command))
        # --- NEW: Add the /post command handler ---
        self.application.add_handler(CommandHandler("post", self.post_command))
        # --- END NEW ---

        # Message handler for reply guy and away messages
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        if update.effective_user.id != self.user_id:
            await update.message.reply_text("⛔ Unauthorized access!")
            return

        welcome_msg = """
🤖 **Telegram Auto Bot is Ready!**

Available commands:
• `/config` - View current settings
• `/toggle_autopost` - Enable/disable auto posting
• `/toggle_replyguy` - Enable/disable reply guy mode
• `/toggle_away` - Enable/disable away messages
• `/add_post <text>` - Add scheduled post
• `/list_posts` - View scheduled posts
• `/add_reply <text>` - Add reply template
• `/status` - Check bot status
• `/help` - Show this help
• `/post` - Post the next scheduled post immediately

Let's automate your Telegram presence! 🚀
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command with detailed instructions"""
        help_text = """
🔧 **Bot Features:**

**1. Auto Posting** 📅
- Automatically posts from your scheduled content
- Set custom intervals between posts
- Add posts with `/add_post Your amazing content here!`

**2. Reply Guy Mode** 💬
- Automatically replies to messages in groups/channels
- Customizable reply probability
- Add custom replies with `/add_reply Your reply template`

**3. Away Messages** 🏃‍♂️
- Auto-responds when you're unavailable
- Sends once per person per day
- Perfect for maintaining engagement

**Quick Setup:**
1. `/toggle_autopost` - Start auto posting
2. `/add_post Hello world!` - Add your first post
3. `/toggle_replyguy` - Enable smart replies
4. `/toggle_away` - Set away mode

Use `/config` to see current settings!
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current configuration"""
        if update.effective_user.id != self.user_id:
            return

        config_text = f"""
⚙️ **Current Configuration:**

📝 Auto Post: {'✅ Enabled' if self.config['auto_post_enabled'] else '❌ Disabled'}
💬 Reply Guy: {'✅ Enabled' if self.config['reply_guy_enabled'] else '❌ Disabled'}
🏃‍♂️ Away Mode: {'✅ Enabled' if self.config['away_message_enabled'] else '❌ Disabled'}

📊 **Stats:**
• Post Interval: {self.config['post_interval_hours']} hours
• Reply Probability: {int(self.config['reply_probability'] * 100)}%
• Scheduled Posts: {len(self.scheduled_posts)}
• Reply Templates: {len(self.reply_templates)}
        """
        await update.message.reply_text(config_text, parse_mode='Markdown')

    async def toggle_autopost(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle auto posting"""
        if update.effective_user.id != self.user_id:
            return

        self.config['auto_post_enabled'] = not self.config['auto_post_enabled']
        status = "enabled" if self.config['auto_post_enabled'] else "disabled"
        await update.message.reply_text(f"📅 Auto posting {status}!")

    async def toggle_replyguy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle reply guy mode"""
        if update.effective_user.id != self.user_id:
            return

        self.config['reply_guy_enabled'] = not self.config['reply_guy_enabled']
        status = "enabled" if self.config['reply_guy_enabled'] else "disabled"
        await update.message.reply_text(f"💬 Reply guy mode {status}!")

    async def toggle_away(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle away messages"""
        if update.effective_user.id != self.user_id:
            return

        self.config['away_message_enabled'] = not self.config['away_message_enabled']
        status = "enabled" if self.config['away_message_enabled'] else "disabled"
        await update.message.reply_text(f"🏃‍♂️ Away messages {status}!")

    async def add_scheduled_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a scheduled post"""
        if update.effective_user.id != self.user_id:
            return

        if not context.args:
            await update.message.reply_text("❌ Please provide post content: `/add_post Your content here`")
            return

        post_content = " ".join(context.args)
        self.scheduled_posts.append({
            "content": post_content,
            "created_at": datetime.now().isoformat(),
            "posted": False
        })

        await update.message.reply_text(f"✅ Added scheduled post: '{post_content[:50]}...'")

    async def list_posts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List scheduled posts"""
        if update.effective_user.id != self.user_id:
            return

        if not self.scheduled_posts:
            await update.message.reply_text("📭 No scheduled posts yet. Add some with `/add_post`!")
            return

        posts_text = "📋 **Scheduled Posts:**\n\n"
        for i, post in enumerate(self.scheduled_posts[:10], 1):
            status = "✅ Posted" if post['posted'] else "⏳ Pending"
            content_preview = post['content'][:40] + "..." if len(post['content']) > 40 else post['content']
            posts_text += f"{i}. {content_preview} ({status})\n"

        if len(self.scheduled_posts) > 10:
            posts_text += f"\n... and {len(self.scheduled_posts) - 10} more posts"

        await update.message.reply_text(posts_text, parse_mode='Markdown')

    async def add_reply_template(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a reply template"""
        if update.effective_user.id != self.user_id:
            return

        if not context.args:
            await update.message.reply_text("❌ Please provide reply template: `/add_reply Your reply here`")
            return

        reply_content = " ".join(context.args)
        self.reply_templates.append(reply_content)

        await update.message.reply_text(f"✅ Added reply template: '{reply_content}'")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot status"""
        if update.effective_user.id != self.user_id:
            return

        uptime = datetime.now()  # You'd track actual uptime in a real implementation
        pending_posts = len([p for p in self.scheduled_posts if not p['posted']])

        status_text = f"""
🤖 **Bot Status Report**

🟢 Status: Online and Active
⏰ Last Check: {uptime.strftime('%H:%M:%S')}

📊 **Activity:**
• Pending Posts: {pending_posts}
• Away Messages Sent Today: {len(self.away_message_sent)}
• Total Reply Templates: {len(self.reply_templates)}

🔄 **Next Actions:**
• Auto Post: {'In ' + str(self.config['post_interval_hours']) + 'h' if self.config['auto_post_enabled'] else 'Disabled'}
• Reply Monitoring: {'Active' if self.config['reply_guy_enabled'] else 'Inactive'}
        """
        await update.message.reply_text(status_text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages for reply guy and away messages"""
        # Skip if message is from bot owner
        if update.effective_user.id == self.user_id:
            return

        # Away message logic
        if self.config['away_message_enabled']:
            user_id = update.effective_user.id
            today = datetime.now().date().isoformat()

            # Send away message once per user per day
            if user_id not in self.away_message_sent or self.away_message_sent[user_id] != today:
                away_message = random.choice(self.away_messages)
                await update.message.reply_text(away_message)
                self.away_message_sent[user_id] = today

        # Reply guy logic
        if self.config['reply_guy_enabled'] and random.random() < self.config['reply_probability']:
            # Add some delay to seem more natural
            await asyncio.sleep(random.uniform(1, 5))

            reply = random.choice(self.reply_templates)
            await update.message.reply_text(reply)

    # --- NEW: post_command function ---
    async def post_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Immediately posts the next scheduled post."""
        if update.effective_user.id != self.user_id:
            await update.message.reply_text("⛔ Unauthorized access!")
            return

        logger.info(f"Received /post command from user {update.effective_user.id}. Attempting to post.")

        unposted = [p for p in self.scheduled_posts if not p['posted']]

        if not unposted:
            await update.message.reply_text("🤔 No unposted content available to post manually.")
            return

        try:
            # Call the auto_post_job directly to handle the posting logic
            # This function needs to be awaited since it's an async function
            await self.auto_post_job()
            await update.message.reply_text("✅ Posted the next scheduled content!")
        except Exception as e:
            logger.error(f"Error while manually posting: {e}")
            await update.message.reply_text(f"❌ Failed to post content: {e}")

    # --- END NEW ---

    async def auto_post_job(self):
        """Job function for auto posting"""
        if not self.config['auto_post_enabled'] or not self.scheduled_posts:
            # If auto_post_enabled is False, this job should not run automatically
            # However, post_command will call it directly regardless of auto_post_enabled
            # So, we only exit if there are no posts at all.
            if not self.scheduled_posts:
                logger.info("Auto post job skipped: No scheduled posts.")
                return

            # If auto_post is disabled but manually triggered, we proceed.
            if not self.config['auto_post_enabled']:
                 logger.info("Auto post job running (manually triggered), though auto-posting is disabled.")


        # Find next unposted content
        unposted = [p for p in self.scheduled_posts if not p['posted']]
        if not unposted:
            logger.info("Auto post job skipped: No unposted content available.")
            return

        # Post the oldest unposted content
        post = unposted[0]
        try:
            # Post to your own chat or channel (you'll need to specify chat_id)
            # For demo purposes, we'll just log it
            logger.info(f"Attempting to send auto post: {post['content']}")
            
            # --- IMPORTANT: Replace YOUR_CHANNEL_ID with the actual chat ID you want to post to ---
            # await self.bot.send_message(chat_id=YOUR_CHANNEL_ID, text=post['content'])
            # For now, let's simulate sending if you don't have a specific chat_id
            await self.bot.send_message(chat_id=self.user_id, text=f"**Auto Post Simulation (to you):**\n\n{post['content']}", parse_mode='Markdown')
            logger.info(f"Successfully simulated posting: '{post['content'][:50]}...'")

            # Mark as posted
            post['posted'] = True
            post['posted_at'] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Error in auto posting (message: '{post['content'][:50]}...'): {e}")


    def run_scheduler(self):
        """Run the scheduler for auto posting"""
        # Ensure the scheduler task is created as an asyncio task
        # This lambda ensures auto_post_job is awaited correctly
        schedule.every(self.config['post_interval_hours']).hours.do(
            lambda: asyncio.create_task(self.auto_post_job())
        )

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def run(self):
        """Start the bot"""
        logger.info("🚀 Starting Telegram Auto Bot...")

        # Start scheduler in background
        import threading
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()

        # Start bot
        # This will block until the bot is stopped
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# Usage example (This part is in your main.py now, but included for completeness if testing bot.py directly)
if __name__ == "__main__":
    # Configuration
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
    USER_ID = 123456789  # Your Telegram user ID

    # Create and run bot
    bot = TelegramAutoBot(BOT_TOKEN, USER_ID)
    bot.run()
