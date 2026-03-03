import random
import sqlite3
from datetime import datetime
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class AffiliateManager:
    """Manages affiliate links and product promotions with funnel integration"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH.replace('analytics.db', 'affiliates.db')
        self._init_db()
        
        self.products = {
            'tech_news': [
                {
                    'name': 'DigitalOcean',
                    'description': 'Get $200 credit for cloud hosting',
                    'link': 'https://m.do.co/c/your-referral-code',
                    'cta': '🎁 Claim $200 Free Credit',
                    'commission_rate': 0.25
                },
                {
                    'name': 'Hostinger',
                    'description': 'Web hosting starting at $2.99/month',
                    'link': 'https://hostinger.com?ref=your-code',
                    'cta': '💰 Get 75% OFF Hosting',
                    'commission_rate': 0.30
                }
            ],
            'productivity': [
                {
                    'name': 'Notion',
                    'description': 'All-in-one workspace for notes and tasks',
                    'link': 'https://notion.so/your-affiliate',
                    'cta': '📝 Try Notion Free',
                    'commission_rate': 0.20
                },
                {
                    'name': 'Grammarly',
                    'description': 'AI-powered writing assistant',
                    'link': 'https://grammarly.com/your-ref',
                    'cta': '✍️ Write Better with AI',
                    'commission_rate': 0.20
                }
            ],
            'ai_updates': [
                {
                    'name': 'ChatGPT Plus',
                    'description': 'Upgrade to GPT-4 for advanced AI',
                    'link': 'https://chat.openai.com/your-ref',
                    'cta': '🤖 Upgrade to GPT-4',
                    'commission_rate': 0.15
                },
                {
                    'name': 'Midjourney',
                    'description': 'Create stunning AI images',
                    'link': 'https://midjourney.com/your-ref',
                    'cta': '🎨 Generate AI Art',
                    'commission_rate': 0.20
                }
            ],
            'data_science': [
                {
                    'name': 'DataCamp',
                    'description': 'Learn data science online',
                    'link': 'https://datacamp.com/your-ref',
                    'cta': '📊 Start Learning Free',
                    'commission_rate': 0.30
                },
                {
                    'name': 'Kaggle',
                    'description': 'Practice with real datasets',
                    'link': 'https://kaggle.com/your-ref',
                    'cta': '🏆 Join Competitions',
                    'commission_rate': 0.25
                }
            ],
            'motivational': [
                {
                    'name': 'Audible',
                    'description': 'Listen to motivational audiobooks',
                    'link': 'https://audible.com/your-ref',
                    'cta': '🎧 Get 2 Free Audiobooks',
                    'commission_rate': 0.10
                },
                {
                    'name': 'Skillshare',
                    'description': 'Learn new skills online',
                    'link': 'https://skillshare.com/your-ref',
                    'cta': '🎓 Get 30 Days Free',
                    'commission_rate': 0.25
                }
            ]
        }
    
    def _init_db(self):
        """Initialize affiliate tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                product_link TEXT NOT NULL,
                topic TEXT NOT NULL,
                funnel_stage TEXT NOT NULL,
                commission_rate REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id INTEGER NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (link_id) REFERENCES affiliate_links(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id INTEGER NOT NULL,
                conversion_value REAL NOT NULL,
                commission_earned REAL NOT NULL,
                converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (link_id) REFERENCES affiliate_links(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Affiliate manager database initialized")
    
    def should_add_affiliate(self, funnel_stage, engagement_rate=0):
        """Decide if affiliate should be added based on funnel stage and engagement"""
        # Only add affiliates in soft_promotion and strong_cta stages
        if funnel_stage not in ['soft_promotion', 'strong_cta']:
            return False
        
        # In soft_promotion, only add if engagement is decent
        if funnel_stage == 'soft_promotion':
            # 50% chance in soft stage, higher if engagement is good
            base_chance = 0.5
            if engagement_rate > 5:  # Above 5% engagement
                base_chance = 0.7
            return random.random() < base_chance
        
        # In strong_cta, always add affiliate
        return True
    
    def get_affiliate_product(self, topic):
        """Get a relevant affiliate product for the topic"""
        products = self.products.get(topic, [])
        if not products:
            return None
        
        product = random.choice(products)
        logger.info(f"Selected affiliate product: {product['name']} for {topic}")
        return product
    
    def format_affiliate_cta(self, product, funnel_stage):
        """Format affiliate CTA based on funnel stage"""
        if not product:
            return ""
        
        if funnel_stage == 'soft_promotion':
            # Subtle, helpful mention
            cta = f"\n\n💡 **Helpful Resource**\n\n"
            cta += f"Many in our community use **{product['name']}** for this.\n"
            cta += f"{product['description']}\n\n"
            cta += f"👉 [{product['cta']}]({product['link']})"
        
        elif funnel_stage == 'strong_cta':
            # Strong, direct promotion
            cta = f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
            cta += f"🎯 **RECOMMENDED SOLUTION**\n\n"
            cta += f"**{product['name']}**\n"
            cta += f"{product['description']}\n\n"
            cta += f"✨ **Why We Recommend It:**\n"
            cta += f"• Trusted by thousands\n"
            cta += f"• Easy to get started\n"
            cta += f"• Proven results\n\n"
            cta += f"👉 [{product['cta']}]({product['link']})\n"
            cta += f"━━━━━━━━━━━━━━━━━━━━"
        
        else:
            # Default format
            cta = f"\n\n💡 **Recommended Tool**\n\n"
            cta += f"**{product['name']}**\n"
            cta += f"{product['description']}\n\n"
            cta += f"👉 [{product['cta']}]({product['link']})"
        
        return cta
    
    def track_affiliate_link(self, post_id, product, topic, funnel_stage):
        """Track affiliate link creation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO affiliate_links 
            (post_id, product_name, product_link, topic, funnel_stage, commission_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (post_id, product['name'], product['link'], topic, funnel_stage, 
              product.get('commission_rate', 0.20)))
        
        link_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Affiliate link tracked: {product['name']} in {funnel_stage} stage")
        return link_id
    
    def track_click(self, link_id):
        """Track affiliate link click"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO affiliate_clicks (link_id)
            VALUES (?)
        ''', (link_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Affiliate click tracked for link {link_id}")
    
    def track_conversion(self, link_id, conversion_value):
        """Track affiliate conversion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get commission rate
        cursor.execute('''
            SELECT commission_rate FROM affiliate_links WHERE id = ?
        ''', (link_id,))
        
        result = cursor.fetchone()
        if not result:
            logger.error(f"Link {link_id} not found")
            return
        
        commission_rate = result[0]
        commission_earned = conversion_value * commission_rate
        
        cursor.execute('''
            INSERT INTO affiliate_conversions 
            (link_id, conversion_value, commission_earned)
            VALUES (?, ?, ?)
        ''', (link_id, conversion_value, commission_earned))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Conversion tracked: ${conversion_value} (${commission_earned} commission)")
    
    def get_conversion_stats(self, days=30):
        """Get affiliate conversion statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                al.product_name,
                al.funnel_stage,
                COUNT(DISTINCT al.id) as links_created,
                COUNT(DISTINCT ac.id) as clicks,
                COUNT(DISTINCT acv.id) as conversions,
                SUM(acv.conversion_value) as total_value,
                SUM(acv.commission_earned) as total_commission,
                CAST(COUNT(DISTINCT acv.id) AS REAL) / 
                    NULLIF(COUNT(DISTINCT ac.id), 0) * 100 as conversion_rate
            FROM affiliate_links al
            LEFT JOIN affiliate_clicks ac ON al.id = ac.link_id
            LEFT JOIN affiliate_conversions acv ON al.id = acv.link_id
            WHERE al.created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY al.product_name, al.funnel_stage
            ORDER BY total_commission DESC
        ''', (days,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'product': row[0],
                'stage': row[1],
                'links': row[2],
                'clicks': row[3],
                'conversions': row[4],
                'value': row[5] or 0.0,
                'commission': row[6] or 0.0,
                'conversion_rate': row[7] or 0.0
            }
            for row in results
        ]
    
    def get_revenue_per_post(self, post_id):
        """Get revenue generated by a specific post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(acv.commission_earned) as total_commission,
                COUNT(acv.id) as conversions
            FROM affiliate_links al
            JOIN affiliate_conversions acv ON al.id = acv.link_id
            WHERE al.post_id = ?
        ''', (post_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'commission': result[0] or 0.0,
                'conversions': result[1] or 0
            }
        
        return {'commission': 0.0, 'conversions': 0}
