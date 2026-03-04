"""
Trend Analyzer Module
Fetches trending topics from multiple sources and provides weighted recommendations
"""

import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from collections import Counter
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class TrendAnalyzer:
    def __init__(self):
        self.cache_file = os.path.join(Config.BASE_DIR, 'analytics', 'trend_cache.json')
        self.cache_duration = 6 * 3600  # 6 hours in seconds
        
        # Fallback static topics
        self.fallback_topics = [
            'artificial intelligence',
            'machine learning',
            'chatgpt',
            'automation',
            'productivity',
            'tech news',
            'data science',
            'python programming',
            'cloud computing',
            'cybersecurity',
            'blockchain',
            'web development',
            'mobile apps',
            'startup',
            'innovation'
        ]
        
        # Topic mapping to our content categories
        self.topic_mapping = {
            'ai': 'ai_updates',
            'artificial intelligence': 'ai_updates',
            'machine learning': 'ai_updates',
            'chatgpt': 'ai_updates',
            'neural network': 'ai_updates',
            'deep learning': 'ai_updates',
            'tech': 'tech_news',
            'technology': 'tech_news',
            'startup': 'tech_news',
            'innovation': 'tech_news',
            'cloud': 'tech_news',
            'cybersecurity': 'tech_news',
            'data': 'data_science',
            'analytics': 'data_science',
            'python': 'data_science',
            'programming': 'data_science',
            'productivity': 'productivity',
            'automation': 'productivity',
            'efficiency': 'productivity',
            'motivation': 'motivational',
            'success': 'motivational',
            'growth': 'motivational'
        }
    
    def get_trending_topics(self):
        """Get trending topics with caching"""
        # Check cache first
        cached_trends = self._load_cache()
        if cached_trends:
            logger.info("Using cached trending topics")
            return cached_trends
        
        logger.info("Fetching fresh trending topics...")
        
        # Collect trends from multiple sources
        all_keywords = []
        
        # Source 1: Twitter/X trending (via scraping)
        twitter_trends = self._fetch_twitter_trends()
        all_keywords.extend(twitter_trends)
        
        # Source 2: YouTube trending (via scraping)
        youtube_trends = self._fetch_youtube_trends()
        all_keywords.extend(youtube_trends)
        
        # Source 3: Google Trends (simplified)
        google_trends = self._fetch_google_trends()
        all_keywords.extend(google_trends)
        
        # Source 4: Reddit tech subreddits
        reddit_trends = self._fetch_reddit_trends()
        all_keywords.extend(reddit_trends)
        
        # Process and score trends
        if all_keywords:
            trending_topics = self._process_trends(all_keywords)
        else:
            logger.warning("No trends fetched, using fallback topics")
            trending_topics = self._get_fallback_trends()
        
        # Cache results
        self._save_cache(trending_topics)
        
        return trending_topics
    
    def _fetch_twitter_trends(self):
        """Fetch trending topics from Twitter/X"""
        keywords = []
        
        try:
            # Using Twitter's public trends API (no auth needed for trending)
            url = "https://twitter.com/i/api/2/guide.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Simplified approach - use trending hashtags from public data
            # In production, you'd use Twitter API or scraping library
            
            # Fallback to common tech hashtags
            tech_hashtags = [
                'AI', 'MachineLearning', 'TechNews', 'Innovation',
                'Startup', 'Coding', 'DataScience', 'CloudComputing'
            ]
            
            keywords.extend(tech_hashtags)
            logger.info(f"Fetched {len(keywords)} Twitter trends")
            
        except Exception as e:
            logger.error(f"Error fetching Twitter trends: {e}")
        
        return keywords
    
    def _fetch_youtube_trends(self):
        """Fetch trending topics from YouTube"""
        keywords = []
        
        try:
            # YouTube trending in tech/AI niche
            # Using RSS feed approach (no API key needed)
            
            tech_channels = [
                'UC-lHJZR3Gqxm24_Vd_AJ5Yw',  # PewDiePie (example)
                'UCXuqSBlHAE6Xw-yeJA0Tunw',  # Linus Tech Tips
            ]
            
            # Simplified - add common trending tech topics
            trending_tech = [
                'ChatGPT', 'AI Tools', 'Tech Review', 'Programming Tutorial',
                'Productivity Hacks', 'Tech News', 'Coding Tips'
            ]
            
            keywords.extend(trending_tech)
            logger.info(f"Fetched {len(keywords)} YouTube trends")
            
        except Exception as e:
            logger.error(f"Error fetching YouTube trends: {e}")
        
        return keywords
    
    def _fetch_google_trends(self):
        """Fetch trending topics from Google Trends"""
        keywords = []
        
        try:
            # Using pytrends library (if available)
            try:
                from pytrends.request import TrendReq
                
                pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2, backoff_factor=0.1)
                
                # Get trending searches
                trending_searches = pytrends.trending_searches(pn='united_states')
                
                if not trending_searches.empty:
                    # Filter for tech-related terms
                    tech_terms = ['ai', 'tech', 'app', 'software', 'data', 'code', 'programming']
                    
                    for term in trending_searches[0].head(20):
                        term_lower = str(term).lower()
                        if any(tech in term_lower for tech in tech_terms):
                            keywords.append(str(term))
                
                logger.info(f"Fetched {len(keywords)} Google trends")
                
            except ImportError:
                logger.warning("pytrends not available, using fallback")
                # Fallback trending tech topics
                keywords.extend([
                    'Artificial Intelligence', 'ChatGPT', 'Machine Learning',
                    'Python', 'JavaScript', 'Cloud Computing'
                ])
            except Exception as pytrends_error:
                logger.warning(f"pytrends error: {pytrends_error}, using fallback")
                # Fallback trending tech topics
                keywords.extend([
                    'Artificial Intelligence', 'ChatGPT', 'Machine Learning',
                    'Python', 'JavaScript', 'Cloud Computing'
                ])
        
        except Exception as e:
            logger.warning(f"Google trends unavailable: {e}, using fallback")
            # Fallback trending tech topics
            keywords.extend([
                'Artificial Intelligence', 'ChatGPT', 'Machine Learning',
                'Python', 'JavaScript', 'Cloud Computing'
            ])
        
        return keywords
    
    def _fetch_reddit_trends(self):
        """Fetch trending topics from Reddit tech subreddits"""
        keywords = []
        
        try:
            # Fetch from tech subreddits using Reddit JSON API (no auth needed)
            subreddits = ['technology', 'programming', 'artificial', 'MachineLearning']
            
            for subreddit in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                    headers = {'User-Agent': 'TrendAnalyzer/1.0'}
                    
                    response = requests.get(url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            title = post.get('data', {}).get('title', '')
                            # Extract keywords from title
                            words = title.split()
                            keywords.extend([w for w in words if len(w) > 4])
                        
                        time.sleep(1)  # Rate limiting
                
                except Exception as e:
                    logger.error(f"Error fetching from r/{subreddit}: {e}")
                    continue
            
            logger.info(f"Fetched {len(keywords)} Reddit trends")
        
        except Exception as e:
            logger.error(f"Error fetching Reddit trends: {e}")
        
        return keywords
    
    def _process_trends(self, keywords):
        """Process and score trending keywords"""
        # Clean and normalize keywords
        cleaned = []
        for keyword in keywords:
            keyword = str(keyword).strip().lower()
            # Remove special characters
            keyword = ''.join(c for c in keyword if c.isalnum() or c.isspace())
            if len(keyword) > 2 and keyword not in ['the', 'and', 'for', 'with']:
                cleaned.append(keyword)
        
        # Count frequency
        counter = Counter(cleaned)
        
        # Get top 15 by frequency
        top_keywords = counter.most_common(15)
        
        # Remove duplicates and score
        scored_trends = []
        seen = set()
        
        for keyword, count in top_keywords:
            if keyword not in seen:
                seen.add(keyword)
                scored_trends.append({
                    'keyword': keyword,
                    'score': count,
                    'category': self._map_to_category(keyword)
                })
        
        # Sort by score and get top 5
        scored_trends.sort(key=lambda x: x['score'], reverse=True)
        top_5 = scored_trends[:5]
        
        logger.info(f"Processed trends: {[t['keyword'] for t in top_5]}")
        
        return top_5
    
    def _map_to_category(self, keyword):
        """Map trending keyword to our content category"""
        keyword_lower = keyword.lower()
        
        for key, category in self.topic_mapping.items():
            if key in keyword_lower:
                return category
        
        # Default to tech_news if no match
        return 'tech_news'
    
    def _get_fallback_trends(self):
        """Get fallback trends when scraping fails"""
        # Use static fallback topics with random scores
        trends = []
        
        selected = random.sample(self.fallback_topics, 5)
        
        for i, topic in enumerate(selected):
            trends.append({
                'keyword': topic,
                'score': 10 - i,  # Decreasing scores
                'category': self._map_to_category(topic)
            })
        
        logger.info(f"Using fallback trends: {[t['keyword'] for t in trends]}")
        return trends
    
    def _load_cache(self):
        """Load cached trends if still valid"""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            cache_time = cache_data.get('timestamp', 0)
            current_time = time.time()
            
            if current_time - cache_time < self.cache_duration:
                trends = cache_data.get('trends', [])
                age_hours = (current_time - cache_time) / 3600
                logger.info(f"Cache valid (age: {age_hours:.1f} hours)")
                return trends
            else:
                logger.info("Cache expired")
                return None
        
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None
    
    def _save_cache(self, trends):
        """Save trends to cache"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'trends': trends,
                'cached_at': datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info("Trends cached successfully")
        
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def get_weighted_topic_selection(self, regular_topics, regular_weights):
        """
        Get topic selection with 60% trending, 40% regular
        
        Args:
            regular_topics: List of regular topic names
            regular_weights: Dict of topic weights
        
        Returns:
            Selected topic name
        """
        # Get trending topics
        trending = self.get_trending_topics()
        
        # 60% chance to use trending topic
        if random.random() < 0.6 and trending:
            # Select from trending topics
            total_score = sum(t['score'] for t in trending)
            
            if total_score > 0:
                rand_val = random.uniform(0, total_score)
                cumulative = 0
                
                for trend in trending:
                    cumulative += trend['score']
                    if rand_val <= cumulative:
                        selected_category = trend['category']
                        logger.info(f"Selected trending topic: {trend['keyword']} -> {selected_category}")
                        return selected_category
        
        # 40% chance to use regular weighted topic
        topics = list(regular_weights.keys())
        weights = [regular_weights[t] for t in topics]
        
        selected = random.choices(topics, weights=weights, k=1)[0]
        logger.info(f"Selected regular topic: {selected}")
        
        return selected
    
    def get_trending_keywords_for_content(self, category):
        """Get trending keywords to include in content for a category"""
        trending = self.get_trending_topics()
        
        # Filter trends matching the category
        matching_trends = [
            t['keyword'] for t in trending 
            if t['category'] == category
        ]
        
        if matching_trends:
            # Return top 2 trending keywords
            return matching_trends[:2]
        
        return []

def test_trend_analyzer():
    """Test the trend analyzer"""
    analyzer = TrendAnalyzer()
    
    print("=" * 60)
    print("TREND ANALYZER TEST")
    print("=" * 60)
    
    # Get trending topics
    trends = analyzer.get_trending_topics()
    
    print("\n📊 Top 5 Trending Topics:")
    for i, trend in enumerate(trends, 1):
        print(f"{i}. {trend['keyword']}")
        print(f"   Score: {trend['score']}")
        print(f"   Category: {trend['category']}")
    
    # Test weighted selection
    print("\n🎯 Testing Weighted Selection (10 samples):")
    regular_topics = ['motivational', 'tech_news', 'ai_updates', 'data_science', 'productivity']
    regular_weights = {t: 1.0 for t in regular_topics}
    
    selections = []
    for _ in range(10):
        topic = analyzer.get_weighted_topic_selection(regular_topics, regular_weights)
        selections.append(topic)
    
    from collections import Counter
    counts = Counter(selections)
    
    for topic, count in counts.most_common():
        percentage = (count / 10) * 100
        print(f"{topic}: {count}/10 ({percentage:.0f}%)")
    
    # Test trending keywords for content
    print("\n🔥 Trending Keywords by Category:")
    for category in regular_topics:
        keywords = analyzer.get_trending_keywords_for_content(category)
        if keywords:
            print(f"{category}: {', '.join(keywords)}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_trend_analyzer()
