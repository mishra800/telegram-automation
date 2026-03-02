# 🤖 Telegram Content Automation System

**Zero-Budget AI-Powered Content Generation & Auto-Posting**

Automatically generate engaging content with AI, create beautiful images, post to Telegram, collect analytics, and optimize your content strategy — all without paid APIs.

## ✨ Features

- 🧠 **AI Content Generation** - Local LLM (Ollama/Llama3/Mistral)
- 🎨 **AI Image Generation** - Stable Diffusion or gradient fallback
- 📱 **Auto-Post to Telegram** - Channels and groups
- 📊 **Analytics Collection** - Views, forwards, reactions
- 🎯 **Smart Strategy Adjustment** - AI learns what works
- 📈 **Real-time Dashboard** - Beautiful web interface
- ⏰ **Flexible Scheduling** - Multiple posts per day
- 🔄 **Fully Automated** - Set it and forget it

## 🚀 Quick Start

### 1. Install Prerequisites
```bash
# Install Python 3.10+
# Install Ollama from https://ollama.ai
ollama pull llama3
```

### 2. Setup Project
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Telegram bot token and channel/group IDs
```

### 3. Run System
```bash
# Start Ollama (in separate terminal)
ollama serve

# Start automation system
python main.py
```

### 4. Access Dashboard
Open browser: http://localhost:5000

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AUTOMATION FLOW                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Scheduler → Generate Content → Generate Image →        │
│  Post to Telegram → Store Post ID → Collect Analytics → │
│  Analyze Performance → Adjust Strategy                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Components

1. **Content Generation Engine** (`ai_engine/content_generator.py`)
   - Uses local Ollama LLM
   - Generates 5 content types
   - Fallback content included

2. **Image Generation** (`ai_engine/image_generator.py`)
   - Stable Diffusion support
   - Gradient fallback
   - Text overlay with Pillow

3. **Telegram Bot** (`bot/telegram_bot.py`)
   - Auto-post with retry
   - Markdown formatting
   - Multi-target support

4. **Scheduler** (`bot/scheduler.py`)
   - APScheduler integration
   - Configurable times
   - Topic weight selection

5. **Analytics** (`analytics/`)
   - SQLite database
   - Stats collection
   - Performance analysis

6. **Dashboard** (`dashboard/`)
   - Flask web app
   - Real-time stats
   - Engagement charts

## 🎯 Content Topics

- **Motivational** - Inspiring quotes and advice
- **Tech News** - Latest technology trends
- **AI Updates** - AI industry developments
- **Data Science** - Tips and insights
- **Productivity** - Efficiency hacks

## 📊 Analytics & Optimization

### Automatic Collection
- Views, forwards, reactions tracked
- Data collected 24 hours after posting
- Stored in SQLite database

### Strategy Adjustment
- Weekly performance analysis
- Topic weights auto-adjusted
- Best performers get more posts

## 🎮 Commands

```bash
# Start system
python main.py

# Post immediately
python main.py post-now

# Post specific topic
python main.py post-now motivational

# Test content generation
python main.py test-content tech_news

# Test image generation
python main.py test-image ai_updates "AI Revolution"

# View statistics
python main.py stats

# Show help
python main.py help
```

## ⚙️ Configuration

Edit `.env` file:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
TELEGRAM_GROUP_ID=-100xxxxxxxxxx

# Ollama
OLLAMA_MODEL=llama3
OLLAMA_HOST=http://localhost:11434

# Scheduling
POST_TIMES=09:00,14:00,20:00
TIMEZONE=UTC

# Dashboard
DASHBOARD_PORT=5000
```

## 📁 Project Structure

```
telegram-automation/
├── bot/                    # Core bot functionality
│   ├── config.py          # Configuration management
│   ├── logger.py          # Logging system
│   ├── scheduler.py       # Post scheduling
│   └── telegram_bot.py    # Telegram API integration
├── ai_engine/             # AI content generation
│   ├── content_generator.py  # LLM content creation
│   └── image_generator.py    # Image generation
├── analytics/             # Analytics & database
│   ├── database.py        # SQLite operations
│   └── collector.py       # Stats collection
├── dashboard/             # Web dashboard
│   ├── app.py            # Flask application
│   └── templates/
│       └── dashboard.html
├── images/                # Generated images (auto-created)
├── logs/                  # System logs (auto-created)
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── SETUP.md             # Detailed setup guide
```

## 🔧 Customization

### Add New Topics
1. Edit `bot/config.py` - add to TOPICS list
2. Add prompts in `ai_engine/content_generator.py`
3. Add colors in `ai_engine/image_generator.py`

### Change Posting Schedule
Edit `.env`:
```env
POST_TIMES=06:00,12:00,18:00,22:00
```

### Modify Content Style
Edit prompts in `ai_engine/content_generator.py`

## 🐛 Troubleshooting

### Ollama Not Running
```bash
ollama serve
```

### Bot Can't Post
- Verify bot is admin in channel/group
- Check bot token is correct
- Ensure channel ID format: @channel or -100xxxxx

### Image Generation Slow
- Use gradient fallback (set USE_LOCAL_SD=false)
- Use smaller Ollama model (mistral)

## 📈 Performance

- **Content Generation**: 2-5 seconds
- **Image Generation**: 5-30 seconds (SD) or <1 second (gradient)
- **Posting**: 1-2 seconds
- **Memory Usage**: ~500MB (without SD) or ~4GB (with SD)

## 🔒 Security

- Never commit `.env` file
- Keep bot token secret
- Use `.gitignore` properly
- Regularly update dependencies

## 📝 Requirements

- Python 3.10+
- Ollama with llama3/mistral
- 2GB RAM minimum (8GB recommended for SD)
- Internet connection (for Telegram API only)

## 🎓 Learning Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Stable Diffusion](https://github.com/huggingface/diffusers)

## 🤝 Contributing

Feel free to fork, modify, and improve this system!

## 📄 License

Free to use for personal and commercial projects.

## 🌟 Features Roadmap

- [ ] Multi-language support
- [ ] Video generation
- [ ] Instagram integration
- [ ] Advanced A/B testing
- [ ] Custom ML models
- [ ] Voice message generation

---

**Built with ❤️ for content creators who want automation without breaking the bank**

For detailed setup instructions, see [SETUP.md](SETUP.md)
