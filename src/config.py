"""
Configuration management for Telegram Auto Bot
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # Telegram Bot Settings
        self.BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
        self.USER_ID: int = int(os.getenv('USER_ID', '0'))
        
        # Bot Feature Settings
        self.AUTO_POST_ENABLED: bool = os.getenv('AUTO_POST_ENABLED', 'false').lower() == 'true'
        self.REPLY_GUY_ENABLED: bool = os.getenv('REPLY_GUY_ENABLED', 'false').lower() == 'true'
        self.AWAY_MESSAGE_ENABLED: bool = os.getenv('AWAY_MESSAGE_ENABLED', 'false').lower() == 'true'
        
        # Timing Settings
        self.POST_INTERVAL_HOURS: int = int(os.getenv('POST_INTERVAL_HOURS', '2'))
        self.REPLY_PROBABILITY: float = float(os.getenv('REPLY_PROBABILITY', '0.3'))
        self.REPLY_DELAY_MIN: int = int(os.getenv('REPLY_DELAY_MIN', '1'))
        self.REPLY_DELAY_MAX: int = int(os.getenv('REPLY_DELAY_MAX', '5'))
        
        # Channel/Group Settings
        self.TARGET_CHANNEL: Optional[str] = os.getenv('TARGET_CHANNEL')
        self.TARGET_GROUPS: list = self._parse_list(os.getenv('TARGET_GROUPS', ''))
        
        # Database Settings
        self.DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///bot_data.db')
        self.REDIS_URL: Optional[str] = os.getenv('REDIS_URL')
        
        # Logging Settings
        self.LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE: str = os.getenv('LOG_FILE', 'bot.log')
        
        # Deployment Settings
        self.PORT: int = int(os.getenv('PORT', '8000'))
        self.WEBHOOK_URL: Optional[str] = os.getenv('WEBHOOK_URL')
        self.ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
        
        # Feature Limits
        self.MAX_SCHEDULED_POSTS: int = int(os.getenv('MAX_SCHEDULED_POSTS', '100'))
        self.MAX_REPLY_TEMPLATES: int = int(os.getenv('MAX_REPLY_TEMPLATES', '50'))
        
        # Default Templates
        self.DEFAULT_REPLY_TEMPLATES = [
            "That's interesting! 🤔",
            "Great point! 👍",
            "I agree with this 💯",
            "Thanks for sharing! 🙏",
            "This is really helpful 💡",
            "Couldn't agree more! ✨",
            "Love this perspective 🔥",
            "So true! 💯"
        ]
        
        self.DEFAULT_AWAY_MESSAGES = [
            "Hey! I'm currently away but will get back to you soon! 🚀",
            "Thanks for your message! I'll respond when I'm back online 💫",
            "Away from keyboard right now, but I'll catch up with you later! ⚡"
        ]
    
    def _parse_list(self, value: str) -> list:
        """Parse comma-separated string into list"""
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == 'production'
    
    def validate(self) -> tuple[bool, list]:
        """Validate configuration and return (is_valid, errors)"""
        errors = []
        
        if not self.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not self.USER_ID or self.USER_ID == 0:
            errors.append("USER_ID is required and must be a valid Telegram user ID")
        
        if self.POST_INTERVAL_HOURS < 1:
            errors.append("POST_INTERVAL_HOURS must be at least 1")
        
        if not (0 <= self.REPLY_PROBABILITY <= 1):
            errors.append("REPLY_PROBABILITY must be between 0 and 1")
        
        if self.REPLY_DELAY_MIN > self.REPLY_DELAY_MAX:
            errors.append("REPLY_DELAY_MIN cannot be greater than REPLY_DELAY_MAX")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> dict:
        """Convert config to dictionary (excluding sensitive data)"""
        return {
            "auto_post_enabled": self.AUTO_POST_ENABLED,
            "reply_guy_enabled": self.REPLY_GUY_ENABLED,
            "away_message_enabled": self.AWAY_MESSAGE_ENABLED,
            "post_interval_hours": self.POST_INTERVAL_HOURS,
            "reply_probability": self.REPLY_PROBABILITY,
            "environment": self.ENVIRONMENT,
            "log_level": self.LOG_LEVEL,
            "max_scheduled_posts": self.MAX_SCHEDULED_POSTS,
            "max_reply_templates": self.MAX_REPLY_TEMPLATES
        }
