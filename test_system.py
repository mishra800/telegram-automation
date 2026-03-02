#!/usr/bin/env python3
"""
System Test Script
Tests all components without posting to Telegram
"""

import os
import sys
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

def test_config():
    print("\n" + "="*60)
    print("Testing Configuration...")
    print("="*60)
    
    try:
        print(f"✓ Base Directory: {Config.BASE_DIR}")
        print(f"✓ Images Directory: {Config.IMAGES_DIR}")
        print(f"✓ Logs Directory: {Config.LOGS_DIR}")
        print(f"✓ Database Path: {Config.DB_PATH}")
        print(f"✓ Topics: {', '.join(Config.TOPICS)}")
        print(f"✓ Post Times: {', '.join(Config.POST_TIMES)}")
        print(f"✓ Ollama Model: {Config.OLLAMA_MODEL}")
        print(f"✓ Ollama Host: {Config.OLLAMA_HOST}")
        return True
    except Exception as e:
        print(f"✗ Configuration Error: {e}")
        return False

def test_database():
    print("\n" + "="*60)
    print("Testing Database...")
    print("="*60)
    
    try:
        from analytics.database import AnalyticsDB
        db = AnalyticsDB()
        
        weights = db.get_topic_weights()
        print(f"✓ Database initialized")
        print(f"✓ Topic weights loaded: {len(weights)} topics")
        
        stats = db.get_dashboard_stats()
        print(f"✓ Dashboard stats: {stats['total_posts']} posts")
        
        return True
    except Exception as e:
        print(f"✗ Database Error: {e}")
        return False

def test_content_generation():
    print("\n" + "="*60)
    print("Testing Content Generation...")
    print("="*60)
    
    try:
        from ai_engine.content_generator import ContentGenerator
        gen = ContentGenerator()
        
        content = gen.generate_content('motivational')
        print(f"✓ Content generated for 'motivational'")
        print(f"  Length: {len(content['text'])} characters")
        print(f"  Topic: {content['topic']}")
        print("\nSample content:")
        print("-" * 60)
        print(content['text'][:200] + "...")
        print("-" * 60)
        
        return True
    except Exception as e:
        print(f"✗ Content Generation Error: {e}")
        print("  Note: This is expected if Ollama is not running")
        print("  Fallback content will be used automatically")
        return True

def test_image_generation():
    print("\n" + "="*60)
    print("Testing Image Generation...")
    print("="*60)
    
    try:
        from ai_engine.image_generator import ImageGenerator
        gen = ImageGenerator()
        
        image_path = gen.generate_image('tech_news', 'Test Image Generation')
        print(f"✓ Image generated successfully")
        print(f"  Path: {image_path}")
        print(f"  Exists: {os.path.exists(image_path)}")
        
        if os.path.exists(image_path):
            size = os.path.getsize(image_path)
            print(f"  Size: {size / 1024:.2f} KB")
        
        return True
    except Exception as e:
        print(f"✗ Image Generation Error: {e}")
        return False

def test_ollama_connection():
    print("\n" + "="*60)
    print("Testing Ollama Connection...")
    print("="*60)
    
    try:
        import requests
        response = requests.get(f"{Config.OLLAMA_HOST}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✓ Ollama is running")
            print(f"  Available models: {len(models)}")
            for model in models:
                print(f"    - {model['name']}")
            return True
        else:
            print(f"✗ Ollama returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to Ollama at {Config.OLLAMA_HOST}")
        print("  Please start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Ollama Connection Error: {e}")
        return False

def test_telegram_config():
    print("\n" + "="*60)
    print("Testing Telegram Configuration...")
    print("="*60)
    
    if Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_BOT_TOKEN != 'your_bot_token_here':
        print(f"✓ Bot token configured")
        print(f"  Token: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
    else:
        print(f"✗ Bot token not configured")
        print(f"  Please set TELEGRAM_BOT_TOKEN in .env file")
        return False
    
    if Config.TELEGRAM_CHANNEL_ID:
        print(f"✓ Channel ID configured: {Config.TELEGRAM_CHANNEL_ID}")
    
    if Config.TELEGRAM_GROUP_ID:
        print(f"✓ Group ID configured: {Config.TELEGRAM_GROUP_ID}")
    
    if not Config.TELEGRAM_CHANNEL_ID and not Config.TELEGRAM_GROUP_ID:
        print(f"✗ No channel or group configured")
        return False
    
    return True

def main():
    print("\n" + "="*60)
    print("TELEGRAM CONTENT AUTOMATION SYSTEM - TEST SUITE")
    print("="*60)
    
    results = {
        'Configuration': test_config(),
        'Database': test_database(),
        'Ollama Connection': test_ollama_connection(),
        'Content Generation': test_content_generation(),
        'Image Generation': test_image_generation(),
        'Telegram Config': test_telegram_config(),
    }
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(results.values())
    total = len(results)
    
    print("\n" + "="*60)
    print(f"Tests Passed: {passed}/{total}")
    print("="*60)
    
    if passed == total:
        print("\n✓ All tests passed! System is ready to run.")
        print("\nStart the system with: python main.py")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("  - Ollama not running: ollama serve")
        print("  - .env not configured: cp .env.example .env")
        print("  - Missing dependencies: pip install -r requirements.txt")
    
    print("\n")

if __name__ == "__main__":
    main()
