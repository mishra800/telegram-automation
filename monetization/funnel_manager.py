"""
Funnel Manager - Strategic Content Funnel System
Implements 5-stage content cycle for optimal conversions
"""

import sqlite3
from datetime import datetime
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class FunnelManager:
    """
    Manages content funnel cycle:
    1. Viral Post - Build awareness
    2. Value Post - Provide value
    3. Authority Post - Build trust
    4. Soft Promotion - Introduce solution
    5. Strong CTA Post - Drive conversion
    """
    
    def __init__(self):
        self.db_path = Config.DB_PATH.replace('analytics.db', 'funnel.db')
        
        # Funnel stages - define before _init_db()
        self.stages = [
            'viral',           # Stage 1: Viral content for reach
            'value',           # Stage 2: Educational/valuable content
            'authority',       # Stage 3: Expertise demonstration
            'soft_promotion',  # Stage 4: Subtle product mention
            'strong_cta'       # Stage 5: Direct call-to-action
        ]
        
        self.current_stage_index = 0
        
        self._init_db()
    
    def _init_db(self):
        """Initialize funnel tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funnel_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_stage TEXT NOT NULL,
                stage_index INTEGER NOT NULL,
                cycle_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funnel_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                stage TEXT NOT NULL,
                topic TEXT NOT NULL,
                has_affiliate BOOLEAN DEFAULT 0,
                affiliate_product TEXT,
                views INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0.0,
                conversion_rate REAL DEFAULT 0.0,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                affiliate_product TEXT NOT NULL,
                conversion_value REAL NOT NULL,
                conversion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES funnel_posts(id)
            )
        ''')
        
        # Initialize funnel state if not exists
        cursor.execute('SELECT COUNT(*) FROM funnel_state')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO funnel_state (current_stage, stage_index, cycle_count)
                VALUES (?, ?, ?)
            ''', (self.stages[0], 0, 0))
        
        conn.commit()
        conn.close()
        logger.info("Funnel manager database initialized")
    
    def get_current_stage(self):
        """Get current funnel stage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT current_stage, stage_index, cycle_count
            FROM funnel_state
            ORDER BY id DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'stage': result[0],
                'index': result[1],
                'cycle': result[2]
            }
        
        return {
            'stage': self.stages[0],
            'index': 0,
            'cycle': 0
        }
    
    def advance_stage(self):
        """Move to next stage in funnel"""
        current = self.get_current_stage()
        next_index = (current['index'] + 1) % len(self.stages)
        next_stage = self.stages[next_index]
        
        # Increment cycle count when completing full cycle
        cycle_count = current['cycle']
        if next_index == 0:
            cycle_count += 1
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO funnel_state (current_stage, stage_index, cycle_count)
            VALUES (?, ?, ?)
        ''', (next_stage, next_index, cycle_count))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Funnel advanced: {current['stage']} -> {next_stage} (Cycle {cycle_count})")
        
        return next_stage
    
    def should_include_affiliate(self, stage):
        """Determine if affiliate should be included based on stage"""
        # Only include affiliates in soft_promotion and strong_cta stages
        return stage in ['soft_promotion', 'strong_cta']
    
    def get_affiliate_intensity(self, stage):
        """Get affiliate promotion intensity for stage"""
        intensities = {
            'viral': 0.0,           # No affiliate
            'value': 0.0,           # No affiliate
            'authority': 0.0,       # No affiliate
            'soft_promotion': 0.5,  # Subtle mention
            'strong_cta': 1.0       # Strong promotion
        }
        return intensities.get(stage, 0.0)
    
    def get_content_guidelines(self, stage):
        """Get content creation guidelines for current stage"""
        guidelines = {
            'viral': {
                'focus': 'Engagement and reach',
                'style': 'Entertaining, shareable, emotional',
                'cta': 'Share, tag, comment',
                'affiliate': False,
                'tone': 'Casual, fun, relatable'
            },
            'value': {
                'focus': 'Education and value delivery',
                'style': 'Informative, practical, actionable',
                'cta': 'Save, bookmark, learn more',
                'affiliate': False,
                'tone': 'Helpful, expert, clear'
            },
            'authority': {
                'focus': 'Credibility and expertise',
                'style': 'Data-driven, case studies, insights',
                'cta': 'Follow for more insights',
                'affiliate': False,
                'tone': 'Professional, authoritative, trustworthy'
            },
            'soft_promotion': {
                'focus': 'Problem awareness and solution hint',
                'style': 'Story-based, relatable problem',
                'cta': 'Learn about solution',
                'affiliate': True,
                'tone': 'Conversational, helpful, non-pushy'
            },
            'strong_cta': {
                'focus': 'Direct conversion',
                'style': 'Benefits-focused, urgency, social proof',
                'cta': 'Get started now, claim offer',
                'affiliate': True,
                'tone': 'Confident, persuasive, action-oriented'
            }
        }
        return guidelines.get(stage, guidelines['value'])
    
    def track_post(self, post_id, stage, topic, has_affiliate=False, affiliate_product=None):
        """Track funnel post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO funnel_posts 
            (post_id, stage, topic, has_affiliate, affiliate_product)
            VALUES (?, ?, ?, ?, ?)
        ''', (post_id, stage, topic, has_affiliate, affiliate_product))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Funnel post tracked: Stage={stage}, Affiliate={has_affiliate}")
    
    def update_post_metrics(self, post_id, views=None, clicks=None, conversions=None, revenue=None):
        """Update post performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if views is not None:
            updates.append("views = ?")
            params.append(views)
        
        if clicks is not None:
            updates.append("clicks = ?")
            params.append(clicks)
        
        if conversions is not None:
            updates.append("conversions = ?")
            params.append(conversions)
        
        if revenue is not None:
            updates.append("revenue = ?")
            params.append(revenue)
        
        # Calculate conversion rate
        if clicks is not None and conversions is not None and clicks > 0:
            conversion_rate = (conversions / clicks) * 100
            updates.append("conversion_rate = ?")
            params.append(conversion_rate)
        
        if updates:
            params.append(post_id)
            query = f"UPDATE funnel_posts SET {', '.join(updates)} WHERE post_id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def track_conversion(self, post_id, affiliate_product, conversion_value):
        """Track affiliate conversion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO affiliate_conversions 
            (post_id, affiliate_product, conversion_value)
            VALUES (?, ?, ?)
        ''', (post_id, affiliate_product, conversion_value))
        
        # Update post revenue
        cursor.execute('''
            UPDATE funnel_posts
            SET revenue = revenue + ?,
                conversions = conversions + 1
            WHERE post_id = ?
        ''', (conversion_value, post_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Conversion tracked: ${conversion_value} from {affiliate_product}")
    
    def get_stage_performance(self, days=30):
        """Get performance metrics by funnel stage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                stage,
                COUNT(*) as post_count,
                SUM(views) as total_views,
                SUM(clicks) as total_clicks,
                SUM(conversions) as total_conversions,
                SUM(revenue) as total_revenue,
                AVG(conversion_rate) as avg_conversion_rate
            FROM funnel_posts
            WHERE posted_at >= datetime('now', '-' || ? || ' days')
            GROUP BY stage
            ORDER BY 
                CASE stage
                    WHEN 'viral' THEN 1
                    WHEN 'value' THEN 2
                    WHEN 'authority' THEN 3
                    WHEN 'soft_promotion' THEN 4
                    WHEN 'strong_cta' THEN 5
                END
        ''', (days,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'stage': row[0],
                'posts': row[1],
                'views': row[2] or 0,
                'clicks': row[3] or 0,
                'conversions': row[4] or 0,
                'revenue': row[5] or 0.0,
                'conversion_rate': row[6] or 0.0
            }
            for row in results
        ]
    
    def get_funnel_health(self):
        """Get overall funnel health metrics"""
        performance = self.get_stage_performance(days=30)
        
        if not performance:
            return {
                'status': 'no_data',
                'message': 'Not enough data to assess funnel health'
            }
        
        # Calculate funnel metrics
        total_views = sum(p['views'] for p in performance)
        total_revenue = sum(p['revenue'] for p in performance)
        total_conversions = sum(p['conversions'] for p in performance)
        
        # Check if all stages are represented
        stages_used = set(p['stage'] for p in performance)
        all_stages_active = len(stages_used) == len(self.stages)
        
        # Calculate conversion funnel
        viral_views = next((p['views'] for p in performance if p['stage'] == 'viral'), 0)
        cta_conversions = next((p['conversions'] for p in performance if p['stage'] == 'strong_cta'), 0)
        
        funnel_conversion = (cta_conversions / viral_views * 100) if viral_views > 0 else 0
        
        return {
            'status': 'healthy' if all_stages_active else 'incomplete',
            'total_views': total_views,
            'total_revenue': total_revenue,
            'total_conversions': total_conversions,
            'funnel_conversion_rate': funnel_conversion,
            'stages_active': len(stages_used),
            'stages_total': len(self.stages),
            'performance_by_stage': performance
        }

def test_funnel_manager():
    """Test funnel manager"""
    print("=" * 60)
    print("FUNNEL MANAGER TEST")
    print("=" * 60)
    
    manager = FunnelManager()
    
    print("\n✅ Funnel manager initialized")
    print(f"   Stages: {len(manager.stages)}")
    print(f"   Database: {manager.db_path}")
    
    print("\n📊 Funnel Stages:")
    for i, stage in enumerate(manager.stages, 1):
        guidelines = manager.get_content_guidelines(stage)
        print(f"\n{i}. {stage.upper()}")
        print(f"   Focus: {guidelines['focus']}")
        print(f"   Affiliate: {guidelines['affiliate']}")
        print(f"   Tone: {guidelines['tone']}")
    
    print("\n🔄 Testing Stage Progression:")
    for i in range(7):
        current = manager.get_current_stage()
        print(f"   {i+1}. Stage: {current['stage']} (Cycle {current['cycle']})")
        manager.advance_stage()
    
    print("\n" + "=" * 60)
    print("✅ Funnel manager ready!")
    print("=" * 60)

if __name__ == "__main__":
    test_funnel_manager()
