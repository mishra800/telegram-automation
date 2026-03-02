import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from bot.config import Config
from bot.logger import setup_logger
from ai_engine.content_generator import ContentGenerator
from ai_engine.image_generator import ImageGenerator
from bot.telegram_bot import post_content_sync
from analytics.database import AnalyticsDB
from analytics.collector import AnalyticsCollector

logger = setup_logger(__name__)

class ContentScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=Config.TIMEZONE)
        self.content_gen = ContentGenerator()
        self.image_gen = ImageGenerator()
        self.db = AnalyticsDB()
        self.collector = AnalyticsCollector()
        
    def start(self):
        for post_time in Config.POST_TIMES:
            hour, minute = post_time.split(':')
            
            self.scheduler.add_job(
                self.create_and_post,
                CronTrigger(hour=int(hour), minute=int(minute)),
                id=f'post_{post_time}',
                name=f'Daily post at {post_time}'
            )
            logger.info(f"Scheduled post at {post_time}")
        
        self.scheduler.add_job(
            self.collector.collect_stats,
            CronTrigger(hour=2, minute=0),
            id='collect_stats',
            name='Daily stats collection'
        )
        logger.info("Scheduled daily stats collection at 02:00")
        
        self.scheduler.add_job(
            self.collector.analyze_and_adjust,
            CronTrigger(day_of_week='mon', hour=3, minute=0),
            id='analyze_adjust',
            name='Weekly strategy adjustment'
        )
        logger.info("Scheduled weekly analysis every Monday at 03:00")
        
        self.scheduler.start()
        logger.info("Scheduler started successfully")
    
    def create_and_post(self):
        try:
            logger.info("=" * 50)
            logger.info("Starting content creation and posting...")
            
            topic = self._select_topic()
            logger.info(f"Selected topic: {topic}")
            
            content = self.content_gen.generate_content(topic)
            logger.info("Content generated")
            
            title = content['text'].split('\n')[0][:50]
            image_path = self.image_gen.generate_image(topic, title)
            logger.info(f"Image generated: {image_path}")
            
            results = post_content_sync(content['text'], image_path, topic)
            
            for result in results:
                if result['success']:
                    self.db.save_post(
                        result['message_id'],
                        result['chat_id'],
                        result['topic'],
                        result['target_type']
                    )
                    logger.info(
                        f"Posted successfully to {result['target_type']}: "
                        f"Message ID {result['message_id']}"
                    )
                else:
                    logger.error(f"Failed to post to {result['target_type']}: {result.get('error')}")
            
            logger.info("Content creation and posting completed")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Error in create_and_post: {e}", exc_info=True)
    
    def _select_topic(self):
        weights = self.db.get_topic_weights()
        
        topics = list(weights.keys())
        topic_weights = [weights[t] for t in topics]
        
        selected = random.choices(topics, weights=topic_weights, k=1)[0]
        
        return selected
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def post_now(self, topic=None):
        if topic and topic not in Config.TOPICS:
            logger.error(f"Invalid topic: {topic}")
            return
        
        if topic:
            original_weights = self.db.get_topic_weights()
            temp_weights = {t: 0.0 for t in Config.TOPICS}
            temp_weights[topic] = 1.0
            
            for t, w in temp_weights.items():
                self.db.update_topic_weights([{
                    'topic': t,
                    'post_count': 0,
                    'total_views': 0,
                    'total_forwards': 0,
                    'avg_views': 0,
                    'avg_forwards': 0,
                    'engagement_score': w
                }])
        
        self.create_and_post()
        
        if topic:
            for t, w in original_weights.items():
                self.db.update_topic_weights([{
                    'topic': t,
                    'post_count': 0,
                    'total_views': 0,
                    'total_forwards': 0,
                    'avg_views': 0,
                    'avg_forwards': 0,
                    'engagement_score': w
                }])
