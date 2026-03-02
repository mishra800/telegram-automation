# Telegram Content Automation System - Setup Guide

## 🎯 Overview
A fully automated, zero-budget system for generating AI content, creating images, and auto-posting to Telegram with analytics and strategy adjustment.

## 📋 Prerequisites

### 1. Python 3.10+
```bash
python --version
```

### 2. Ollama (Local LLM)
Download and install from: https://ollama.ai

After installation, pull a model:
```bash
ollama pull llama3
# or
ollama pull mistral
```

### 3. Telegram Bot Token
1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Add your bot to your channel/group as admin

### 4. Get Channel/Group ID
For Channel:
- Your channel username (e.g., @mychannel)

For Group:
- Add @userinfobot to your group
- It will show the group ID (e.g., -100123456789)

## 🚀 Installation

### Step 1: Clone/Download Project
```bash
cd telegram-automation
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your details
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel
TELEGRAM_GROUP_ID=-100xxxxxxxxxx

OLLAMA_MODEL=llama3
OLLAMA_HOST=http://localhost:11434

POST_TIMES=09:00,14:00,20:00
TIMEZONE=UTC
```

### Step 5: Start Ollama
```bash
# Make sure Ollama is running
ollama serve
```

## 🎮 Usage

### Start the System
```bash
python main.py
```

This will:
- Start the content scheduler
- Launch the dashboard at http://localhost:5000
- Begin automated posting at scheduled times

### Manual Commands

#### Post Immediately
```bash
python main.py post-now
```

#### Post Specific Topic
```bash
python main.py post-now motivational
python main.py post-now tech_news
python main.py post-now ai_updates
```

#### Test Content Generation
```bash
python main.py test-content motivational
```

#### Test Image Generation
```bash
python main.py test-image tech_news "AI Revolution"
```

#### View Statistics
```bash
python main.py stats
```

#### Help
```bash
python main.py help
```

## 📊 Dashboard

Access the dashboard at: http://localhost:5000

Features:
- Total posts, views, and forwards
- Best performing topic
- Daily engagement chart
- Topic performance breakdown
- Auto-refresh every minute

## 🔧 Configuration

### Posting Schedule
Edit `POST_TIMES` in `.env`:
```env
POST_TIMES=09:00,14:00,20:00
```

### Topics
Available topics (in `bot/config.py`):
- motivational
- tech_news
- ai_updates
- data_science
- productivity

### Analytics
- Stats collected 24 hours after posting
- Weekly strategy adjustment every Monday at 3 AM
- Topic weights automatically adjusted based on engagement

## 🎨 Customization

### Add New Topics
1. Edit `bot/config.py` - add to `TOPICS` list
2. Edit `ai_engine/content_generator.py` - add prompt
3. Edit `ai_engine/image_generator.py` - add color scheme

### Change Image Style
Edit `ai_engine/image_generator.py`:
- Modify `prompts` dictionary for SD prompts
- Modify `colors` dictionary for gradient colors
- Adjust font size and positioning

### Adjust Posting Frequency
Edit `.env`:
```env
POST_TIMES=06:00,09:00,12:00,15:00,18:00,21:00
```

## 🐛 Troubleshooting

### Ollama Connection Error
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Telegram Bot Error
- Verify bot token is correct
- Ensure bot is admin in channel/group
- Check channel/group ID format

### Image Generation Issues
- If Stable Diffusion fails, system uses gradient fallback
- For GPU acceleration, ensure CUDA is installed
- Reduce image quality in `image_generator.py` if needed

### Database Issues
```bash
# Delete and recreate database
rm analytics/analytics.db
python main.py
```

## 📁 Project Structure
```
telegram-automation/
├── bot/
│   ├── config.py          # Configuration
│   ├── logger.py          # Logging setup
│   ├── scheduler.py       # Post scheduling
│   └── telegram_bot.py    # Telegram API
├── ai_engine/
│   ├── content_generator.py  # LLM content
│   └── image_generator.py    # Image creation
├── analytics/
│   ├── database.py        # SQLite operations
│   └── collector.py       # Stats collection
├── dashboard/
│   ├── app.py            # Flask dashboard
│   └── templates/
│       └── dashboard.html
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── .env                 # Configuration
```

## 🔒 Security Notes

- Never commit `.env` file
- Keep bot token secret
- Use environment variables in production
- Regularly update dependencies

## 📈 Performance Tips

1. **Ollama**: Use smaller models (mistral) for faster generation
2. **Images**: Disable SD and use gradients only for speed
3. **Scheduling**: Spread posts throughout the day
4. **Analytics**: Adjust collection frequency as needed

## 🆘 Support

Check logs in `logs/` directory for detailed error information.

## 📝 License

Free to use and modify for personal and commercial projects.
