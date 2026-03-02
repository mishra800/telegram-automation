# 🚀 GET STARTED - Complete Guide

## 📋 What You're About to Build

A fully automated system that:
- Generates AI content every day
- Creates beautiful images automatically
- Posts to your Telegram channel/group
- Tracks performance analytics
- Optimizes content strategy based on data
- All without spending a penny!

## ⏱️ Time Required

- **First-time setup**: 10-15 minutes
- **If you have Ollama**: 5 minutes
- **Daily maintenance**: 0 minutes (fully automated!)

## 📦 Step-by-Step Installation

### Step 1: Install Python (if needed)

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

**Mac:**
```bash
brew install python@3.10
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.10 python3-pip
```

**Verify:**
```bash
python --version
# Should show: Python 3.10.x or higher
```

### Step 2: Install Ollama

**All Platforms:**
1. Go to https://ollama.ai
2. Download for your OS
3. Install the application
4. Open terminal and run:

```bash
ollama pull llama3
```

This downloads the AI model (about 4GB). Wait for it to complete.

**Verify:**
```bash
ollama list
# Should show: llama3
```

### Step 3: Create Telegram Bot

1. Open Telegram
2. Search for `@BotFather`
3. Send: `/newbot`
4. Follow instructions:
   - Choose a name: "My Content Bot"
   - Choose username: "my_content_bot" (must end in 'bot')
5. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 4: Setup Your Channel/Group

**For Channel:**
1. Create a channel in Telegram
2. Make it public (or keep private)
3. Add your bot as administrator:
   - Channel Settings → Administrators → Add Administrator
   - Search for your bot username
   - Give "Post Messages" permission
4. Note your channel username (e.g., `@mychannel`)

**For Group:**
1. Create a group in Telegram
2. Add your bot to the group
3. Make bot an admin
4. Get group ID:
   - Add `@userinfobot` to your group
   - It will show the group ID (e.g., `-100123456789`)

### Step 5: Setup Project

**Windows:**
```bash
# Navigate to project folder
cd telegram-automation

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
# Navigate to project folder
cd telegram-automation

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env file
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Edit these values:**
```env
TELEGRAM_BOT_TOKEN=paste_your_token_here
TELEGRAM_CHANNEL_ID=@yourchannel
TELEGRAM_GROUP_ID=-100xxxxxxxxxx

OLLAMA_MODEL=llama3
POST_TIMES=09:00,14:00,20:00
```

**Save and close the file.**

### Step 7: Test Everything

```bash
# Check requirements
python check_requirements.py

# Test the system
python test_system.py
```

If all tests pass, you're ready!

### Step 8: Start the System

**Option 1: Using startup script**

Windows:
```bash
start.bat
```

Mac/Linux:
```bash
./start.sh
```

**Option 2: Manual start**

```bash
# Make sure Ollama is running (separate terminal)
ollama serve

# Start the automation system
python main.py
```

### Step 9: Access Dashboard

Open your browser:
```
http://localhost:5000
```

You should see your dashboard with stats!

### Step 10: Test Manual Post

In another terminal (keep main.py running):

```bash
# Activate venv first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Post immediately
python main.py post-now
```

Check your Telegram channel - you should see a post!

## ✅ Success Checklist

- [ ] Python 3.10+ installed
- [ ] Ollama installed and llama3 model downloaded
- [ ] Telegram bot created
- [ ] Bot added as admin to channel/group
- [ ] .env file configured
- [ ] Dependencies installed
- [ ] Tests passed
- [ ] System started
- [ ] Dashboard accessible
- [ ] Test post successful

## 🎮 Daily Usage

### Automated Mode (Recommended)

Just leave it running! The system will:
- Post 3 times per day (09:00, 14:00, 20:00)
- Collect analytics daily
- Adjust strategy weekly

### Manual Mode

```bash
# Post now
python main.py post-now

# Post specific topic
python main.py post-now motivational
python main.py post-now tech_news
python main.py post-now ai_updates
python main.py post-now data_science
python main.py post-now productivity

# View stats
python main.py stats

