# ⚡ Quick Start Guide

Get your Telegram automation running in 5 minutes!

## 🎯 Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] Ollama installed (https://ollama.ai)
- [ ] Telegram bot token from @BotFather
- [ ] Channel/Group ID where bot is admin

## 🚀 Installation (5 Steps)

### Step 1: Check Requirements
```bash
python check_requirements.py
```

### Step 2: Install Dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Install Ollama Model
```bash
ollama pull llama3
```

### Step 4: Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env with your details:
# - TELEGRAM_BOT_TOKEN (from @BotFather)
# - TELEGRAM_CHANNEL_ID (your @channel)
# - TELEGRAM_GROUP_ID (optional, -100xxxxx)
```

### Step 5: Test & Run
```bash
# Test everything
python test_system.py

# Start the system
python main.py
```

## 🎮 Quick Commands

```bash
# Start system (automated posting)
python main.py

# Post immediately
python main.py post-now

# Post specific topic
python main.py post-now motivational

# Test content generation
python main.py test-content

# View statistics
python main.py stats
```

## 📊 Access Dashboard

Open browser: **http://localhost:5000**

## 🔧 Common Issues

### "Ollama connection error"
```bash
# Start Ollama in separate terminal
ollama serve
```

### "Bot token invalid"
- Get new token from @BotFather
- Update TELEGRAM_BOT_TOKEN in .env

### "Can't post to channel"
- Make bot admin in channel
- Use correct format: @channelname

### "Module not found"
```bash
pip install -r requirements.txt
```

## 📁 What Gets Created

```
telegram-automation/
├── images/          # Generated images (auto-created)
├── logs/            # System logs (auto-created)
├── analytics/       # Database (auto-created)
│   └── analytics.db
└── [source files]
```

## ⚙️ Configuration Quick Reference

Edit `.env`:

```env
# Required
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHANNEL_ID=@mychannel

# Optional
TELEGRAM_GROUP_ID=-100123456789
POST_TIMES=09:00,14:00,20:00
OLLAMA_MODEL=llama3
```

## 🎯 Content Topics

Available topics for posting:
- `motivational` - Inspiring content
- `tech_news` - Technology updates
- `ai_updates` - AI industry news
- `data_science` - Data tips
- `productivity` - Efficiency hacks

## 📈 How It Works

1. **Scheduler** triggers at configured times
2. **AI** generates content using Ollama
3. **Image** created with Stable Diffusion or gradient
4. **Post** sent to Telegram channel/group
5. **Analytics** collected after 24 hours
6. **Strategy** adjusted weekly based on performance

## 🔄 Automation Schedule

Default posting times:
- 09:00 - Morning post
- 14:00 - Afternoon post
- 20:00 - Evening post

Analytics collection: Daily at 02:00
Strategy adjustment: Weekly on Monday at 03:00

## 💡 Pro Tips

1. **Start with gradients**: Set `USE_LOCAL_SD=false` for faster images
2. **Test first**: Use `python main.py post-now` to test before automation
3. **Monitor logs**: Check `logs/` directory for issues
4. **Adjust schedule**: Edit `POST_TIMES` in `.env` for your timezone
5. **Use smaller model**: Try `mistral` if `llama3` is slow

## 🆘 Need Help?

1. Check logs: `logs/YYYYMMDD.log`
2. Run tests: `python test_system.py`
3. Check requirements: `python check_requirements.py`
4. Read full guide: `SETUP.md`

## 🎉 Success Indicators

✓ Dashboard shows at http://localhost:5000
✓ Logs show "System is running!"
✓ First post appears in your channel
✓ No errors in logs

## 📝 Next Steps After Setup

1. Let it run for a week
2. Check dashboard for analytics
3. Best performing topics get more posts automatically
4. Customize content in `ai_engine/content_generator.py`
5. Adjust image styles in `ai_engine/image_generator.py`

---

**Ready to automate? Run: `python main.py`** 🚀
