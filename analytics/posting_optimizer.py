"""
Posting Psychology Optimizer
Optimizes posting times, frequency, and patterns based on audience behavior
"""

import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class PostingOptimizer:
    """Optimize posting strategy based on audience psychology"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_optimizer_tables()
    
    def _init_optimizer_tables(self):
        """Initialize optimizer tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posting_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hour INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                avg_views REAL DEFAULT 0.0,
                avg_engagement REAL DEFAULT 0.0,
                post_count INTEGER DEFAULT 0,
                best_topics TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(hour, day_of_week)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audience_behavior (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                context TEXT,
                measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Posting optimizer tables initialized")
    
    def analyze_best_posting_times(self, days=30):
        """Analyze best posting times based on historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                CAST(strftime('%H', date) AS INTEGER) as hour,
                CAST(strftime('%w', date) AS INTEGER) as day_of_week,
                AVG(views) as avg_views,
                AVG(CAST(forwards + reactions AS REAL) / NULLIF(views, 0) * 100) as avg_engagement,
                COUNT(*) as post_count,
                GROUP_CONCAT(DISTINCT topic) as topics
            FROM posts
            WHERE date >= ? AND views > 0
            GROUP BY hour, day_of_week
            HAVING post_count >= 3
            ORDER BY avg_engagement DESC, avg_views DESC
        ''', (cutoff_date,))
        
        results = cursor.fetchall()
        
        # Update posting_patterns table
        for row in results:
            hour, day_of_week, avg_views, avg_engagement, post_count, topics = row
            
            cursor.execute('''
                INSERT INTO posting_patterns 
                (hour, day_of_week, avg_views, avg_engagement, post_count, best_topics, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(hour, day_of_week) DO UPDATE SET
                    avg_views = ?,
                    avg_engagement = ?,
                    post_count = ?,
                    best_topics = ?,
                    last_updated = CURRENT_TIMESTAMP
            ''', (hour, day_of_week, avg_views or 0, avg_engagement or 0, post_count, topics,
                  avg_views or 0, avg_engagement or 0, post_count, topics))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Analyzed {len(results)} posting time patterns")
        return results
    
    def get_optimal_posting_schedule(self, posts_per_day, current_day=None):
        """Get optimal posting schedule for a given day"""
        if current_day is None:
            current_day = datetime.now().weekday()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get best hours for this day of week
        cursor.execute('''
            SELECT hour, avg_engagement, avg_views
            FROM posting_patterns
            WHERE day_of_week = ?
            ORDER BY avg_engagement DESC, avg_views DESC
            LIMIT ?
        ''', (current_day, posts_per_day * 2))  # Get 2x to have options
        
        best_hours = cursor.fetchall()
        conn.close()
        
        if not best_hours:
            # Fallback to default schedule if no data
            return self._get_default_schedule(posts_per_day)
        
        # Select top hours ensuring minimum spacing
        selected_hours = []
        min_spacing = max(2, 24 // posts_per_day)  # At least 2 hours apart
        
        for hour, engagement, views in best_hours:
            if not selected_hours or all(abs(hour - h) >= min_spacing for h in selected_hours):
                selected_hours.append(hour)
                if len(selected_hours) >= posts_per_day:
                    break
        
        # Fill remaining slots if needed
        while len(selected_hours) < posts_per_day:
            for hour in range(6, 23):  # 6 AM to 11 PM
                if hour not in selected_hours:
                    if not selected_hours or all(abs(hour - h) >= min_spacing for h in selected_hours):
                        selected_hours.append(hour)
                        break
            break  # Avoid infinite loop
        
        selected_hours.sort()
        logger.info(f"Optimal schedule for day {current_day}: {selected_hours}")
        return selected_hours
    
    def _get_default_schedule(self, posts_per_day):
        """Get default posting schedule"""
        # Peak engagement times based on general social media research
        peak_hours = [7, 9, 12, 15, 18, 20, 21]
        
        if posts_per_day <= len(peak_hours):
            return peak_hours[:posts_per_day]
        
        # Distribute evenly if more posts needed
        interval = 24 // posts_per_day
        return [6 + (i * interval) for i in range(posts_per_day)]
    
    def calculate_audience_fatigue_score(self, days=7):
        """Calculate if audience is experiencing content fatigue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get engagement trend over time
        cursor.execute('''
            SELECT 
                DATE(date) as post_date,
                AVG(CAST(forwards + reactions AS REAL) / NULLIF(views, 0) * 100) as engagement_rate
            FROM posts
            WHERE date >= ? AND views > 0
            GROUP BY post_date
            ORDER BY post_date
        ''', (cutoff_date,))
        
        daily_engagement = cursor.fetchall()
        conn.close()
        
        if len(daily_engagement) < 3:
            return 0.0  # Not enough data
        
        # Calculate trend (negative = declining engagement = fatigue)
        engagements = [row[1] for row in daily_engagement if row[1] is not None]
        
        if len(engagements) < 3:
            return 0.0
        
        # Simple linear trend
        first_half_avg = sum(engagements[:len(engagements)//2]) / (len(engagements)//2)
        second_half_avg = sum(engagements[len(engagements)//2:]) / (len(engagements) - len(engagements)//2)
        
        if first_half_avg == 0:
            return 0.0
        
        trend = (second_half_avg - first_half_avg) / first_half_avg
        
        # Fatigue score: 0 = no fatigue, 1 = high fatigue
        fatigue_score = max(0, min(1, -trend))  # Negative trend = fatigue
        
        logger.info(f"Audience fatigue score: {fatigue_score:.2f}")
        return fatigue_score
    
    def recommend_posting_frequency(self, current_followers, current_posts_per_day):
        """Recommend optimal posting frequency"""
        fatigue_score = self.calculate_audience_fatigue_score()
        
        # Adjust based on fatigue
        if fatigue_score > 0.5:
            # High fatigue - reduce frequency
            recommended = max(3, current_posts_per_day - 2)
            reason = "High audience fatigue detected"
        elif fatigue_score > 0.3:
            # Moderate fatigue - slight reduction
            recommended = max(4, current_posts_per_day - 1)
            reason = "Moderate audience fatigue"
        else:
            # Low fatigue - can maintain or increase
            if current_followers < 1000:
                recommended = min(20, current_posts_per_day + 2)
                reason = "Growth phase - increase frequency"
            elif current_followers < 10000:
                recommended = current_posts_per_day
                reason = "Maintain current frequency"
            else:
                recommended = max(6, current_posts_per_day - 1)
                reason = "Large audience - focus on quality"
        
        logger.info(f"Frequency recommendation: {recommended} posts/day ({reason})")
        return {
            'recommended_posts_per_day': recommended,
            'reason': reason,
            'fatigue_score': fatigue_score
        }
    
    def get_content_mix_recommendation(self, days=14):
        """Recommend optimal content type mix"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Analyze performance by topic
        cursor.execute('''
            SELECT 
                topic,
                COUNT(*) as post_count,
                AVG(views) as avg_views,
                AVG(CAST(forwards + reactions AS REAL) / NULLIF(views, 0) * 100) as avg_engagement
            FROM posts
            WHERE date >= ? AND views > 0
            GROUP BY topic
            ORDER BY avg_engagement DESC, avg_views DESC
        ''', (cutoff_date,))
        
        topic_performance = cursor.fetchall()
        conn.close()
        
        if not topic_performance:
            return None
        
        total_posts = sum(row[1] for row in topic_performance)
        
        recommendations = []
        for topic, count, avg_views, avg_engagement in topic_performance:
            current_share = (count / total_posts * 100) if total_posts > 0 else 0
            
            # Recommend increasing share of high-performing topics
            if avg_engagement and avg_engagement > 5:  # Above 5% engagement
                recommended_share = min(35, current_share + 5)
            elif avg_engagement and avg_engagement > 3:
                recommended_share = current_share
            else:
                recommended_share = max(10, current_share - 5)
            
            recommendations.append({
                'topic': topic,
                'current_share': current_share,
                'recommended_share': recommended_share,
                'avg_engagement': avg_engagement or 0,
                'avg_views': avg_views or 0
            })
        
        logger.info(f"Content mix recommendations generated for {len(recommendations)} topics")
        return recommendations
