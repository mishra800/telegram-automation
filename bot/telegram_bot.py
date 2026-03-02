import asyncio
from telegram import Bot
from telegram.error import TelegramError
from telegram.constants import ParseMode
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.channel_id = Config.TELEGRAM_CHANNEL_ID
        self.group_id = Config.TELEGRAM_GROUP_ID
        
    async def post_content(self, text, image_path, topic):
        results = []
        
        if self.channel_id:
            result = await self._post_to_target(
                self.channel_id, text, image_path, topic, "channel"
            )
            results.append(result)
        
        if self.group_id:
            result = await self._post_to_target(
                self.group_id, text, image_path, topic, "group"
            )
            results.append(result)
        
        return results
    
    async def _post_to_target(self, target_id, text, image_path, topic, target_type):
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Posting to {target_type} (attempt {attempt + 1})")
                
                with open(image_path, 'rb') as photo:
                    message = await self.bot.send_photo(
                        chat_id=target_id,
                        photo=photo,
                        caption=text,
                        parse_mode=ParseMode.MARKDOWN
                    )
                
                logger.info(f"Successfully posted to {target_type}: {message.message_id}")
                
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

def post_content_sync(text, image_path, topic):
    bot = TelegramBot()
    return asyncio.run(bot.post_content(text, image_path, topic))

def get_post_stats_sync(chat_id, message_id):
    bot = TelegramBot()
    return asyncio.run(bot.get_post_stats(chat_id, message_id))
