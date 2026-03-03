#!/usr/bin/env python3
"""
Telegram Content Automation System
Zero-Budget AI Content Generation and Auto-Posting
"""

import sys
import time
import signal
import threading
from bot.config import Config
from bot.logger import setup_logger
from bot.scheduler import ContentScheduler
from dashboard.app import run_dashboard

logger = setup_logger(__name__)

class AutomationSystem:
    def __init__(self):
        self.scheduler = None
        self.dashboard_thread = None
        self.running = False
    
    def start(self):
        try:
            logger.info("=" * 60)
            logger.info("TELEGRAM CONTENT AUTOMATION SYSTEM")
            logger.info("=" * 60)
            
            Config.validate()
            logger.info("Configuration validated successfully")
            
            self.scheduler = ContentScheduler()
            self.scheduler.start()
            logger.info("Content scheduler started")
            
            self.dashboard_thread = threading.Thread(
                target=run_dashboard,
                daemon=True
            )
            self.dashboard_thread.start()
            logger.info(f"Dashboard started at http://{Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
            
            self.running = True
            
            logger.info("=" * 60)
            logger.info("System is running!")
            if Config.GROWTH_MODE:
                logger.info(f"Mode: GROWTH (Dynamic posting based on followers)")
                logger.info(f"Current: {self.scheduler.current_posts_per_day} posts/day for {self.scheduler.current_follower_count} followers")
                logger.info(f"Thresholds: <{Config.FOLLOWER_THRESHOLD_LOW}={Config.POSTS_PER_DAY_LOW}/day, "
                          f"<{Config.FOLLOWER_THRESHOLD_HIGH}={Config.POSTS_PER_DAY_MEDIUM}/day, "
                          f"else={Config.POSTS_PER_DAY_HIGH}/day")
            else:
                logger.info(f"Mode: NORMAL ({Config.POSTS_PER_DAY_HIGH} posts/day)")
            logger.info(f"Timezone: {Config.TIMEZONE}")
            logger.info(f"Min interval: {Config.MIN_POST_INTERVAL_MINUTES} minutes")
            logger.info(f"Dashboard: http://localhost:{Config.DASHBOARD_PORT}")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 60)
            
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\nShutdown requested...")
            self.stop()
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            self.stop()
            sys.exit(1)
    
    def stop(self):
        logger.info("Stopping system...")
        self.running = False
        
        if self.scheduler:
            self.scheduler.stop()
            logger.info("Scheduler stopped")
        
        logger.info("System stopped successfully")
    
    def post_now(self, topic=None):
        if not self.scheduler:
            self.scheduler = ContentScheduler()
        
        logger.info(f"Manual post triggered{f' for topic: {topic}' if topic else ''}")
        self.scheduler.post_now(topic)

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "post-now":
            topic = sys.argv[2] if len(sys.argv) > 2 else None
            system = AutomationSystem()
            system.post_now(topic)
            return
        
        elif command == "test-content":
            from ai_engine.content_generator import ContentGenerator
            topic = sys.argv[2] if len(sys.argv) > 2 else 'motivational'
            gen = ContentGenerator()
            content = gen.generate_content(topic)
            print("\n" + "=" * 60)
            print(f"TOPIC: {topic}")
            print("=" * 60)
            print(content['text'])
            print("=" * 60)
            return
        
        elif command == "test-image":
            from ai_engine.image_generator import ImageGenerator
            topic = sys.argv[2] if len(sys.argv) > 2 else 'motivational'
            title = sys.argv[3] if len(sys.argv) > 3 else 'Test Image'
            gen = ImageGenerator()
            path = gen.generate_image(topic, title)
            print(f"Image generated: {path}")
            return
        
        elif command == "stats":
            from analytics.database import AnalyticsDB
            db = AnalyticsDB()
            stats = db.get_dashboard_stats()
            print("\n" + "=" * 60)
            print("SYSTEM STATISTICS")
            print("=" * 60)
            print(f"Total Posts: {stats['total_posts']}")
            print(f"Total Views: {stats['total_views']}")
            print(f"Total Forwards: {stats['total_forwards']}")
            print(f"Best Topic: {stats['best_topic']} ({stats['best_topic_views']} views)")
            print("=" * 60)
            return
        
        elif command == "auto-response":
            from bot.telegram_bot import start_auto_response_system
            print("\n" + "=" * 60)
            print("STARTING AUTO-RESPONSE SYSTEM")
            print("=" * 60)
            print("Listening for incoming messages...")
            print("Press Ctrl+C to stop")
            print("=" * 60 + "\n")
            start_auto_response_system()
            return
        
        elif command == "conversation-stats":
            from bot.telegram_bot import get_conversation_stats_sync
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            stats = get_conversation_stats_sync(days)
            print("\n" + "=" * 60)
            print(f"CONVERSATION STATISTICS (Last {days} days)")
            print("=" * 60)
            if stats:
                total = stats[0][0] if stats else 0
                unique = stats[0][1] if stats else 0
                print(f"Total Conversations: {total}")
                print(f"Unique Users: {unique}")
                print("\nKeyword Breakdown:")
                for stat in stats:
                    keyword = stat[2]
                    count = stat[3]
                    print(f"  {keyword}: {count}")
            else:
                print("No conversations recorded yet")
            print("=" * 60)
            return
        
        elif command == "help":
            print("""
Telegram Content Automation System - Commands:

  python main.py                    Start the automation system
  python main.py post-now [topic]   Post immediately (optional: specify topic)
  python main.py test-content [topic]  Test content generation
  python main.py test-image [topic] [title]  Test image generation
  python main.py stats              Show system statistics
  python main.py auto-response      Start auto-response system
  python main.py conversation-stats [days]  Show conversation statistics
  python main.py help               Show this help message

Available topics:
  - motivational
  - tech_news
  - ai_updates
  - data_science
  - productivity
            """)
            return
    
    system = AutomationSystem()
    
    def signal_handler(sig, frame):
        system.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    system.start()

if __name__ == "__main__":
    main()
