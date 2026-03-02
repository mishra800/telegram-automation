from analytics.database import AnalyticsDB
from bot.telegram_bot import get_post_stats_sync
from bot.logger import setup_logger

logger = setup_logger(__name__)

class AnalyticsCollector:
    def __init__(self):
        self.db = AnalyticsDB()
    
    def collect_stats(self):
        logger.info("Starting analytics collection...")
        
        posts = self.db.get_posts_for_stats_collection()
        
        if not posts:
            logger.info("No posts to collect stats for")
            return
        
        logger.info(f"Collecting stats for {len(posts)} posts")
        
        for post in posts:
            try:
                stats = get_post_stats_sync(post['chat_id'], post['message_id'])
                
                self.db.update_post_stats(
                    post['message_id'],
                    post['chat_id'],
                    stats['views'],
                    stats['forwards'],
                    stats['reactions']
                )
                
                logger.info(f"Updated stats for post {post['message_id']}: {stats['views']} views")
                
            except Exception as e:
                logger.error(f"Error collecting stats for post {post['message_id']}: {e}")
        
        logger.info("Analytics collection completed")
    
    def analyze_and_adjust(self):
        logger.info("Analyzing performance and adjusting strategy...")
        
        performance = self.db.get_topic_performance(days=7)
        
        if not performance:
            logger.info("No performance data available yet")
            return
        
        logger.info("Topic Performance (Last 7 days):")
        for tp in performance:
            logger.info(
                f"  {tp['topic']}: {tp['post_count']} posts, "
                f"{tp['avg_views']:.1f} avg views, "
                f"score: {tp['engagement_score']:.1f}"
            )
        
        self.db.update_topic_weights(performance)
        
        logger.info("Strategy adjustment completed")
