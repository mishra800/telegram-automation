"""
Content Queue System
Pre-generates content to ensure 99.9% uptime
"""

import sqlite3
import random
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger
from ai_engine.content_generator import ContentGenerator
from ai_engine.image_generator import ImageGenerator

logger = setup_logger(__name__)

class ContentQueue:
    def __init__(self, min_queue_size=20):
        self.db_path = Config.DB_PATH
        self.min_queue_size = min_queue_size
        self.content_gen = ContentGenerator()
        self.image_gen = ImageGenerator()
        self._init_db()
    
    def _init_db(self):
        """Initialize content queue table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content_text TEXT NOT NULL,
                image_path TEXT NOT NULL,
                content_type TEXT DEFAULT 'regular',
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                status TEXT DEFAULT 'ready'
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_queue_status 
            ON content_queue(status, priority DESC)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Content queue database initialized")
    
    def get_queue_size(self):
        """Get current queue size"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM content_queue WHERE status = 'ready'
        ''')
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def add_to_queue(self, topic, content_text, image_path, content_type='regular', priority=5):
        """Add pre-generated content to queue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO content_queue 
            (topic, content_text, image_path, content_type, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (topic, content_text, image_path, content_type, priority))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Added to queue: {topic} ({content_type})")
    
    def get_next_content(self, topic=None):
        """Get next content from queue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if topic:
            cursor.execute('''
                SELECT id, topic, content_text, image_path, content_type
                FROM content_queue
                WHERE status = 'ready' AND topic = ?
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            ''', (topic,))
        else:
            cursor.execute('''
                SELECT id, topic, content_text, image_path, content_type
                FROM content_queue
                WHERE status = 'ready'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            ''')
        
        row = cursor.fetchone()
        
        if row:
            content_id = row[0]
            
            # Mark as used
            cursor.execute('''
                UPDATE content_queue
                SET status = 'used', used_at = ?
                WHERE id = ?
            ''', (datetime.now(), content_id))
            
            conn.commit()
            conn.close()
            
            return {
                'id': row[0],
                'topic': row[1],
                'text': row[2],
                'image_path': row[3],
                'content_type': row[4]
            }
        
        conn.close()
        return None
    
    def fill_queue(self, target_size=None):
        """Fill queue with pre-generated content"""
        if target_size is None:
            target_size = self.min_queue_size
        
        current_size = self.get_queue_size()
        needed = target_size - current_size
        
        if needed <= 0:
            logger.info(f"Queue is full ({current_size} items)")
            return
        
        logger.info(f"Filling queue: need {needed} items")
        
        # Distribute topics evenly
        topics = Config.TOPICS
        items_per_topic = needed // len(topics)
        remainder = needed % len(topics)
        
        for topic in topics:
            count = items_per_topic + (1 if remainder > 0 else 0)
            remainder -= 1
            
            for i in range(count):
                try:
                    # Generate content
                    content = self.content_gen.generate_content(topic)
                    
                    # Generate image
                    title = content['text'].split('\n')[0][:50]
                    image_path = self.image_gen.generate_image(topic, title)
                    
                    # Add to queue
                    self.add_to_queue(
                        topic=topic,
                        content_text=content['text'],
                        image_path=image_path,
                        content_type='regular',
                        priority=5
                    )
                    
                except Exception as e:
                    logger.error(f"Error generating content for queue: {e}")
        
        new_size = self.get_queue_size()
        logger.info(f"Queue filled: {new_size} items ready")
    
    def get_emergency_content(self, topic):
        """Get emergency fallback content if queue is empty"""
        logger.warning("Using emergency fallback content")
        
        emergency_content = {
            'motivational': """🌟 Never Give Up

• Every expert was once a beginner
• Progress happens one step at a time
• Your effort today shapes tomorrow
• Believe in your journey
• Success is built daily

What's your goal today?

#Motivation #Success #Growth #Inspiration""",
            
            'tech_news': """🚀 Tech Update

• Innovation never stops
• New tools emerge daily
• Stay curious and keep learning
• Technology shapes our future
• Embrace the change

What tech excites you?

#Tech #Innovation #Future #Technology""",
            
            'ai_updates': """🤖 AI Progress

• AI is transforming industries
• New capabilities every week
• Democratizing access to tools
• Ethical development matters
• Future is collaborative

How do you use AI?

#AI #MachineLearning #Future #Innovation""",
            
            'data_science': """📊 Data Insights

• Data tells stories
• Analysis drives decisions
• Visualization matters
• Clean data is key
• Keep learning

What's your favorite tool?

#DataScience #Analytics #Python #Data""",
            
            'productivity': """⚡ Productivity Tip

• Focus on one thing at a time
• Take regular breaks
• Plan your day
• Eliminate distractions
• Celebrate progress

What's your best hack?

#Productivity #Focus #Success #Efficiency"""
        }
        
        text = emergency_content.get(topic, emergency_content['motivational'])
        
        # Generate emergency image
        title = text.split('\n')[0][:50]
        image_path = self.image_gen.generate_image(topic, title)
        
        return {
            'topic': topic,
            'text': text,
            'image_path': image_path,
            'content_type': 'emergency'
        }
    
    def cleanup_old_content(self, days=7):
        """Remove old used content from queue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            DELETE FROM content_queue
            WHERE status = 'used' AND used_at < ?
        ''', (cutoff_date,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted} old content items")
        return deleted
    
    def get_queue_stats(self):
        """Get queue statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                status,
                COUNT(*) as count,
                AVG(priority) as avg_priority
            FROM content_queue
            GROUP BY status
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'count': row[1],
                'avg_priority': row[2]
            }
        
        cursor.execute('''
            SELECT topic, COUNT(*) as count
            FROM content_queue
            WHERE status = 'ready'
            GROUP BY topic
        ''')
        
        topic_distribution = {}
        for row in cursor.fetchall():
            topic_distribution[row[0]] = row[1]
        
        conn.close()
        
        return {
            'by_status': stats,
            'by_topic': topic_distribution,
            'total_ready': stats.get('ready', {}).get('count', 0)
        }
    
    def prioritize_content(self, content_id, new_priority):
        """Change priority of queued content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE content_queue
            SET priority = ?
            WHERE id = ? AND status = 'ready'
        ''', (new_priority, content_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated priority for content {content_id} to {new_priority}")

def maintain_queue():
    """Scheduled task to maintain content queue"""
    queue = ContentQueue(min_queue_size=20)
    
    # Fill queue if needed
    queue.fill_queue(target_size=25)
    
    # Cleanup old content
    queue.cleanup_old_content(days=7)
    
    # Log stats
    stats = queue.get_queue_stats()
    logger.info(f"Queue stats: {stats}")
    
    return stats

if __name__ == "__main__":
    # Test the queue system
    queue = ContentQueue(min_queue_size=5)
    
    print(f"Current queue size: {queue.get_queue_size()}")
    
    # Fill queue
    queue.fill_queue(target_size=10)
    
    # Get stats
    stats = queue.get_queue_stats()
    print(f"\nQueue stats: {stats}")
    
    # Get next content
    content = queue.get_next_content()
    if content:
        print(f"\nNext content: {content['topic']}")
        print(f"Text preview: {content['text'][:100]}...")
    
    # Cleanup
    deleted = queue.cleanup_old_content(days=7)
    print(f"\nCleaned up {deleted} old items")
