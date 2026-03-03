import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, time, timedelta
from bot.config import Config
from bot.logger import setup_logger
from ai_engine.content_generator import ContentGenerator
from ai_engine.image_generator import ImageGenerator
from ai_engine.video_generator import VideoGenerator
from ai_engine.trend_analyzer import TrendAnalyzer
from bot.telegram_bot import post_content_sync, get_follower_count_sync
from analytics.database import AnalyticsDB
from analytics.collector import AnalyticsCollector
from monetization.viral_content import ViralContentEngine
from monetization.affiliate_manager import AffiliateManager
from monetization.engagement_tracker import EngagementTracker
from monetization.smart_affiliate import SmartAffiliateOptimizer
from monetization.funnel_manager import FunnelManager
from monetization.revenue_tracker import RevenueTracker
from bot.content_queue import ContentQueue
from analytics.ab_testing import ABTester
from ai_engine.content_uniqueness import ContentUniquenessChecker
from analytics.posting_optimizer import PostingOptimizer

logger = setup_logger(__name__)

class ContentScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=Config.TIMEZONE)
        self.content_gen = ContentGenerator()
        self.image_gen = ImageGenerator()
        self.video_gen = VideoGenerator()
        self.db = AnalyticsDB()
        self.collector = AnalyticsCollector()
        self.viral_engine = ViralContentEngine()
        self.affiliate_mgr = AffiliateManager()
        self.engagement_tracker = EngagementTracker()
        self.smart_affiliate = SmartAffiliateOptimizer()
        self.funnel_mgr = FunnelManager()
        self.revenue_tracker = RevenueTracker()
        self.content_queue = ContentQueue(min_queue_size=20)
        self.ab_tester = ABTester()
        self.trend_analyzer = TrendAnalyzer()
        self.uniqueness_checker = ContentUniquenessChecker()
        self.posting_optimizer = PostingOptimizer()
        self.current_follower_count = 0
        self.current_posts_per_day = Config.POSTS_PER_DAY_HIGH
        self.scheduled_job_ids = []
        self.use_queue = True  # Enable content queue by default
        self.video_percentage = 0.3  # 30% of posts should be videos
        
    def get_follower_count(self):
        """Get current follower count from Telegram"""
        try:
            count = get_follower_count_sync()
            self.current_follower_count = count
            logger.info(f"Current follower count: {count}")
            return count
        except Exception as e:
            logger.error(f"Error getting follower count: {e}")
            return self.current_follower_count
    
    def calculate_posts_per_day(self, follower_count):
        """Calculate posts per day based on follower count"""
        if not Config.GROWTH_MODE:
            return Config.POSTS_PER_DAY_HIGH
        
        if follower_count < Config.FOLLOWER_THRESHOLD_LOW:
            posts = Config.POSTS_PER_DAY_LOW
        elif follower_count < Config.FOLLOWER_THRESHOLD_HIGH:
            posts = Config.POSTS_PER_DAY_MEDIUM
        else:
            posts = Config.POSTS_PER_DAY_HIGH
        
        logger.info(f"Calculated {posts} posts/day for {follower_count} followers")
        return posts
    
    def generate_posting_schedule(self, posts_per_day):
        """Generate evenly spaced posting times for the day"""
        if posts_per_day <= 0:
            return []
        
        # Calculate interval in minutes
        total_minutes = 24 * 60
        interval_minutes = total_minutes // posts_per_day
        
        # Ensure minimum interval
        if interval_minutes < Config.MIN_POST_INTERVAL_MINUTES:
            interval_minutes = Config.MIN_POST_INTERVAL_MINUTES
            posts_per_day = total_minutes // interval_minutes
            logger.warning(f"Adjusted to {posts_per_day} posts/day due to minimum interval constraint")
        
        # Generate times starting from 6 AM
        start_hour = 6
        start_minute = 0
        
        posting_times = []
        current_minutes = start_hour * 60 + start_minute
        
        for i in range(posts_per_day):
            hour = (current_minutes // 60) % 24
            minute = current_minutes % 60
            posting_times.append((hour, minute))
            current_minutes += interval_minutes
        
        logger.info(f"Generated schedule: {posts_per_day} posts/day, interval: {interval_minutes} min")
        return posting_times
    
    def schedule_posts(self):
        """Schedule posts based on current follower count"""
        # Remove existing post jobs
        for job_id in self.scheduled_job_ids:
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass
        self.scheduled_job_ids = []
        
        # Get current follower count
        follower_count = self.get_follower_count()
        
        # Calculate posts per day
        posts_per_day = self.calculate_posts_per_day(follower_count)
        self.current_posts_per_day = posts_per_day
        
        # Generate posting schedule
        posting_times = self.generate_posting_schedule(posts_per_day)
        
        # Schedule each post
        for idx, (hour, minute) in enumerate(posting_times):
            job_id = f'post_{hour:02d}_{minute:02d}'
            self.scheduler.add_job(
                self.create_and_post,
                CronTrigger(hour=hour, minute=minute, timezone=Config.TIMEZONE),
                id=job_id,
                name=f'Post at {hour:02d}:{minute:02d}'
            )
            self.scheduled_job_ids.append(job_id)
            logger.info(f"Scheduled post #{idx+1} at {hour:02d}:{minute:02d}")
        
        logger.info(f"Total scheduled posts: {len(posting_times)}/day")
    
    def start(self):
        # Fill content queue on startup
        if self.use_queue:
            logger.info("Filling content queue...")
            self.content_queue.fill_queue(target_size=25)
            logger.info(f"Content queue ready: {self.content_queue.get_queue_size()} items")
        
        # Schedule initial posts based on follower count
        self.schedule_posts()
        
        # Schedule daily follower count check and reschedule (at 5 AM)
        self.scheduler.add_job(
            self.schedule_posts,
            CronTrigger(hour=5, minute=0, timezone=Config.TIMEZONE),
            id='reschedule_posts',
            name='Daily schedule adjustment'
        )
        logger.info("Scheduled daily schedule adjustment at 05:00")
        
        # Schedule stats collection
        self.scheduler.add_job(
            self.collector.collect_stats,
            CronTrigger(hour=2, minute=0, timezone=Config.TIMEZONE),
            id='collect_stats',
            name='Daily stats collection'
        )
        logger.info("Scheduled daily stats collection at 02:00")
        
        # Schedule weekly strategy adjustment
        self.scheduler.add_job(
            self.collector.analyze_and_adjust,
            CronTrigger(day_of_week='mon', hour=3, minute=0, timezone=Config.TIMEZONE),
            id='analyze_adjust',
            name='Weekly strategy adjustment'
        )
        logger.info("Scheduled weekly analysis every Monday at 03:00")
        
        # Schedule trend refresh (every 6 hours)
        self.scheduler.add_job(
            self.trend_analyzer.get_trending_topics,
            CronTrigger(hour='*/6', timezone=Config.TIMEZONE),
            id='refresh_trends',
            name='Trend refresh'
        )
        logger.info("Scheduled trend refresh every 6 hours")
        
        # Schedule content queue maintenance (daily at 4 AM)
        if self.use_queue:
            self.scheduler.add_job(
                self.content_queue.fill_queue,
                CronTrigger(hour=4, minute=0, timezone=Config.TIMEZONE),
                id='maintain_queue',
                name='Content queue maintenance'
            )
            logger.info("Scheduled content queue maintenance at 04:00")
        
        # Schedule affiliate optimization (weekly on Sunday at 1 AM)
        self.scheduler.add_job(
            self.smart_affiliate.optimize_portfolio,
            CronTrigger(day_of_week='sun', hour=1, minute=0, timezone=Config.TIMEZONE),
            id='optimize_affiliates',
            name='Affiliate optimization'
        )
        logger.info("Scheduled affiliate optimization every Sunday at 01:00")
        
        # Schedule A/B test analysis (daily at 3 AM)
        self.scheduler.add_job(
            self.ab_tester.auto_analyze_tests,
            CronTrigger(hour=3, minute=30, timezone=Config.TIMEZONE),
            id='analyze_ab_tests',
            name='A/B test analysis'
        )
        logger.info("Scheduled A/B test analysis at 03:30")
        
        # Schedule database backup (daily at 4 AM)
        from analytics.database_backup import DatabaseBackup
        backup_system = DatabaseBackup()
        self.scheduler.add_job(
            backup_system.backup_all_databases,
            CronTrigger(hour=4, minute=0, timezone=Config.TIMEZONE),
            id='backup_databases',
            name='Database backup'
        )
        logger.info("Scheduled database backup at 04:00")
        
        # Schedule growth tracking (daily at 11:59 PM)
        from analytics.growth_accelerator import GrowthAccelerator
        growth_accelerator = GrowthAccelerator()
        self.scheduler.add_job(
            lambda: growth_accelerator.track_daily_growth(
                self.current_follower_count,
                self.current_posts_per_day,
                0  # Will be calculated from actual data
            ),
            CronTrigger(hour=23, minute=59, timezone=Config.TIMEZONE),
            id='track_growth',
            name='Daily growth tracking'
        )
        logger.info("Scheduled daily growth tracking at 23:59")
        
        # Schedule content uniqueness cleanup (weekly on Monday at 2 AM)
        self.scheduler.add_job(
            self.uniqueness_checker.cleanup_old_content,
            CronTrigger(day_of_week='mon', hour=2, minute=0, timezone=Config.TIMEZONE),
            id='cleanup_content_history',
            name='Content history cleanup'
        )
        logger.info("Scheduled content history cleanup every Monday at 02:00")
        
        # Schedule posting optimization analysis (weekly on Sunday at 2 AM)
        self.scheduler.add_job(
            self.posting_optimizer.analyze_best_posting_times,
            CronTrigger(day_of_week='sun', hour=2, minute=0, timezone=Config.TIMEZONE),
            id='optimize_posting_times',
            name='Posting time optimization'
        )
        logger.info("Scheduled posting time optimization every Sunday at 02:00")
        
        self.scheduler.start()
        logger.info(f"Scheduler started successfully in {'GROWTH' if Config.GROWTH_MODE else 'NORMAL'} mode")
        logger.info(f"Current schedule: {self.current_posts_per_day} posts/day for {self.current_follower_count} followers")
        logger.info(f"Content queue: {'ENABLED' if self.use_queue else 'DISABLED'}")
    
    def create_and_post(self):
        try:
            logger.info("=" * 50)
            logger.info("Starting content creation and posting...")
            
            # Get current funnel stage
            funnel_state = self.funnel_mgr.get_current_stage()
            current_stage = funnel_state['stage']
            stage_guidelines = self.funnel_mgr.get_content_guidelines(current_stage)
            
            logger.info(f"Funnel Stage: {current_stage} (Cycle {funnel_state['cycle']})")
            logger.info(f"Stage Focus: {stage_guidelines['focus']}")
            
            topic = self._select_topic()
            logger.info(f"Selected topic: {topic}")
            
            # Try to get content from queue first
            if self.use_queue:
                queued_content = self.content_queue.get_next_content(topic)
                if queued_content:
                    logger.info("Using pre-generated content from queue")
                    content_text = queued_content['text']
                    image_path = queued_content['image_path']
                    content_type = queued_content['content_type']
                    
                    # Refill queue if running low
                    if self.content_queue.get_queue_size() < 10:
                        logger.info("Queue running low, triggering refill")
                        self.content_queue.fill_queue(target_size=20)
                else:
                    logger.warning("Queue empty, generating content on-demand")
                    queued_content = None
            else:
                queued_content = None
            
            # Generate content if not from queue
            affiliate_product = None  # Initialize for all paths
            
            if not queued_content:
                # Decide content type (regular or engagement post)
                import random
                is_engagement_post = random.random() < 0.2  # 20% engagement posts
                
                if is_engagement_post:
                    # Create viral engagement post
                    post_types = ['question', 'poll', 'challenge']
                    post_type = random.choice(post_types)
                    content_text = self.viral_engine.create_engagement_post(topic, post_type)
                    content_type = f'engagement_{post_type}'
                    logger.info(f"Created engagement post: {post_type}")
                else:
                    # Generate regular content with uniqueness check
                    max_attempts = 3
                    for attempt in range(max_attempts):
                        content = self.content_gen.generate_content(
                            topic, 
                            trending_keywords=self.trend_analyzer.get_trending_keywords_for_content(topic),
                            funnel_stage=current_stage
                        )
                        content_text = content['text']
                        
                        # Check uniqueness
                        if self.uniqueness_checker.is_content_unique(content_text, topic):
                            self.uniqueness_checker.save_content(content_text, topic)
                            logger.info(f"Unique content generated on attempt {attempt + 1}")
                            break
                        else:
                            logger.warning(f"Content too similar, regenerating (attempt {attempt + 1})")
                            if attempt == max_attempts - 1:
                                logger.warning("Using content despite similarity")
                    
                    content_type = 'regular'
                    
                    # Add trending keywords to content
                    trending_keywords = self.trend_analyzer.get_trending_keywords_for_content(topic)
                    if trending_keywords:
                        # Add trending keywords as hashtags
                        trending_tags = ' '.join([f'#{kw.replace(" ", "")}' for kw in trending_keywords])
                        content_text = content_text.rstrip() + f'\n\n🔥 Trending: {trending_tags}'
                        logger.info(f"Added trending keywords: {trending_keywords}")
                    
                    # Add viral elements
                    content_text = self.viral_engine.add_viral_elements(content_text, topic)
                    
                    # Add affiliate link based on funnel stage
                    has_affiliate = self.funnel_mgr.should_include_affiliate(current_stage)
                    
                    if has_affiliate:
                        # Get best performing products for this topic
                        best_products = self.smart_affiliate.get_best_products(topic, limit=3)
                        
                        if best_products:
                            # Use top performing product
                            product_name = best_products[0][0]
                            logger.info(f"Using top affiliate: {product_name} (score: {best_products[0][1]:.2f})")
                        
                        product = self.affiliate_mgr.get_affiliate_product(topic)
                        if product:
                            # Format CTA based on funnel stage (soft vs strong)
                            affiliate_cta = self.affiliate_mgr.format_affiliate_cta(product, current_stage)
                            content_text += affiliate_cta
                            affiliate_product = product['name']
                            
                            # Track impression
                            self.smart_affiliate.track_impression(product['name'], topic)
                            logger.info(f"Added {current_stage} affiliate: {product['name']}")
                
                logger.info("Content generated")
                
                # Decide whether to create video or image (30% video, 70% image)
                create_video = random.random() < self.video_percentage and self.video_gen.is_available()
                
                if create_video:
                    # Generate video
                    logger.info("Creating video content...")
                    media_path = self.video_gen.generate_video(topic, content_text)
                    media_type = 'video'
                    
                    if not media_path:
                        # Fallback to image if video generation fails
                        logger.warning("Video generation failed, falling back to image")
                        title = content_text.split('\n')[0][:50]
                        media_path = self.image_gen.generate_image(topic, title)
                        media_type = 'image'
                    else:
                        logger.info(f"Video generated: {media_path}")
                else:
                    # Generate image
                    title = content_text.split('\n')[0][:50]
                    media_path = self.image_gen.generate_image(topic, title)
                    media_type = 'image'
                    logger.info(f"Image generated: {media_path}")
            else:
                # From queue - always image for now
                media_type = 'image'
            
            results = post_content_sync(content_text, media_path, topic, media_type=media_type)
            
            for result in results:
                if result['success']:
                    post_id = self.db.save_post(
                        result['message_id'],
                        result['chat_id'],
                        result['topic'],
                        result['target_type']
                    )
                    
                    # Track content type for analytics
                    has_affiliate = affiliate_product is not None
                    self.engagement_tracker.track_post_performance(
                        post_id, topic, content_type, has_affiliate, 0, 0, 0
                    )
                    
                    # Track funnel post
                    self.funnel_mgr.track_post(
                        post_id, current_stage, topic, has_affiliate, affiliate_product
                    )
                    
                    # Track affiliate link if present
                    if has_affiliate and affiliate_product:
                        product = self.affiliate_mgr.get_affiliate_product(topic)
                        if product:
                            self.affiliate_mgr.track_affiliate_link(
                                post_id, product, topic, current_stage
                            )
                    
                    logger.info(
                        f"Posted successfully to {result['target_type']}: "
                        f"Message ID {result['message_id']} | Stage: {current_stage}"
                    )
                else:
                    logger.error(f"Failed to post to {result['target_type']}: {result.get('error')}")
            
            # Advance funnel stage after successful post
            next_stage = self.funnel_mgr.advance_stage()
            logger.info(f"Funnel advanced to: {next_stage}")
            
            logger.info("Content creation and posting completed")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Error in create_and_post: {e}", exc_info=True)
            
            # Try emergency content as last resort
            if self.use_queue:
                try:
                    logger.info("Attempting emergency content...")
                    emergency = self.content_queue.get_emergency_content(topic)
                    results = post_content_sync(emergency['text'], emergency['image_path'], topic)
                    logger.info("Emergency content posted successfully")
                except Exception as e2:
                    logger.error(f"Emergency content also failed: {e2}")
    
    def _select_topic(self):
        """
        Select topic with 60% trending, 40% regular weighted selection
        """
        weights = self.db.get_topic_weights()
        
        # Use trend analyzer for weighted selection
        selected = self.trend_analyzer.get_weighted_topic_selection(
            regular_topics=list(weights.keys()),
            regular_weights=weights
        )
        
        return selected
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def post_now(self, topic=None):
        if topic and topic not in Config.TOPICS:
            logger.error(f"Invalid topic: {topic}")
            return
        
        if topic:
            original_weights = self.db.get_topic_weights()
            temp_weights = {t: 0.0 for t in Config.TOPICS}
            temp_weights[topic] = 1.0
            
            for t, w in temp_weights.items():
                self.db.update_topic_weights([{
                    'topic': t,
                    'post_count': 0,
                    'total_views': 0,
                    'total_forwards': 0,
                    'avg_views': 0,
                    'avg_forwards': 0,
                    'engagement_score': w
                }])
        
        self.create_and_post()
        
        if topic:
            for t, w in original_weights.items():
                self.db.update_topic_weights([{
                    'topic': t,
                    'post_count': 0,
                    'total_views': 0,
                    'total_forwards': 0,
                    'avg_views': 0,
                    'avg_forwards': 0,
                    'engagement_score': w
                }])
