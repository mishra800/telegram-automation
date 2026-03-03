"""
Smart Affiliate Optimization System
Tracks performance and optimizes affiliate product selection
"""

import sqlite3
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class SmartAffiliateOptimizer:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize affiliate tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                topic TEXT NOT NULL,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0.0,
                ctr REAL DEFAULT 0.0,
                conversion_rate REAL DEFAULT 0.0,
                roi REAL DEFAULT 0.0,
                last_used TIMESTAMP,
                performance_score REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                test_start TIMESTAMP,
                test_end TIMESTAMP,
                result TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Smart affiliate database initialized")
    
    def track_impression(self, product_name, topic):
        """Track when affiliate product is shown"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO affiliate_performance 
            (product_name, topic, impressions, last_used)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(product_name) DO UPDATE SET
            impressions = impressions + 1,
            last_used = ?
        ''', (product_name, topic, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def track_click(self, product_name):
        """Track when affiliate link is clicked"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE affiliate_performance
            SET clicks = clicks + 1
            WHERE product_name = ?
        ''', (product_name,))
        
        conn.commit()
        conn.close()
        
        self._update_metrics(product_name)
    
    def track_conversion(self, product_name, revenue):
        """Track when affiliate sale is made"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE affiliate_performance
            SET conversions = conversions + 1,
                revenue = revenue + ?
            WHERE product_name = ?
        ''', (revenue, product_name))
        
        conn.commit()
        conn.close()
        
        self._update_metrics(product_name)
        logger.info(f"Conversion tracked: {product_name} - ${revenue}")
    
    def _update_metrics(self, product_name):
        """Calculate and update performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT impressions, clicks, conversions, revenue
            FROM affiliate_performance
            WHERE product_name = ?
        ''', (product_name,))
        
        row = cursor.fetchone()
        if row:
            impressions, clicks, conversions, revenue = row
            
            # Calculate metrics
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
            roi = revenue  # Simplified ROI (no cost tracking yet)
            
            # Calculate performance score (weighted)
            performance_score = (
                ctr * 0.3 +  # 30% weight on CTR
                conversion_rate * 0.4 +  # 40% weight on conversion
                min(roi / 100, 10) * 0.3  # 30% weight on revenue (capped at 10)
            )
            
            cursor.execute('''
                UPDATE affiliate_performance
                SET ctr = ?, conversion_rate = ?, roi = ?, performance_score = ?
                WHERE product_name = ?
            ''', (ctr, conversion_rate, roi, performance_score, product_name))
            
            conn.commit()
        
        conn.close()
    
    def get_best_products(self, topic, limit=3):
        """Get best performing products for a topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_name, performance_score, ctr, conversion_rate
            FROM affiliate_performance
            WHERE topic = ? AND status = 'active'
            ORDER BY performance_score DESC
            LIMIT ?
        ''', (topic, limit))
        
        products = cursor.fetchall()
        conn.close()
        
        return products
    
    def get_underperformers(self, min_impressions=50, min_score=2.0):
        """Identify underperforming products"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_name, impressions, performance_score, ctr, conversion_rate
            FROM affiliate_performance
            WHERE impressions >= ? AND performance_score < ? AND status = 'active'
            ORDER BY performance_score ASC
        ''', (min_impressions, min_score))
        
        underperformers = cursor.fetchall()
        conn.close()
        
        return underperformers
    
    def pause_product(self, product_name, reason="Low performance"):
        """Pause underperforming product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE affiliate_performance
            SET status = 'paused'
            WHERE product_name = ?
        ''', (product_name,))
        
        cursor.execute('''
            INSERT INTO affiliate_tests (product_name, test_end, result, notes)
            VALUES (?, ?, 'paused', ?)
        ''', (product_name, datetime.now(), reason))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Paused product: {product_name} - {reason}")
    
    def activate_product(self, product_name):
        """Reactivate a paused product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE affiliate_performance
            SET status = 'active'
            WHERE product_name = ?
        ''', (product_name,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Activated product: {product_name}")
    
    def get_performance_report(self, days=30):
        """Get comprehensive performance report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                product_name,
                topic,
                impressions,
                clicks,
                conversions,
                revenue,
                ctr,
                conversion_rate,
                performance_score,
                status
            FROM affiliate_performance
            WHERE last_used >= ?
            ORDER BY performance_score DESC
        ''', (cutoff_date,))
        
        report = cursor.fetchall()
        conn.close()
        
        return report
    
    def optimize_portfolio(self):
        """Automatically optimize affiliate product portfolio"""
        logger.info("Running affiliate portfolio optimization...")
        
        # Pause underperformers
        underperformers = self.get_underperformers(min_impressions=50, min_score=2.0)
        for product in underperformers:
            product_name = product[0]
            score = product[2]
            self.pause_product(product_name, f"Score {score:.2f} below threshold")
        
        # Get top performers
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_name, performance_score, revenue
            FROM affiliate_performance
            WHERE status = 'active'
            ORDER BY performance_score DESC
            LIMIT 10
        ''')
        
        top_performers = cursor.fetchall()
        conn.close()
        
        logger.info(f"Optimization complete: Paused {len(underperformers)} products")
        logger.info(f"Top performers: {[p[0] for p in top_performers[:3]]}")
        
        return {
            'paused': len(underperformers),
            'top_performers': top_performers
        }
    
    def get_recommendations(self, topic):
        """Get smart recommendations for which products to promote"""
        best_products = self.get_best_products(topic, limit=5)
        
        if not best_products:
            return {
                'strategy': 'test_new',
                'message': 'No performance data yet, test new products'
            }
        
        top_product = best_products[0]
        score = top_product[1]
        
        if score > 5.0:
            return {
                'strategy': 'double_down',
                'product': top_product[0],
                'message': f'High performer detected! Focus on {top_product[0]}'
            }
        elif score > 2.0:
            return {
                'strategy': 'continue',
                'product': top_product[0],
                'message': f'Moderate performance, continue testing'
            }
        else:
            return {
                'strategy': 'pivot',
                'message': 'Low performance, try different products'
            }

def optimize_affiliates():
    """Scheduled task to optimize affiliate portfolio"""
    optimizer = SmartAffiliateOptimizer()
    results = optimizer.optimize_portfolio()
    logger.info(f"Affiliate optimization results: {results}")
    return results

if __name__ == "__main__":
    # Test the optimizer
    optimizer = SmartAffiliateOptimizer()
    
    # Simulate some data
    optimizer.track_impression("DigitalOcean", "tech_news")
    optimizer.track_click("DigitalOcean")
    optimizer.track_conversion("DigitalOcean", 25.0)
    
    # Get report
    report = optimizer.get_performance_report(days=30)
    print("\nPerformance Report:")
    for row in report:
        print(f"{row[0]}: Score {row[8]:.2f}, CTR {row[6]:.2f}%, Conv {row[7]:.2f}%")
    
    # Get recommendations
    rec = optimizer.get_recommendations("tech_news")
    print(f"\nRecommendation: {rec}")
