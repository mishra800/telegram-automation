import random
from bot.logger import setup_logger

logger = setup_logger(__name__)

class AffiliateManager:
    """Manages affiliate links and product promotions"""
    
    def __init__(self):
        self.products = {
            'tech_news': [
                {
                    'name': 'DigitalOcean',
                    'description': 'Get $200 credit for cloud hosting',
                    'link': 'https://m.do.co/c/your-referral-code',
                    'cta': '🎁 Claim $200 Free Credit'
                },
                {
                    'name': 'Hostinger',
                    'description': 'Web hosting starting at $2.99/month',
                    'link': 'https://hostinger.com?ref=your-code',
                    'cta': '💰 Get 75% OFF Hosting'
                }
            ],
            'productivity': [
                {
                    'name': 'Notion',
                    'description': 'All-in-one workspace for notes and tasks',
                    'link': 'https://notion.so/your-affiliate',
                    'cta': '📝 Try Notion Free'
                },
                {
                    'name': 'Grammarly',
                    'description': 'AI-powered writing assistant',
                    'link': 'https://grammarly.com/your-ref',
                    'cta': '✍️ Write Better with AI'
                }
            ],
            'ai_updates': [
                {
                    'name': 'ChatGPT Plus',
                    'description': 'Upgrade to GPT-4 for advanced AI',
                    'link': 'https://chat.openai.com/your-ref',
                    'cta': '🤖 Upgrade to GPT-4'
                },
                {
                    'name': 'Midjourney',
                    'description': 'Create stunning AI images',
                    'link': 'https://midjourney.com/your-ref',
                    'cta': '🎨 Generate AI Art'
                }
            ],
            'data_science': [
                {
                    'name': 'DataCamp',
                    'description': 'Learn data science online',
                    'link': 'https://datacamp.com/your-ref',
                    'cta': '📊 Start Learning Free'
                },
                {
                    'name': 'Kaggle',
                    'description': 'Practice with real datasets',
                    'link': 'https://kaggle.com/your-ref',
                    'cta': '🏆 Join Competitions'
                }
            ],
            'motivational': [
                {
                    'name': 'Audible',
                    'description': 'Listen to motivational audiobooks',
                    'link': 'https://audible.com/your-ref',
                    'cta': '🎧 Get 2 Free Audiobooks'
                },
                {
                    'name': 'Skillshare',
                    'description': 'Learn new skills online',
                    'link': 'https://skillshare.com/your-ref',
                    'cta': '🎓 Get 30 Days Free'
                }
            ]
        }
        
        self.frequency = 0.3  # 30% of posts include affiliate
    
    def should_add_affiliate(self):
        """Decide if this post should include affiliate link"""
        return random.random() < self.frequency
    
    def get_affiliate_product(self, topic):
        """Get a relevant affiliate product for the topic"""
        products = self.products.get(topic, [])
        if not products:
            return None
        
        product = random.choice(products)
        logger.info(f"Selected affiliate product: {product['name']} for {topic}")
        return product
    
    def format_affiliate_cta(self, product):
        """Format affiliate CTA for post"""
        if not product:
            return ""
        
        cta = f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
        cta += f"💡 **Recommended Tool**\n\n"
        cta += f"**{product['name']}**\n"
        cta += f"{product['description']}\n\n"
        cta += f"👉 [{product['cta']}]({product['link']})\n"
        cta += f"━━━━━━━━━━━━━━━━━━━━"
        
        return cta
    
    def track_click(self, product_name, topic):
        """Track affiliate link clicks (for analytics)"""
        # This would integrate with your analytics database
        logger.info(f"Affiliate click tracked: {product_name} from {topic}")
