"""
Growth Accelerator
Advanced strategies to maximize follower growth
"""

import sqlite3
import random
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class GrowthAccelerator:
    """Implements growth hacking strategies"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_growth_tables()
    
    def _init_growth_tables(self):
        """Initialize growth tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS growth_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                follower_count INTEGER NOT NULL,
                new_followers INTEGER DEFAULT 0,
                growth_rate REAL DEFAULT 0.0,
                posts_count INTEGER DEFAULT 0,
                avg_engagement REAL DEFAULT 0.0,
                viral_posts INTEGER DEFAULT 0,
                UNIQUE(date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS viral_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                views INTEGER NOT NULL,
                forwards INTEGER NOT NULL,
                virality_score REAL NOT NULL,
                content_preview TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS growth_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_name TEXT NOT NULL,
                strategy TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP,
                baseline_growth REAL,
                experiment_growth REAL,
                success BOOLEAN,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Growth accelerator tables initialized")
    
    def track_daily_growth(self, follower_count, posts_count, avg_engagement):
        """Track daily growth metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        # Get yesterday's count
        cursor.execute('''
            SELECT follower_count FROM growth_metrics
            WHERE date = date(?, '-1 day')
        ''', (today,))
        
        yesterday = cursor.fetchone()
        yesterday_count = yesterday[0] if yesterday else follower_count
        
        new_followers = follower_count - yesterday_count
        growth_rate = (new_followers / yesterday_count * 100) if yesterday_count > 0 else 0
        
        cursor.execute('''
            INSERT INTO growth_metrics 
            (date, follower_count, new_followers, growth_rate, posts_count, avg_engagement)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                follower_count = ?,
                new_followers = ?,
                growth_rate = ?,
                posts_count = ?,
                avg_engagement = ?
        ''', (today, follower_count, new_followers, growth_rate, posts_count, avg_engagement,
              follower_count, new_followers, growth_rate, posts_count, avg_engagement))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Growth tracked: {new_followers:+d} followers ({growth_rate:+.2f}%)")
        return {
            'new_followers': new_followers,
            'growth_rate': growth_rate
        }
    
    def identify_viral_posts(self, threshold_multiplier=3.0):
        """Identify posts that went viral"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate average performance
        cursor.execute('''
            SELECT AVG(views), AVG(forwards)
            FROM posts
            WHERE views > 0
        ''')
        
        avg_views, avg_forwards = cursor.fetchone()
        
        if not avg_views or not avg_forwards:
            conn.close()
            return []
        
        # Find posts exceeding threshold
        threshold_views = avg_views * threshold_multiplier
        threshold_forwards = avg_forwards * threshold_multiplier
        
        cursor.execute('''
            SELECT id, message_id, topic, views, forwards
            FROM posts
            WHERE views >= ? OR forwards >= ?
            ORDER BY (views + forwards * 2) DESC
            LIMIT 20
        ''', (threshold_views, threshold_forwards))
        
        viral_posts = cursor.fetchall()
        
        # Save to viral_posts table
        for post in viral_posts:
            post_id, message_id, topic, views, forwards = post
            virality_score = (views / avg_views) + (forwards / avg_forwards * 2)
            
            cursor.execute('''
                INSERT OR IGNORE INTO viral_posts 
                (post_id, topic, views, forwards, virality_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (post_id, topic, views, forwards, virality_score))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Identified {len(viral_posts)} viral posts")
        return viral_posts
    
    def get_viral_content_patterns(self):
        """Analyze patterns in viral content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                topic,
                COUNT(*) as viral_count,
                AVG(virality_score) as avg_virality,
                AVG(views) as avg_views,
                AVG(forwards) as avg_forwards
            FROM viral_posts
            GROUP BY topic
            ORDER BY viral_count DESC, avg_virality DESC
        ''')
        
        patterns = cursor.fetchall()
        conn.close()
        
        return [
            {
                'topic': row[0],
                'viral_count': row[1],
                'avg_virality': row[2],
                'avg_views': row[3],
                'avg_forwards': row[4]
            }
            for row in patterns
        ]
    
    def recommend_growth_strategy(self, current_followers, growth_rate):
        """Recommend growth strategy based on current metrics"""
        strategies = []
        
        # Strategy 1: Posting frequency
        if current_followers < 1000:
            if growth_rate < 5:
                strategies.append({
                    'strategy': 'increase_frequency',
                    'action': 'Increase posting to 15-20 posts/day',
                    'reason': 'Low follower count needs more visibility',
                    'priority': 'high'
                })
        
        # Strategy 2: Viral content focus
        viral_patterns = self.get_viral_content_patterns()
        if viral_patterns:
            top_viral_topic = viral_patterns[0]['topic']
            strategies.append({
                'strategy': 'focus_viral_topics',
                'action': f'Increase {top_viral_topic} content by 30%',
                'reason': f'{top_viral_topic} has highest viral potential',
                'priority': 'high'
            })
        
        # Strategy 3: Engagement optimization
        if growth_rate < 3:
            strategies.append({
                'strategy': 'boost_engagement',
                'action': 'Increase engagement posts (questions, polls) to 40%',
                'reason': 'Low growth rate indicates low engagement',
                'priority': 'medium'
            })
        
        # Strategy 4: Cross-promotion
        if current_followers > 500:
            strategies.append({
                'strategy': 'cross_promotion',
                'action': 'Add "Share with 3 friends" CTAs to top posts',
                'reason': 'Leverage existing audience for growth',
                'priority': 'medium'
            })
        
        # Strategy 5: Trend riding
        strategies.append({
            'strategy': 'trend_surfing',
            'action': 'Increase trending topic content to 70%',
            'reason': 'Trending content gets discovered more',
            'priority': 'high'
        })
        
        logger.info(f"Generated {len(strategies)} growth strategies")
        return strategies
    
    def calculate_growth_velocity(self, days=7):
        """Calculate growth velocity (acceleration)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        cursor.execute('''
            SELECT date, growth_rate
            FROM growth_metrics
            WHERE date >= ?
            ORDER BY date
        ''', (cutoff_date,))
        
        growth_data = cursor.fetchall()
        conn.close()
        
        if len(growth_data) < 2:
            return 0.0
        
        # Calculate velocity (change in growth rate)
        rates = [row[1] for row in growth_data]
        first_half = rates[:len(rates)//2]
        second_half = rates[len(rates)//2:]
        
        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0
        
        velocity = avg_second - avg_first
        
        logger.info(f"Growth velocity: {velocity:+.2f}% (acceleration)")
        return velocity
    
    def predict_follower_milestone(self, target_followers):
        """Predict when target follower count will be reached"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent growth data
        cursor.execute('''
            SELECT follower_count, growth_rate
            FROM growth_metrics
            WHERE date >= date('now', '-30 days')
            ORDER BY date DESC
            LIMIT 1
        ''')
        
        current_data = cursor.fetchone()
        
        if not current_data:
            conn.close()
            return None
        
        current_followers, avg_growth_rate = current_data
        
        # Get average daily growth
        cursor.execute('''
            SELECT AVG(new_followers)
            FROM growth_metrics
            WHERE date >= date('now', '-14 days')
        ''')
        
        avg_daily_growth = cursor.fetchone()[0] or 0
        conn.close()
        
        if avg_daily_growth <= 0:
            return None
        
        followers_needed = target_followers - current_followers
        days_to_target = followers_needed / avg_daily_growth
        
        target_date = datetime.now() + timedelta(days=days_to_target)
        
        logger.info(f"Predicted to reach {target_followers} followers in {days_to_target:.0f} days")
        
        return {
            'target_followers': target_followers,
            'current_followers': current_followers,
            'followers_needed': followers_needed,
            'days_to_target': int(days_to_target),
            'target_date': target_date.date(),
            'avg_daily_growth': avg_daily_growth
        }
    
    def get_growth_insights(self):
        """Get comprehensive growth insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current metrics
        cursor.execute('''
            SELECT follower_count, growth_rate, avg_engagement
            FROM growth_metrics
            ORDER BY date DESC
            LIMIT 1
        ''')
        
        current = cursor.fetchone()
        
        if not current:
            conn.close()
            return None
        
        current_followers, growth_rate, avg_engagement = current
        
        # Get 7-day trend
        cursor.execute('''
            SELECT AVG(growth_rate), AVG(avg_engagement)
            FROM growth_metrics
            WHERE date >= date('now', '-7 days')
        ''')
        
        week_avg = cursor.fetchone()
        conn.close()
        
        avg_growth_7d, avg_engagement_7d = week_avg if week_avg else (0, 0)
        
        velocity = self.calculate_growth_velocity()
        strategies = self.recommend_growth_strategy(current_followers, growth_rate)
        viral_patterns = self.get_viral_content_patterns()
        
        # Predictions
        milestones = []
        for target in [1000, 5000, 10000, 50000]:
            if target > current_followers:
                prediction = self.predict_follower_milestone(target)
                if prediction:
                    milestones.append(prediction)
        
        return {
            'current_followers': current_followers,
            'growth_rate': growth_rate,
            'avg_engagement': avg_engagement,
            'avg_growth_7d': avg_growth_7d,
            'avg_engagement_7d': avg_engagement_7d,
            'growth_velocity': velocity,
            'recommended_strategies': strategies,
            'viral_patterns': viral_patterns,
            'milestone_predictions': milestones
        }
