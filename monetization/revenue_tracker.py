import sqlite3
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class RevenueTracker:
    """Track revenue from different monetization sources with funnel integration"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_revenue_tables()
    
    def _init_revenue_tables(self):
        """Initialize revenue tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if revenue table exists
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='revenue'
            ''')
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Check if funnel_stage column exists
                cursor.execute('PRAGMA table_info(revenue)')
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'funnel_stage' not in columns:
                    # Add missing columns
                    cursor.execute('ALTER TABLE revenue ADD COLUMN funnel_stage TEXT')
                    logger.info("Added funnel_stage column to revenue table")
                
                if 'affiliate_product' not in columns:
                    cursor.execute('ALTER TABLE revenue ADD COLUMN affiliate_product TEXT')
                    logger.info("Added affiliate_product column to revenue table")
                
                if 'conversion_rate' not in columns:
                    cursor.execute('ALTER TABLE revenue ADD COLUMN conversion_rate REAL DEFAULT 0.0')
                    logger.info("Added conversion_rate column to revenue table")
            else:
                # Create new table with all columns
                cursor.execute('''
                    CREATE TABLE revenue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT DEFAULT 'USD',
                        description TEXT,
                        post_id INTEGER,
                        funnel_stage TEXT,
                        affiliate_product TEXT,
                        conversion_rate REAL DEFAULT 0.0,
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS post_revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL UNIQUE,
                    funnel_stage TEXT NOT NULL,
                    views INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0.0,
                    conversion_rate REAL DEFAULT 0.0,
                    roi REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_revenue_date 
                ON revenue(date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_revenue_stage 
                ON revenue(funnel_stage)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_post_revenue_stage 
                ON post_revenue(funnel_stage)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Revenue tracking tables initialized")
            
        except Exception as e:
            logger.error(f"Error initializing revenue tables: {e}")
    
    def add_revenue(self, source, amount, description=None, post_id=None, 
                   funnel_stage=None, affiliate_product=None, conversion_rate=0.0):
        """Add revenue entry with funnel tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO revenue 
                (source, amount, description, post_id, funnel_stage, 
                 affiliate_product, conversion_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (source, amount, description, post_id, funnel_stage, 
                  affiliate_product, conversion_rate))
            
            # Update post revenue if post_id provided
            if post_id:
                cursor.execute('''
                    INSERT INTO post_revenue (post_id, funnel_stage, revenue, conversions)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(post_id) DO UPDATE SET
                        revenue = revenue + ?,
                        conversions = conversions + 1,
                        updated_at = CURRENT_TIMESTAMP
                ''', (post_id, funnel_stage or 'unknown', amount, amount))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Revenue added: ${amount} from {source} (Stage: {funnel_stage})")
            
        except Exception as e:
            logger.error(f"Error adding revenue: {e}")
    
    def update_post_metrics(self, post_id, funnel_stage, views=None, clicks=None):
        """Update post performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if post exists
            cursor.execute('SELECT id FROM post_revenue WHERE post_id = ?', (post_id,))
            exists = cursor.fetchone()
            
            if not exists:
                # Create entry
                cursor.execute('''
                    INSERT INTO post_revenue (post_id, funnel_stage, views, clicks)
                    VALUES (?, ?, ?, ?)
                ''', (post_id, funnel_stage, views or 0, clicks or 0))
            else:
                # Update entry
                updates = []
                params = []
                
                if views is not None:
                    updates.append("views = ?")
                    params.append(views)
                
                if clicks is not None:
                    updates.append("clicks = ?")
                    params.append(clicks)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(post_id)
                    query = f"UPDATE post_revenue SET {', '.join(updates)} WHERE post_id = ?"
                    cursor.execute(query, params)
            
            # Calculate conversion rate
            cursor.execute('''
                UPDATE post_revenue
                SET conversion_rate = CASE 
                    WHEN clicks > 0 THEN (CAST(conversions AS REAL) / clicks) * 100
                    ELSE 0
                END,
                roi = CASE
                    WHEN views > 0 THEN (revenue / views) * 1000
                    ELSE 0
                END
                WHERE post_id = ?
            ''', (post_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating post metrics: {e}")
    
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
                    AVG(amount) as avg,
                    AVG(conversion_rate) as avg_conversion
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
                    'average': row[3],
                    'conversion_rate': row[4] or 0.0
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting revenue by source: {e}")
            return []
    
    def get_revenue_by_funnel_stage(self, days=30):
        """Get revenue breakdown by funnel stage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    funnel_stage,
                    SUM(amount) as total_revenue,
                    COUNT(*) as conversions,
                    AVG(amount) as avg_revenue,
                    AVG(conversion_rate) as avg_conversion_rate
                FROM revenue
                WHERE date >= datetime('now', '-' || ? || ' days')
                    AND funnel_stage IS NOT NULL
                GROUP BY funnel_stage
                ORDER BY 
                    CASE funnel_stage
                        WHEN 'viral' THEN 1
                        WHEN 'value' THEN 2
                        WHEN 'authority' THEN 3
                        WHEN 'soft_promotion' THEN 4
                        WHEN 'strong_cta' THEN 5
                        ELSE 6
                    END
            ''', (days,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'stage': row[0],
                    'revenue': row[1],
                    'conversions': row[2],
                    'avg_revenue': row[3],
                    'conversion_rate': row[4] or 0.0
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting revenue by funnel stage: {e}")
            return []
    
    def get_revenue_trend(self, days=30):
        """Get daily revenue trend"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    DATE(date) as day,
                    SUM(amount) as total,
                    COUNT(*) as conversions
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
                    'amount': row[1],
                    'conversions': row[2]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting revenue trend: {e}")
            return []
    
    def get_post_performance(self, days=30, limit=10):
        """Get top performing posts by revenue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    post_id,
                    funnel_stage,
                    views,
                    clicks,
                    conversions,
                    revenue,
                    conversion_rate,
                    roi
                FROM post_revenue
                WHERE created_at >= datetime('now', '-' || ? || ' days')
                ORDER BY revenue DESC
                LIMIT ?
            ''', (days, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'post_id': row[0],
                    'stage': row[1],
                    'views': row[2],
                    'clicks': row[3],
                    'conversions': row[4],
                    'revenue': row[5],
                    'conversion_rate': row[6],
                    'roi': row[7]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting post performance: {e}")
            return []
    
    def get_conversion_metrics(self, days=30):
        """Get overall conversion metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    SUM(views) as total_views,
                    SUM(clicks) as total_clicks,
                    SUM(conversions) as total_conversions,
                    SUM(revenue) as total_revenue,
                    AVG(conversion_rate) as avg_conversion_rate,
                    AVG(roi) as avg_roi
                FROM post_revenue
                WHERE created_at >= datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'views': result[0] or 0,
                    'clicks': result[1] or 0,
                    'conversions': result[2] or 0,
                    'revenue': result[3] or 0.0,
                    'conversion_rate': result[4] or 0.0,
                    'roi': result[5] or 0.0,
                    'ctr': (result[1] / result[0] * 100) if result[0] else 0.0
                }
            
            return {
                'views': 0,
                'clicks': 0,
                'conversions': 0,
                'revenue': 0.0,
                'conversion_rate': 0.0,
                'roi': 0.0,
                'ctr': 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting conversion metrics: {e}")
            return {}
