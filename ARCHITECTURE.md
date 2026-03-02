# 🏗️ System Architecture

## Overview

The Telegram Content Automation System is a modular, event-driven architecture designed for zero-budget automated content creation and distribution.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     MAIN CONTROLLER                          │
│                      (main.py)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │ SCHEDULER │  │ DASHBOARD │  │ ANALYTICS │
        └───────────┘  └───────────┘  └───────────┘
                │             │             │
                ▼             ▼             ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │ AI ENGINE │  │   FLASK   │  │  SQLITE   │
        └───────────┘  └───────────┘  └───────────┘
                │                           │
                ▼                           ▼
        ┌───────────┐              ┌───────────┐
        │ TELEGRAM  │◄─────────────│ COLLECTOR │
        │    BOT    │              └───────────┘
        └───────────┘
```

## Module Breakdown

### 1. Main Controller (`main.py`)
**Purpose**: Entry point and system orchestration

**Responsibilities**:
- Initialize all components
- Handle command-line interface
- Manage system lifecycle
- Signal handling (Ctrl+C)

**Key Functions**:
- `start()` - Start automation system
- `stop()` - Graceful shutdown
- `post_now()` - Manual posting trigger

### 2. Configuration (`bot/config.py`)
**Purpose**: Centralized configuration management

**Features**:
- Environment variable loading
- Path management
- Validation
- Default values

**Configuration Sources**:
1. `.env` file (primary)
2. Environment variables
3. Default values

### 3. Scheduler (`bot/scheduler.py`)
**Purpose**: Time-based automation orchestration

**Technology**: APScheduler (BackgroundScheduler)

**Jobs**:
- Content posting (configurable times)
- Analytics collection (daily at 02:00)
- Strategy adjustment (weekly Monday 03:00)

**Flow**:
```
Trigger → Select Topic → Generate Content → 
Generate Image → Post → Save to DB
```

### 4. AI Engine

#### Content Generator (`ai_engine/content_generator.py`)
**Purpose**: AI-powered text content creation

**Technology**: Ollama (local LLM)

**Process**:
1. Select topic-specific prompt
2. Call Ollama API
3. Format response
4. Fallback to pre-written content if error

**Output Format**:
- Catchy headline
- 5-7 bullet points
- Call-to-action
- Relevant hashtags

#### Image Generator (`ai_engine/image_generator.py`)
**Purpose**: Visual content creation

**Technologies**:
- Stable Diffusion (optional)
- Pillow (text overlay)
- Gradient fallback

**Process**:
1. Generate base image (SD or gradient)
2. Add text overlay
3. Save to images directory
4. Return file path

**Image Specs**:
- Size: 1080x1080px
- Format: PNG
- Text: Centered, white with shadow

### 5. Telegram Bot (`bot/telegram_bot.py`)
**Purpose**: Telegram API integration

**Technology**: python-telegram-bot (async)

**Features**:
- Multi-target posting (channel + group)
- Retry mechanism (3 attempts)
- Markdown formatting
- Stats collection

**Methods**:
- `post_content()` - Send message with image
- `get_post_stats()` - Retrieve views/forwards

### 6. Analytics System

#### Database (`analytics/database.py`)
**Purpose**: Data persistence and queries

**Technology**: SQLite3

**Tables**:

**posts**:
```sql
- id (PRIMARY KEY)
- message_id
- chat_id
- date
- topic
- views
- forwards
- reactions
- target_type
- created_at
```

**topic_weights**:
```sql
- topic (PRIMARY KEY)
- weight
- total_posts
- total_views
- avg_engagement
- last_updated
```

**Key Operations**:
- Save post metadata
- Update statistics
- Query performance metrics
- Calculate topic weights

#### Collector (`analytics/collector.py`)
**Purpose**: Stats gathering and analysis

**Functions**:

**collect_stats()**:
1. Get posts older than 24 hours
2. Fetch stats from Telegram
3. Update database

**analyze_and_adjust()**:
1. Calculate 7-day performance
2. Compute engagement scores
3. Update topic weights
4. Log results

**Engagement Score Formula**:
```
score = avg_views + (avg_forwards × 2)
```

**Weight Calculation**:
```
weight = 0.5 + (topic_score / max_score) × 1.5
Range: 0.5 to 2.0
```

### 7. Dashboard (`dashboard/app.py`)
**Purpose**: Web-based monitoring interface

**Technology**: Flask

**Endpoints**:

**GET /**
- Serves HTML dashboard

**GET /api/stats**
- Returns overall statistics
- JSON format

**GET /api/topic-performance**
- Returns per-topic metrics
- Last 30 days

**GET /api/engagement-chart**
- Generates matplotlib chart
- Returns base64 image

**Features**:
- Real-time updates (60s refresh)
- Responsive design
- Interactive charts
- Topic comparison

### 8. Logger (`bot/logger.py`)
**Purpose**: Centralized logging

**Features**:
- File and console output
- Daily log rotation
- Formatted timestamps
- Module-specific loggers

**Log Levels**:
- INFO: Normal operations
- ERROR: Failures and exceptions
- DEBUG: Detailed debugging (optional)

## Data Flow

### Content Creation Flow
```
1. Scheduler triggers at configured time
2. Scheduler selects topic based on weights
3. ContentGenerator creates text via Ollama
4. ImageGenerator creates visual
5. TelegramBot posts to channel/group
6. Database saves post metadata
7. Logger records all operations
```

### Analytics Flow
```
1. Collector runs daily (02:00)
2. Queries posts older than 24h
3. Fetches stats from Telegram API
4. Updates database with metrics
5. Dashboard displays updated data
```

### Strategy Adjustment Flow
```
1. Analyzer runs weekly (Monday 03:00)
2. Calculates 7-day performance per topic
3. Computes engagement scores
4. Updates topic weights in database
5. Future posts use new weights
```

## Topic Selection Algorithm

```python
def select_topic():
    weights = db.get_topic_weights()
    # weights = {'motivational': 1.5, 'tech_news': 0.8, ...}
    
    topics = list(weights.keys())
    topic_weights = [weights[t] for t in topics]
    
    # Weighted random selection
    selected = random.choices(topics, weights=topic_weights, k=1)[0]
    
    return selected
