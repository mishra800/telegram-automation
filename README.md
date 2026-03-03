# Telegram Content Automation System

AI-powered content generation and posting automation for Telegram channels with advanced monetization.

## Features

- **AI Content Generation**: Gemini Pro / Ollama with context-aware prompts
- **Multi-Format Content**: Images (gradient-based) and videos (MoviePy)
- **Trend Integration**: Real-time trending topics from Twitter, YouTube, Google Trends, Reddit
- **5-Stage Monetization Funnel**: Strategic affiliate placement for maximum conversion
- **Auto-Response System**: Professional FAQ handling with rate limiting
- **Growth Optimization**: Viral content detection, posting time optimization, audience fatigue tracking
- **Content Uniqueness**: Prevents repetition with 14-day memory and similarity detection
- **Analytics Dashboard**: Real-time performance tracking and insights
- **Automated Backups**: Daily database backups with integrity verification

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
GEMINI_API_KEY=your_gemini_key

# Optional
USE_GEMINI=true
GROWTH_MODE=true
POSTS_PER_DAY_HIGH=6
MIN_POST_INTERVAL_MINUTES=30
```

### 3. Run System

```bash
# Start automation
python main.py

# Post immediately
python main.py post-now

# Start auto-response
python main.py auto-response

# View statistics
python main.py stats
```

## Architecture

```
├── ai_engine/          # Content & media generation
│   ├── content_generator.py
│   ├── content_uniqueness.py
│   ├── image_generator.py
│   ├── video_generator.py
│   └── trend_analyzer.py
├── analytics/          # Performance tracking & optimization
│   ├── database.py
│   ├── collector.py
│   ├── posting_optimizer.py
│   ├── growth_accelerator.py
│   └── database_backup.py
├── bot/               # Core automation
│   ├── scheduler.py
│   ├── telegram_bot.py
│   ├── config.py
│   └── error_handler.py
├── monetization/      # Revenue optimization
│   ├── funnel_manager.py
│   ├── affiliate_manager.py
│   ├── revenue_tracker.py
│   └── viral_content.py
└── dashboard/         # Web interface
    └── app.py
```

## Deployment

### Render.com (Recommended)

1. Push to GitHub
2. Connect to Render.com
3. Configure environment variables
4. Deploy as Web Service

### Local/VPS

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

## Growth Strategy

**Phase 1 (0-1K followers)**: 15-20 posts/day, 70% trending topics
**Phase 2 (1K-10K followers)**: 8-12 posts/day, 60% trending topics
**Phase 3 (10K+ followers)**: 6-8 posts/day, focus on quality & monetization

## Monetization Funnel

1. **Viral Post** - Build awareness (no affiliate)
2. **Value Post** - Provide value (no affiliate)
3. **Authority Post** - Build trust (no affiliate)
4. **Soft Promotion** - Introduce solution (subtle affiliate)
5. **Strong CTA** - Drive conversion (strong affiliate)

## Monitoring

- Dashboard: `http://localhost:5000`
- Logs: `logs/YYYYMMDD.log`
- Databases: `analytics/*.db`
- Backups: `backups/*.backup`

## Key Metrics

- Follower growth rate
- Engagement rate (forwards + reactions / views)
- Content variety score
- Audience fatigue score
- Conversion rate by funnel stage
- Revenue per post

## Maintenance

- **Daily**: Automated backups at 4 AM
- **Weekly**: Posting optimization (Sunday 2 AM)
- **Weekly**: Content cleanup (Monday 2 AM)
- **Monthly**: Full system audit

## Support

For issues or questions, check logs in `logs/` directory.

## License

MIT License - See LICENSE file for details
