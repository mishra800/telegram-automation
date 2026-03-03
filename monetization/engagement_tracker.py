import sqlite3
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class EngagementTracker:
    """Track user engagement and content performance"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_engagement_tables()
    
    def _init_engagement_tables(self):
        """Initialize engagement tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Content performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    topic TEXT,
                    content_type TEXT,
                    has_affiliate BOOLEAN,
                    views INTEGER DEFAULT 0,
                    forwards INTEGER DEFAULT 0,
                    reactions INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    revenue REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Best posting times table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posting_times (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hour INTEGER,
                    day_of_week INTEGER,
                    avg_views REAL DEFAULT 0.0,
                    avg_engagement REAL DEFAULT 0.0,
                    post_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Viral content patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS viral_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    topic TEXT,
                    avg_views REAL,
                    avg_engagement REAL,
                    success_rate REAL,
                    sample_count INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Engagement tracking tables initialized")
            
        except Exception as e:
            logger.error(f"Error initializing engagement tables: {e}")
    
    def track_post_performance(self, post_id, topic, content_type, has_affiliate, views, forwards, reactions):
        """Track individual post performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            engagement_rate = (forwards + reactions) / max(views, 1) * 100
            
            cursor.execute('''
                INSERT INTO content_performance 
                (post_id, topic, content_type, has_affiliate, views, forwards, reactions, engagement_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (post_id, topic, content_type, has_affiliate, views, forwards, reactions, engagement_rate))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Tracked performance for post {post_id}: {engagement_rate:.2f}% engagement")
            
        except Exception as e:
            logger.error(f"Error tracking post performance: {e}")
    
    def get_best_posting_times(self):
        """Analyze and return best times to post"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    strftime('%H', date) as hour,
                    AVG(views) as avg_views,
                    COUNT(*) as post_count
                FROM posts
                WHERE views > 0
                GROUP BY hour
                ORDER BY avg_views DESC
                LIMIT 5
            ''')
            
            best_times = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'hour': int(row[0]),
                    'avg_views': row[1],
                    'post_count': row[2]
                }
                for row in best_times
            ]
            
        except Exception as e:
            logger.error(f"Error getting best posting times: {e}")
            return []
    
    def get_top_performing_content(self, limit=10):
        """Get top performing content types"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    topic,
                    content_type,
                    AVG(engagement_rate) as avg_engagement,
                    AVG(views) as avg_views,
                    COUNT(*) as count
                FROM content_performance
                GROUP BY topic, content_type
                ORDER BY avg_engagement DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'topic': row[0],
                    'content_type': row[1],
                    'avg_engagement': row[2],
                    'avg_views': row[3],
                    'count': row[4]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting top content: {e}")
            return []
    
    def get_affiliate_performance(self):
        """Analyze affiliate link performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    topic,
                    AVG(CASE WHEN has_affiliate THEN engagement_rate ELSE 0 END) as with_affiliate,
                    AVG(CASE WHEN NOT has_affiliate THEN engagement_rate ELSE 0 END) as without_affiliate,
                    SUM(CASE WHEN has_affiliate THEN 1 ELSE 0 END) as affiliate_count
                FROM content_performance
                GROUP BY topic
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'topic': row[0],
                    'with_affiliate': row[1],
                    'without_affiliate': row[2],
                    'affiliate_count': row[3],
                    'impact': row[1] - row[2]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error analyzing affiliate performance: {e}")
            return []
    
    def get_engagement_insights(self):
        """Get comprehensive engagement insights"""
        return {
            'best_times': self.get_best_posting_times(),
            'top_content': self.get_top_performing_content(),
            'affiliate_performance': self.get_affiliate_performance()
        }
