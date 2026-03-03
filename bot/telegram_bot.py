import asyncio
import sqlite3
import time
from datetime import datetime, timedelta
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
from telegram.constants import ParseMode
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class AutoResponseSystem:
    """Professional auto-response system with FAQ and rate limiting"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH.replace('analytics.db', 'conversations.db')
        self._init_db()
        
        # FAQ mapping dictionary
        self.faq_responses = {
            'price': {
                'keywords': ['price', 'cost', 'pricing', 'how much', 'payment', 'pay'],
                'response': """💰 **Pricing Information**

Thank you for your interest! Our services are designed to provide maximum value.

📋 **Available Options:**
• Free resources and content (available on our channel)
• Premium courses and materials (pricing varies by product)
• Affiliate partnerships (commission-based)

For specific pricing details, please visit our website or contact us directly.

📧 **Contact:** [Your contact information]
🌐 **Website:** [Your website]

Is there anything specific you'd like to know about?"""
            },
            
            'link': {
                'keywords': ['link', 'url', 'website', 'site', 'where'],
                'response': """🔗 **Important Links**

Thank you for reaching out! Here are our official links:

🌐 **Main Website:** [Your website URL]
📱 **Social Media:**
   • Twitter: [Your Twitter]
   • LinkedIn: [Your LinkedIn]
   • Instagram: [Your Instagram]

📚 **Resources:**
   • Blog: [Your blog URL]
   • Documentation: [Your docs URL]

⚠️ **Note:** Please be cautious of fake links. Always verify you're on our official channels.

How else can I assist you today?"""
            },
            
            'details': {
                'keywords': ['details', 'info', 'information', 'tell me', 'explain', 'about'],
                'response': """ℹ️ **About Our Services**

Thank you for your interest! Here's what we offer:

🎯 **Our Mission:**
Providing high-quality content and resources in technology, AI, productivity, and personal development.

📊 **What We Offer:**
• Daily curated content on trending topics
• Educational resources and tutorials
• Industry insights and analysis
• Exclusive tips and strategies

🌟 **Why Choose Us:**
• Expert-curated content
• Regular updates and fresh insights
• Community-driven approach
• Proven track record

Would you like to know more about any specific area?"""
            },
            
            'how': {
                'keywords': ['how to', 'how do', 'how can', 'tutorial', 'guide', 'help'],
                'response': """📚 **How Can We Help?**

Thank you for reaching out! We're here to assist you.

🎓 **Getting Started:**
1. Follow our channel for daily updates
2. Check our pinned messages for important resources
3. Browse our content library
4. Join our community discussions

💡 **Need Specific Help?**
Please let us know what you're trying to achieve, and we'll guide you in the right direction.

📧 **Direct Support:**
For personalized assistance, please contact us at: [Your email]

What specific topic are you interested in?"""
            },
            
            'course': {
                'keywords': ['course', 'training', 'learn', 'education', 'class', 'program'],
                'response': """🎓 **Courses & Training**

Thank you for your interest in our educational programs!

📚 **Available Courses:**
• AI & Machine Learning Fundamentals
• Data Science Bootcamp
• Productivity Mastery
• Tech Career Development

✨ **Course Features:**
• Self-paced learning
• Practical projects
• Certificate of completion
• Lifetime access
• Community support

📅 **Enrollment:**
Courses are available year-round. Visit our website for current offerings and enrollment details.

🌐 **Learn More:** [Your courses URL]

Which area interests you most?"""
            },
            
            'affiliate': {
                'keywords': ['affiliate', 'partner', 'collaboration', 'promote', 'commission'],
                'response': """🤝 **Affiliate Partnership**

Thank you for your interest in partnering with us!

💼 **Affiliate Program Benefits:**
• Competitive commission rates (20-50%)
• High-quality products to promote
• Marketing materials provided
• Dedicated affiliate support
• Monthly payouts

📋 **Requirements:**
• Active audience in tech/business niche
• Professional online presence
• Commitment to quality promotion

📧 **Apply Now:**
Send your application to: [Your affiliate email]
Include: Your platform details, audience size, and why you'd be a great partner.

We review applications within 3-5 business days.

Any questions about the program?"""
            },
            
            'default': {
                'keywords': [],
                'response': """👋 **Hello!**

Thank you for reaching out to us!

I'm an automated assistant here to help you quickly. Here are some common topics I can assist with:

💰 **Pricing** - Ask about costs and payment options
🔗 **Links** - Get our official website and social media
ℹ️ **Details** - Learn more about our services
📚 **How-to** - Get guidance and tutorials
🎓 **Courses** - Explore our training programs
🤝 **Affiliate** - Partner with us

Please let me know what you're interested in, and I'll provide you with the relevant information!

For urgent matters or specific inquiries, please contact us directly at: [Your email]

How can I help you today?"""
            }
        }
        
        # Rate limiting: max 1 reply per user per 5 minutes
        self.rate_limit_seconds = 300  # 5 minutes
    
    def _init_db(self):
        """Initialize conversations database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                message_text TEXT,
                detected_keyword TEXT,
                response_sent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                chat_id INTEGER,
                message_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                user_id INTEGER PRIMARY KEY,
                last_response_time TIMESTAMP,
                response_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_timestamp 
            ON conversations(user_id, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_rate_limits_user 
            ON rate_limits(user_id)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Auto-response database initialized")
    
    def detect_keyword(self, message_text):
        """Detect keyword in message and return appropriate response"""
        message_lower = message_text.lower()
        
        # Check each FAQ category
        for category, data in self.faq_responses.items():
            if category == 'default':
                continue
            
            for keyword in data['keywords']:
                if keyword in message_lower:
                    return category, data['response']
        
        # Return default response if no keyword matched
        return 'default', self.faq_responses['default']['response']
    
    def check_rate_limit(self, user_id):
        """Check if user is within rate limit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT last_response_time FROM rate_limits WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return True  # First time user, allow response
        
        last_response_time = datetime.fromisoformat(result[0])
        time_since_last = datetime.now() - last_response_time
        
        if time_since_last.total_seconds() >= self.rate_limit_seconds:
            return True  # Rate limit expired, allow response
        
        logger.info(f"Rate limit active for user {user_id}")
        return False  # Still within rate limit
    
    def update_rate_limit(self, user_id):
        """Update rate limit for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rate_limits (user_id, last_response_time, response_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                last_response_time = ?,
                response_count = response_count + 1
        ''', (user_id, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def log_conversation(self, user_id, username, first_name, last_name, 
                        message_text, keyword, response, chat_id, message_id):
        """Log conversation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (user_id, username, first_name, last_name, message_text, 
             detected_keyword, response_sent, chat_id, message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, message_text,
              keyword, response, chat_id, message_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Conversation logged for user {user_id}")
    
    def get_conversation_stats(self, days=30):
        """Get conversation statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_conversations,
                COUNT(DISTINCT user_id) as unique_users,
                detected_keyword,
                COUNT(*) as keyword_count
            FROM conversations
            WHERE timestamp >= ?
            GROUP BY detected_keyword
            ORDER BY keyword_count DESC
        ''', (cutoff_date,))
        
        stats = cursor.fetchall()
        conn.close()
        
        return stats

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.channel_id = Config.TELEGRAM_CHANNEL_ID
        self.group_id = Config.TELEGRAM_GROUP_ID
        self.auto_response = AutoResponseSystem()
        self.application = None
        
    async def post_content(self, text, media_path, topic, media_type='image'):
        results = []
        
        if self.channel_id:
            result = await self._post_to_target(
                self.channel_id, text, media_path, topic, "channel", media_type
            )
            results.append(result)
        
        if self.group_id:
            result = await self._post_to_target(
                self.group_id, text, media_path, topic, "group", media_type
            )
            results.append(result)
        
        return results
    
    async def _post_to_target(self, target_id, text, media_path, topic, target_type, media_type='image'):
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Posting {media_type} to {target_type} (attempt {attempt + 1})")
                
                if media_type == 'video':
                    # Post video
                    with open(media_path, 'rb') as video:
                        message = await self.bot.send_video(
                            chat_id=target_id,
                            video=video,
                            caption=text,
                            parse_mode=ParseMode.MARKDOWN,
                            supports_streaming=True,
                            width=1080,
                            height=1920
                        )
                else:
                    # Post image (default)
                    with open(media_path, 'rb') as photo:
                        message = await self.bot.send_photo(
                            chat_id=target_id,
                            photo=photo,
                            caption=text,
                            parse_mode=ParseMode.MARKDOWN
                        )
                
                logger.info(f"Successfully posted {media_type} to {target_type}: {message.message_id}")
                
                return {
                    'success': True,
                    'message_id': message.message_id,
                    'chat_id': target_id,
                    'topic': topic,
                    'target_type': target_type
                }
                
            except TelegramError as e:
                logger.error(f"Telegram error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'topic': topic,
                        'target_type': target_type
                    }
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'topic': topic,
                    'target_type': target_type
                }
    
    async def get_post_stats(self, chat_id, message_id):
        try:
            chat = await self.bot.get_chat(chat_id)
            
            if chat.type == 'channel':
                return await self._get_channel_stats(chat_id, message_id)
            else:
                return {
                    'views': 0,
                    'forwards': 0,
                    'reactions': 0
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'views': 0,
                'forwards': 0,
                'reactions': 0
            }
    
    async def _get_channel_stats(self, chat_id, message_id):
        try:
            message = await self.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=chat_id,
                message_id=message_id
            )
            
            await self.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            
            return {
                'views': getattr(message, 'views', 0),
                'forwards': getattr(message, 'forwards', 0),
                'reactions': 0
            }
        except:
            return {
                'views': 0,
                'forwards': 0,
                'reactions': 0
            }
    
    async def handle_incoming_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages with auto-response"""
        try:
            message = update.message
            if not message or not message.text:
                return
            
            user = message.from_user
            user_id = user.id
            username = user.username or "Unknown"
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            message_text = message.text
            chat_id = message.chat_id
            message_id = message.message_id
            
            logger.info(f"Received message from {username} ({user_id}): {message_text[:50]}...")
            
            # Check rate limit
            if not self.auto_response.check_rate_limit(user_id):
                logger.info(f"Rate limit active for user {user_id}, skipping response")
                return
            
            # Detect keyword and get response
            keyword, response = self.auto_response.detect_keyword(message_text)
            
            # Send response
            await message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Update rate limit
            self.auto_response.update_rate_limit(user_id)
            
            # Log conversation
            self.auto_response.log_conversation(
                user_id, username, first_name, last_name,
                message_text, keyword, response, chat_id, message_id
            )
            
            logger.info(f"Auto-response sent to {username}: keyword={keyword}")
            
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}", exc_info=True)
    
    def start_auto_response_listener(self):
        """Start listening for incoming messages"""
        try:
            # Create application
            self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            
            # Add message handler (only for private messages)
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.ChatType.PRIVATE,
                    self.handle_incoming_message
                )
            )
            
            logger.info("Auto-response listener started")
            
            # Start polling in background
            self.application.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Error starting auto-response listener: {e}", exc_info=True)
    
    async def send_auto_response(self, chat_id, message_text):
        """Send auto-response to a specific chat"""
        try:
            keyword, response = self.auto_response.detect_keyword(message_text)
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info(f"Auto-response sent to chat {chat_id}: keyword={keyword}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending auto-response: {e}")
            return False

