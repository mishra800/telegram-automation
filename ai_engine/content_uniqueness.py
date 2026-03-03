"""
Content Uniqueness Checker
Prevents repetitive content and ensures variety
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class ContentUniquenessChecker:
    """Ensures content uniqueness and variety"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH.replace('analytics.db', 'content_history.db')
        self._init_db()
        
        # Similarity thresholds
        self.min_days_between_similar = 14  # Don't repeat similar content within 14 days
        self.similarity_threshold = 0.7  # 70% similarity = too similar
    
    def _init_db(self):
        """Initialize content history database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                content_preview TEXT NOT NULL,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_hash 
            ON content_history(content_hash)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_topic_date 
            ON content_history(topic, created_at)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Content uniqueness database initialized")
    
    def get_content_hash(self, content):
        """Generate hash of content for duplicate detection"""
        # Normalize content: lowercase, remove special chars, extra spaces
        normalized = ' '.join(content.lower().split())
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def extract_keywords(self, content):
        """Extract key words from content"""
        # Simple keyword extraction (first 10 meaningful words)
        words = content.lower().split()
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been'}
        keywords = [w for w in words if len(w) > 3 and w not in stop_words][:10]
        return ' '.join(keywords)
    
    def is_content_unique(self, content, topic):
        """Check if content is unique enough"""
        content_hash = self.get_content_hash(content)
        keywords = self.extract_keywords(content)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for exact duplicate
        cursor.execute('''
            SELECT id, created_at FROM content_history
            WHERE content_hash = ?
        ''', (content_hash,))
        
        duplicate = cursor.fetchone()
        if duplicate:
            logger.warning(f"Exact duplicate found from {duplicate[1]}")
            conn.close()
            return False
        
        # Check for similar content in recent history
        cutoff_date = datetime.now() - timedelta(days=self.min_days_between_similar)
        
        cursor.execute('''
            SELECT keywords, created_at FROM content_history
            WHERE topic = ? AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT 20
        ''', (topic, cutoff_date))
        
        recent_content = cursor.fetchall()
        conn.close()
        
        # Calculate similarity with recent content
        for recent_keywords, created_at in recent_content:
            similarity = self._calculate_similarity(keywords, recent_keywords)
            if similarity > self.similarity_threshold:
                logger.warning(f"Similar content found ({similarity:.0%} similar) from {created_at}")
                return False
        
        return True
    
    def _calculate_similarity(self, keywords1, keywords2):
        """Calculate similarity between two keyword sets"""
        if not keywords1 or not keywords2:
            return 0.0
        
        set1 = set(keywords1.split())
        set2 = set(keywords2.split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def save_content(self, content, topic):
        """Save content to history"""
        content_hash = self.get_content_hash(content)
        keywords = self.extract_keywords(content)
        preview = content[:200]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO content_history (topic, content_hash, content_preview, keywords)
            VALUES (?, ?, ?, ?)
        ''', (topic, content_hash, preview, keywords))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Content saved to history: {topic}")
    
    def cleanup_old_content(self, days=90):
        """Remove content older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            DELETE FROM content_history
            WHERE created_at < ?
        ''', (cutoff_date,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old content entries")
    
    def get_content_variety_score(self, topic, days=7):
        """Calculate content variety score for a topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT keywords FROM content_history
            WHERE topic = ? AND created_at >= ?
        ''', (topic, cutoff_date))
        
        recent_keywords = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if len(recent_keywords) < 2:
            return 1.0  # High variety if few posts
        
        # Calculate average similarity between all pairs
        total_similarity = 0
        comparisons = 0
        
        for i in range(len(recent_keywords)):
            for j in range(i + 1, len(recent_keywords)):
                similarity = self._calculate_similarity(recent_keywords[i], recent_keywords[j])
                total_similarity += similarity
                comparisons += 1
        
        avg_similarity = total_similarity / comparisons if comparisons > 0 else 0
        variety_score = 1.0 - avg_similarity  # Higher score = more variety
        
        return variety_score
