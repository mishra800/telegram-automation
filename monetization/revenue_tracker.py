import sqlite3
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class RevenueTracker:
    """Track revenue from different monetization sources"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_revenue_tables()
    
    def _init_revenue_tables(self):
        """Initialize revenue tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    description TEXT,
                    post_id INTEGER,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month TEXT NOT NULL,
                    goal_amount REAL NOT NULL,
                    actual_amount REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Revenue tracking tables initialized")
            
        except Exception as e:
            logger.error(f"Error initializing revenue tables: {e}")
    
    def add_revenue(self, source, amount, description=None, post_id=None):
        """Add revenue entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO revenue (source, amount, description, post_id)
                VALUES (?, ?, ?, ?)
            ''', (source, amount, description, post_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Revenue added: ${amount} from {source}")
            
        except Exception as e:
            logger.error(f"Error adding revenue: {e}")
    
    def get_total_revenue(self, days=30):
        """Get total revenue for period"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT SUM(amount)
                FROM revenue
                WHERE date >= datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            total = cursor.fetchone()[0] or 0.0
            conn.close()
            
            return total
            
        except Exception as e:
            logger.error(f"Error getting total revenue: {e}")
            return 0.0
    
    def get_revenue_by_source(self, days=30):
        """Get revenue breakdown by source"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    source,
                    SUM(amount) as total,
                    COUNT(*) as count,
                    AVG(amount) as avg
                FROM revenue
                WHERE date >= datetime('now', '-' || ? || ' days')
                GROUP BY source
                ORDER BY total DESC
            ''', (days,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'source': row[0],
                    'total': row[1],
                    'count': row[2],
                    'average': row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting revenue by source: {e}")
            return []
    
    def get_revenue_trend(self, days=30):
        """Get daily revenue trend"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    DATE(date) as day,
                    SUM(amount) as total
                FROM revenue
                WHERE date >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(date)
                ORDER BY day
            ''', (days,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'date': row[0],
                    'amount': row[1]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting revenue trend: {e}")
            return []