def post_content_sync(text, media_path, topic, media_type='image'):
    bot = TelegramBot()
    return asyncio.run(bot.post_content(text, media_path, topic, media_type))

def get_post_stats_sync(chat_id, message_id):
    bot = TelegramBot()
    return asyncio.run(bot.get_post_stats(chat_id, message_id))

async def get_follower_count_async():
    """Get follower count from Telegram channel"""
    bot = TelegramBot()
    try:
        if bot.channel_id:
            chat = await bot.bot.get_chat(bot.channel_id)
            # For channels, get member count
            count = await bot.bot.get_chat_member_count(bot.channel_id)
            logger.info(f"Channel {bot.channel_id} has {count} members")
            return count
        elif bot.group_id:
            count = await bot.bot.get_chat_member_count(bot.group_id)
            logger.info(f"Group {bot.group_id} has {count} members")
            return count
        else:
            logger.warning("No channel or group configured")
            return 0
    except Exception as e:
        logger.error(f"Error getting follower count: {e}")
        return 0

def get_follower_count_sync():
    """Synchronous wrapper for getting follower count"""
    return asyncio.run(get_follower_count_async())

def start_auto_response_system():
    """Start the auto-response system in background"""
    try:
        bot = TelegramBot()
        logger.info("Starting auto-response system...")
        bot.start_auto_response_listener()
    except Exception as e:
        logger.error(f"Error starting auto-response system: {e}", exc_info=True)

def get_conversation_stats_sync(days=30):
    """Get conversation statistics"""
    bot = TelegramBot()
    return bot.auto_response.get_conversation_stats(days)