```

**Example**:
- Motivational: weight 1.5 (high engagement)
- Tech News: weight 0.8 (low engagement)
- Result: Motivational selected ~65% of time

## Error Handling Strategy

### Content Generation
- Primary: Ollama API
- Fallback: Pre-written content
- Never fails

### Image Generation
- Primary: Stable Diffusion
- Fallback: Gradient images
- Never fails

### Telegram Posting
- Retry: 3 attempts
- Delay: 5 seconds between retries
- Logs: All failures recorded

### Database Operations
- Try-catch all queries
- Log errors
- Return safe defaults

## Performance Characteristics

### Resource Usage
- **Memory**: 
  - Without SD: ~500MB
  - With SD: ~4GB
- **CPU**: 
  - Content gen: 2-5 seconds
  - Image gen (SD): 10-30 seconds
  - Image gen (gradient): <1 second
- **Disk**: 
  - Images: ~100KB each
  - Database: <10MB
  - Logs: ~1MB/day

### Scalability
- **Posts**: Unlimited (database scales)
- **Topics**: Add more in config
- **Targets**: Multiple channels/groups
- **Schedule**: Any frequency

## Security Considerations

### Secrets Management
- Bot token in `.env` (not committed)
- Environment variables supported
- No hardcoded credentials

### API Safety
- Rate limiting respected
- Retry with backoff
- Error handling

### Data Privacy
- Local database only
- No external analytics
- Logs contain no PII

## Extension Points

### Adding New Topics
1. Add to `Config.TOPICS`
2. Add prompt in `ContentGenerator`
3. Add colors in `ImageGenerator`

### Custom Content Sources
- Implement new generator class
- Follow same interface
- Plug into scheduler

### Additional Platforms
- Create new bot class
- Implement `post_content()` method
- Add to scheduler

### Advanced Analytics
- Add columns to database
- Extend collector queries
- Update dashboard API

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.10+ | Core runtime |
| LLM | Ollama (Llama3/Mistral) | Content generation |
| Image AI | Stable Diffusion | Image generation |
| Image Processing | Pillow | Text overlay |
| Telegram | python-telegram-bot | API integration |
| Scheduling | APScheduler | Automation |
| Database | SQLite3 | Data persistence |
| Web Framework | Flask | Dashboard |
| Visualization | Matplotlib | Charts |
| Config | python-dotenv | Environment vars |

## Deployment Architecture

```
┌─────────────────────────────────────┐
│         Local Machine               │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Ollama Server              │  │
│  │   (localhost:11434)          │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Automation System          │  │
│  │   - Scheduler                │  │
│  │   - AI Engine                │  │
│  │   - Database                 │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Dashboard                  │  │
│  │   (localhost:5000)           │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
                 │
                 │ HTTPS
                 ▼
        ┌────────────────┐
        │  Telegram API  │
        │  (Cloud)       │
        └────────────────┘
```

## Future Enhancements

### Planned Features
- [ ] Multi-language support
- [ ] Video generation
- [ ] Voice messages
- [ ] Instagram integration
- [ ] Advanced A/B testing
- [ ] Custom ML models
- [ ] Sentiment analysis
- [ ] Trend detection

### Optimization Opportunities
- [ ] Caching for Ollama responses
- [ ] Batch image generation
- [ ] Async database operations
- [ ] Redis for session management
- [ ] Docker containerization
- [ ] Kubernetes deployment

---

**Architecture Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: AI Automation Team