# Test content
python main.py test-content motivational
```

## 📊 Understanding the Dashboard

**Total Posts**: Number of posts created
**Total Views**: Combined views across all posts
**Total Forwards**: How many times posts were shared
**Best Topic**: Which topic performs best

**Engagement Chart**: Daily views over last 30 days
**Topic Performance**: Breakdown by topic with scores

## ⚙️ Customization

### Change Posting Times

Edit `.env`:
```env
POST_TIMES=06:00,12:00,18:00,22:00
```

### Change Timezone

Edit `.env`:
```env
TIMEZONE=America/New_York
# or
TIMEZONE=Europe/London
# or
TIMEZONE=Asia/Tokyo
```

### Disable Image Generation (Faster)

Edit `.env`:
```env
USE_LOCAL_SD=false
```

This uses gradient images instead of Stable Diffusion (much faster).

### Use Different Model

Edit `.env`:
```env
OLLAMA_MODEL=mistral
```

Then download it:
```bash
ollama pull mistral
```

## 🐛 Troubleshooting

### "Ollama connection error"

**Solution:**
```bash
# Start Ollama in separate terminal
ollama serve
```

### "Bot token invalid"

**Solution:**
1. Check token in .env has no spaces
2. Get new token from @BotFather
3. Update .env file

### "Can't post to channel"

**Solution:**
1. Verify bot is admin in channel
2. Check channel ID format:
   - Public: `@channelname`
   - Private: `-100xxxxxxxxxx`
3. Ensure bot has "Post Messages" permission

### "Module not found"

**Solution:**
```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall
pip install -r requirements.txt
```

### "Permission denied" (Linux/Mac)

**Solution:**
```bash
chmod +x start.sh
./start.sh
```

### Images not generating

**Solution:**
1. Set `USE_LOCAL_SD=false` in .env (uses gradients)
2. Or install CUDA for GPU acceleration
3. Or wait longer (SD takes 10-30 seconds)

### Dashboard not loading

**Solution:**
1. Check if port 5000 is available
2. Change port in .env:
   ```env
   DASHBOARD_PORT=8080
   ```
3. Access at http://localhost:8080

## 📈 Optimization Tips

### For Speed
- Use `mistral` model (smaller, faster)
- Set `USE_LOCAL_SD=false` (gradient images)
- Reduce posting frequency

### For Quality
- Use `llama3` model (better content)
- Enable Stable Diffusion
- Increase posting frequency for more data

### For Analytics
- Let it run for at least 1 week
- Check dashboard regularly
- Adjust based on best performing topics

## 🔒 Security Best Practices

1. **Never commit .env file**
   - Already in .gitignore
   - Contains sensitive tokens

2. **Keep bot token secret**
   - Don't share in screenshots
   - Regenerate if exposed

3. **Regular updates**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 📱 Running 24/7

### On Your Computer

**Windows:**
- Disable sleep mode
- Keep terminal open
- Or use Task Scheduler

**Mac/Linux:**
- Use `screen` or `tmux`
- Or create systemd service

### On a Server

**VPS (Recommended):**
1. Get cheap VPS ($5/month)
2. Install Python + Ollama
3. Clone project
4. Run with systemd or screen

**Example systemd service:**
```ini
[Unit]
Description=Telegram Automation
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/telegram-automation
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🎓 Learning Resources

- **Ollama**: https://ollama.ai/docs
- **Telegram Bots**: https://core.telegram.org/bots
- **Python**: https://docs.python.org/3/
- **Flask**: https://flask.palletsprojects.com/

## 🆘 Getting Help

1. **Check logs**: `logs/YYYYMMDD.log`
2. **Run tests**: `python test_system.py`
3. **Check requirements**: `python check_requirements.py`
4. **Read docs**: All .md files in project

## 🎉 You're Done!

Your automation system is now running!

**What happens next:**
1. System posts at scheduled times
2. Analytics collected automatically
3. Strategy optimized weekly
4. You just monitor the dashboard

**Enjoy your automated content creation!** 🚀

---

**Need more help?**
- Read: SETUP.md (detailed guide)
- Read: QUICKSTART.md (quick reference)
- Read: ARCHITECTURE.md (technical details)
- Check: PROJECT_SUMMARY.txt (complete overview)
