import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
    TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
    
    # Ollama
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    
    # Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    USE_GEMINI = os.getenv('USE_GEMINI', 'false').lower() == 'true'
    
    # Stable Diffusion
    SD_MODEL = os.getenv('SD_MODEL', 'stabilityai/stable-diffusion-2-1')
    USE_LOCAL_SD = os.getenv('USE_LOCAL_SD', 'true').lower() == 'true'
    
    # Scheduling
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')
    GROWTH_MODE = os.getenv('GROWTH_MODE', 'true').lower() == 'true'
    MIN_POST_INTERVAL_MINUTES = int(os.getenv('MIN_POST_INTERVAL_MINUTES', 30))
    
    # Dynamic posting frequency thresholds
    FOLLOWER_THRESHOLD_LOW = int(os.getenv('FOLLOWER_THRESHOLD_LOW', 1000))
    FOLLOWER_THRESHOLD_HIGH = int(os.getenv('FOLLOWER_THRESHOLD_HIGH', 10000))
    POSTS_PER_DAY_LOW = int(os.getenv('POSTS_PER_DAY_LOW', 18))
    POSTS_PER_DAY_MEDIUM = int(os.getenv('POSTS_PER_DAY_MEDIUM', 10))
    POSTS_PER_DAY_HIGH = int(os.getenv('POSTS_PER_DAY_HIGH', 6))
    
    # Analytics
    ANALYTICS_CHECK_DELAY = int(os.getenv('ANALYTICS_CHECK_DELAY', 24))
    
    # Dashboard
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 5000))
    DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    IMAGES_DIR = os.path.join(BASE_DIR, 'images')
    VIDEOS_DIR = os.path.join(BASE_DIR, 'videos')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    DB_PATH = os.path.join(BASE_DIR, 'analytics', 'analytics.db')
    
    # Content Topics
    TOPICS = [
        'motivational',
        'tech_news',
        'ai_updates',
        'data_science',
        'productivity'
    ]
    
    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not cls.TELEGRAM_CHANNEL_ID and not cls.TELEGRAM_GROUP_ID:
            raise ValueError("At least one of TELEGRAM_CHANNEL_ID or TELEGRAM_GROUP_ID is required")
        
        os.makedirs(cls.IMAGES_DIR, exist_ok=True)
        os.makedirs(cls.VIDEOS_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(cls.DB_PATH), exist_ok=True)
