#!/usr/bin/env python3
"""
Deployment Verification Script
Checks all system components before deployment
"""

import sys
import os

def check_imports():
    """Verify all critical imports"""
    print("=" * 60)
    print("CHECKING IMPORTS")
    print("=" * 60)
    
    modules = [
        ('bot.config', 'Config'),
        ('bot.scheduler', 'ContentScheduler'),
        ('bot.telegram_bot', 'TelegramBot'),
        ('ai_engine.content_generator', 'ContentGenerator'),
        ('ai_engine.content_uniqueness', 'ContentUniquenessChecker'),
        ('ai_engine.image_generator', 'ImageGenerator'),
        ('ai_engine.video_generator', 'VideoGenerator'),
        ('ai_engine.trend_analyzer', 'TrendAnalyzer'),
        ('analytics.database', 'AnalyticsDB'),
        ('analytics.collector', 'AnalyticsCollector'),
        ('analytics.posting_optimizer', 'PostingOptimizer'),
        ('analytics.growth_accelerator', 'GrowthAccelerator'),
        ('analytics.database_backup', 'DatabaseBackup'),
        ('monetization.funnel_manager', 'FunnelManager'),
        ('monetization.affiliate_manager', 'AffiliateManager'),
        ('monetization.revenue_tracker', 'RevenueTracker'),
        ('monetization.viral_content', 'ViralContentEngine'),
        ('bot.error_handler', 'ErrorHandler'),
        ('dashboard.app', 'run_dashboard'),
    ]
    
    failed = []
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"✗ {module_name}.{class_name}: {e}")
            failed.append(module_name)
    
    if failed:
        print(f"\n❌ {len(failed)} imports failed")
        return False
    else:
        print(f"\n✅ All {len(modules)} imports successful")
        return True

def check_environment():
    """Check environment configuration"""
    print("\n" + "=" * 60)
    print("CHECKING ENVIRONMENT")
    print("=" * 60)
    
    from bot.config import Config
    
    required = [
        ('TELEGRAM_BOT_TOKEN', Config.TELEGRAM_BOT_TOKEN),
    ]
    
    optional = [
        ('TELEGRAM_CHANNEL_ID', Config.TELEGRAM_CHANNEL_ID),
        ('TELEGRAM_GROUP_ID', Config.TELEGRAM_GROUP_ID),
        ('GEMINI_API_KEY', Config.GEMINI_API_KEY),
        ('USE_GEMINI', Config.USE_GEMINI),
    ]
    
    missing = []
    for name, value in required:
        if not value:
            print(f"✗ {name}: MISSING (required)")
            missing.append(name)
        else:
            print(f"✓ {name}: configured")
    
    for name, value in optional:
        if not value:
            print(f"⚠ {name}: not set (optional)")
        else:
            print(f"✓ {name}: configured")
    
    if missing:
        print(f"\n❌ {len(missing)} required variables missing")
        return False
    else:
        print("\n✅ Environment configured")
        return True

def check_directories():
    """Check required directories"""
    print("\n" + "=" * 60)
    print("CHECKING DIRECTORIES")
    print("=" * 60)
    
    from bot.config import Config
    
    dirs = [
        Config.IMAGES_DIR,
        Config.VIDEOS_DIR,
        Config.LOGS_DIR,
        os.path.dirname(Config.DB_PATH),
        os.path.join(Config.BASE_DIR, 'backups'),
    ]
    
    for directory in dirs:
        if os.path.exists(directory):
            print(f"✓ {directory}")
        else:
            print(f"⚠ {directory} (will be created)")
            os.makedirs(directory, exist_ok=True)
    
    print("\n✅ All directories ready")
    return True

def check_databases():
    """Initialize and verify databases"""
    print("\n" + "=" * 60)
    print("CHECKING DATABASES")
    print("=" * 60)
    
    try:
        from analytics.database import AnalyticsDB
        from monetization.funnel_manager import FunnelManager
        from monetization.affiliate_manager import AffiliateManager
        from ai_engine.content_uniqueness import ContentUniquenessChecker
        from analytics.posting_optimizer import PostingOptimizer
        from analytics.growth_accelerator import GrowthAccelerator
        
        db = AnalyticsDB()
        print("✓ Analytics database initialized")
        
        funnel = FunnelManager()
        print("✓ Funnel database initialized")
        
        affiliate = AffiliateManager()
        print("✓ Affiliate database initialized")
        
        uniqueness = ContentUniquenessChecker()
        print("✓ Content uniqueness database initialized")
        
        optimizer = PostingOptimizer()
        print("✓ Posting optimizer database initialized")
        
        growth = GrowthAccelerator()
        print("✓ Growth accelerator database initialized")
        
        print("\n✅ All databases initialized")
        return True
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        return False

def check_system_health():
    """Overall system health check"""
    print("\n" + "=" * 60)
    print("SYSTEM HEALTH CHECK")
    print("=" * 60)
    
    checks = [
        ("Imports", check_imports),
        ("Environment", check_environment),
        ("Directories", check_directories),
        ("Databases", check_databases),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("🚀 SYSTEM READY FOR DEPLOYMENT")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Monitor: http://localhost:5000")
        print("3. Check logs: logs/")
        return 0
    else:
        print("\n" + "=" * 60)
        print("⚠️  SYSTEM NOT READY")
        print("=" * 60)
        print("\nFix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(check_system_health())
