import sqlite3
from datetime import datetime
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class AnalyticsDB:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_db()
    
    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    chat_id TEXT NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    topic TEXT NOT NULL,
                    views INTEGER DEFAULT 0,
                    forwards INTEGER DEFAULT 0,
                    reactions INTEGER DEFAULT 0,
                    target_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topic_weights (
                    topic TEXT PRIMARY KEY,
                    weight REAL DEFAULT 1.0,
                    total_posts INTEGER DEFAULT 0,
                    total_views INTEGER DEFAULT 0,
                    avg_engagement REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            for topic in Config.TOPICS:
                cursor.execute('''
                    INSERT OR IGNORE INTO topic_weights (topic, weight)
                    VALUES (?, 1.0)
                ''', (topic,))
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def save_post(self, message_id, chat_id, topic, target_type):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO posts (message_id, chat_id, topic, target_type)
                VALUES (?, ?, ?, ?)
            ''', (message_id, chat_id, topic, target_type))
            
            conn.commit()
            post_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Post saved: ID={post_id}, Topic={topic}")
            return post_id
            
        except Exception as e:
            logger.error(f"Error saving post: {e}")
            return None
    
    def update_post_stats(self, message_id, chat_id, views, forwards, reactions):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE posts
                SET views = ?, forwards = ?, reactions = ?
                WHERE message_id = ? AND chat_id = ?
            ''', (views, forwards, reactions, message_id, chat_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stats updated for message {message_id}")
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    def get_posts_for_stats_collection(self, hours_old=24):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, message_id, chat_id, topic
                FROM posts
                WHERE datetime(date) <= datetime('now', '-' || ? || ' hours')
                AND views = 0
                ORDER BY date DESC
                LIMIT 50
            ''', (hours_old,))
            
            posts = cursor.fetchall()
            conn.close()
            
            return [
                {'id': p[0], 'message_id': p[1], 'chat_id': p[2], 'topic': p[3]}
                for p in posts
            ]
            
        except Exception as e:
            logger.error(f"Error getting posts for stats: {e}")
            return []
    
    def get_topic_performance(self, days=7):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    topic,
                    COUNT(*) as post_count,
                    SUM(views) as total_views,
                    SUM(forwards) as total_forwards,
                    AVG(views) as avg_views,
                    AVG(forwards) as avg_forwards
                FROM posts
                WHERE datetime(date) >= datetime('now', '-' || ? || ' days')
                GROUP BY topic
                ORDER BY avg_views DESC
            ''', (days,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'topic': r[0],
                    'post_count': r[1],
                    'total_views': r[2] or 0,
                    'total_forwards': r[3] or 0,
                    'avg_views': r[4] or 0,
                    'avg_forwards': r[5] or 0,
                    'engagement_score': (r[4] or 0) + (r[5] or 0) * 2
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting topic performance: {e}")
            return []
    
    def update_topic_weights(self, topic_performance):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if not topic_performance:
                return
            
            max_score = max(tp['engagement_score'] for tp in topic_performance)
            
            if max_score == 0:
                return
            
            for tp in topic_performance:
                weight = 0.5 + (tp['engagement_score'] / max_score) * 1.5
                
                cursor.execute('''
                    UPDATE topic_weights
                    SET weight = ?,
                        total_posts = ?,
                        total_views = ?,
                        avg_engagement = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE topic = ?
                ''', (
                    weight,
                    tp['post_count'],
                    tp['total_views'],
                    tp['engagement_score'],
                    tp['topic']
                ))
            
            conn.commit()
            conn.close()
            
            logger.info("Topic weights updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating topic weights: {e}")
    
    def get_topic_weights(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT topic, weight FROM topic_weights')
            weights = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            return weights
            
        except Exception as e:
            logger.error(f"Error getting topic weights: {e}")
            return {topic: 1.0 for topic in Config.TOPICS}
    
    def get_dashboard_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*), SUM(views), SUM(forwards) FROM posts')
            total_posts, total_views, total_forwards = cursor.fetchone()
            
            cursor.execute('''
                SELECT topic, SUM(views) as views
                FROM posts
                GROUP BY topic
                ORDER BY views DESC
                LIMIT 1
            ''')
            best_topic = cursor.fetchone()
            
            cursor.execute('''
                SELECT date, SUM(views) as views
                FROM posts
                WHERE datetime(date) >= datetime('now', '-30 days')
                GROUP BY DATE(date)
                ORDER BY date
            ''')
            daily_views = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_posts': total_posts or 0,
                'total_views': total_views or 0,
                'total_forwards': total_forwards or 0,
                'best_topic': best_topic[0] if best_topic else 'N/A',
                'best_topic_views': best_topic[1] if best_topic else 0,
                'daily_views': daily_views
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {
                'total_posts': 0,
                'total_views': 0,
                'total_forwards': 0,
                'best_topic': 'N/A',
                'best_topic_views': 0,
                'daily_views': []
            }
