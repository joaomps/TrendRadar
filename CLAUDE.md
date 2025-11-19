# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrendRadar is a news aggregation and trend analysis tool that collects hot topics from multiple platforms worldwide and provides intelligent filtering, analysis, and multi-channel notifications. The project consists of two main components:

1. **News Crawler & Notification System** ([main.py](main.py) - 4,554 lines)
2. **AI Analysis MCP Server** ([mcp_server/](mcp_server/) - Model Context Protocol server for AI assistants)

### English Migration Status

**Migration Progress**: ~80% complete
- **Currently Active**: 6 English sources (Reddit + Hacker News) - all free, no API key required
- **Ready for Activation**: News API integration (100 requests/day free tier) - requires API key
- **Backward Compatible**: Supports both old Chinese date format (YYYY年MM月DD日) and new English format (YYYY-MM-DD)

**Available English Platforms**:
- **Reddit** (Free): r/worldnews, r/news, r/technology, r/programming, r/science
- **Hacker News** (Free): Top tech stories
- **News API** (API key required): 80,000+ sources including TechCrunch, BBC, CNN, Reuters, Bloomberg

**Documentation**:
- [ENGLISH_SOURCES_INTEGRATION.md](ENGLISH_SOURCES_INTEGRATION.md) - Complete integration guide
- [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) - Secure API key configuration
- [english_platforms_adapter.py](english_platforms_adapter.py) - Platform adapter implementation

## Essential Commands

### Setup
```bash
# Mac/Linux
./setup-mac.sh

# Windows
setup-windows.bat

# Manual installation
pip install -r requirements.txt
# or with UV
uv sync
```

### Running the Application
```bash
# Run news crawler (one-time execution)
python main.py

# Start MCP server (HTTP mode for testing)
./start-http.sh
# or explicitly
uv run python -m mcp_server.server --transport http --host 0.0.0.0 --port 3333

# Start MCP server (STDIO mode - for AI clients like Claude Desktop)
uv run python -m mcp_server.server
```

### Docker Deployment
```bash
# Using docker-compose
cd docker
docker-compose up -d

# Using official image
docker run -d \
  -v ./config:/app/config:ro \
  -v ./output:/app/output \
  -e TZ=Asia/Shanghai \
  wantcat/trendradar:latest
```

### GitHub Actions
- Automatically runs every hour via cron schedule
- Manual trigger available via workflow_dispatch in GitHub Actions tab

## Architecture

### Data Flow
```
News Sources (Multi-platform support)
├── Reddit (Free) ──────────┐
├── Hacker News (Free) ─────┤
├── News API (API key) ─────┤──> EnglishPlatformsAdapter
└── Chinese platforms ──────┘──> NewNow API
    ↓ DataFetcher (with retry logic & multi-API routing)
Raw JSON Data
    ↓ NewsAnalyzer (parse & save)
TXT Files (output/YYYY-MM-DD/txt/HH-MM.txt)
    ↓ Notification System
[Webhooks: Feishu/DingTalk/WeWork/Telegram/Email/Ntfy]
    ↓ ParserService (for MCP - supports both date formats)
AI Analysis Tools (13 tools via MCP server)
```

### Core Components

**News Crawler ([main.py](main.py)):**
- `PushRecordManager`: Tracks daily push history (7-day retention)
- `DataFetcher`: Multi-API data fetcher with retry logic (2 attempts, 3-5s backoff)
  - Routes requests based on platform API type (reddit/hackernews/newsapi/newsnow)
  - Uses `EnglishPlatformsAdapter` for Reddit, Hacker News, and News API
  - Falls back to NewNow API for Chinese platforms
- `NewsAnalyzer`: Processes, filters, weights, and generates reports

**English Platforms Adapter ([english_platforms_adapter.py](english_platforms_adapter.py)):**
- `EnglishPlatformsAdapter`: Unified adapter for English news platforms
  - `fetch_from_reddit()`: Fetches from Reddit subreddits (no auth required)
  - `fetch_from_hackernews()`: Fetches from Hacker News Firebase API (no auth required)
  - `fetch_from_newsapi()`: Fetches from News API (requires API key)
  - Supports proxy configuration
  - Returns data in standardized format compatible with NewsAnalyzer

**MCP Server ([mcp_server/](mcp_server/)):**
- **Tools Layer** ([tools/](mcp_server/tools/)): 13 async tools exposed via FastMCP decorators
  - Data queries: `get_latest_news`, `get_news_by_date`, `get_trending_topics`
  - Search: `search_news`, `search_related_news_history`, `find_similar_news`
  - Analytics: `analyze_topic_trend`, `analyze_data_insights`, `analyze_sentiment`
  - Reports: `generate_summary_report`
  - Config/System: `get_current_config`, `get_system_status`, `trigger_crawl`
- **Services Layer** ([services/](mcp_server/services/)): Data access and parsing
  - `ParserService`: Reads and parses TXT files by date
  - `DataService`: Unified query interface with caching
  - `CacheService`: In-memory TTL cache (15-30 min for queries)
- **Utils Layer** ([utils/](mcp_server/utils/)): Validators, error handling, date parsing

### Singleton Pattern
MCP tools use `_get_tools()` singleton to ensure single instance across all tool calls.

## Multi-Platform Support

### Supported API Types

TrendRadar supports 4 different API types, configured via the `api` field in platform configuration:

1. **reddit** - Reddit API (Free, no authentication)
   - Fetches hot posts from specified subreddits
   - Returns top 50 posts with scores and comment counts
   - Example: `r/worldnews`, `r/technology`, `r/programming`

2. **hackernews** - Hacker News Firebase API (Free, no authentication)
   - Fetches top stories from Hacker News
   - Returns top 50 stories with scores
   - Single configuration (no parameters needed)

3. **newsapi** - News API (Requires API key, 100 requests/day free tier)
   - Access to 80,000+ news sources worldwide
   - Supports specific source IDs (techcrunch, bbc-news, cnn, etc.)
   - Returns top 100 headlines per source

4. **newsnow** - NewNow API (Free, legacy Chinese platforms)
   - Original API for Chinese platforms
   - Used as fallback for non-English sources

### Platform Configuration Format

Each platform in `config/config.yaml` requires these fields:

```yaml
platforms:
  # Reddit configuration
  - id: "reddit-worldnews"      # Unique identifier
    name: "Reddit World News"   # Display name
    api: "reddit"               # API type
    subreddit: "worldnews"      # Reddit-specific: subreddit name

  # Hacker News configuration
  - id: "hackernews"
    name: "Hacker News"
    api: "hackernews"           # No additional parameters needed

  # News API configuration
  - id: "techcrunch"
    name: "TechCrunch"
    api: "newsapi"
    source_id: "techcrunch"     # NewsAPI-specific: source identifier

  # Chinese platform (legacy)
  - id: "zhihu"
    name: "Zhihu"
    api: "newsnow"              # Or omit 'api' field (defaults to newsnow)
```

### Adding New Platforms

**To add a Reddit subreddit**:
```yaml
- id: "reddit-artificial"
  name: "Reddit AI"
  api: "reddit"
  subreddit: "artificial"       # r/artificial
```

**To add a News API source**:
```yaml
- id: "wired"
  name: "Wired"
  api: "newsapi"
  source_id: "wired"            # Get source IDs from https://newsapi.org/sources
```

## Key Patterns and Conventions

### Three Push Modes
Configured in `config/config.yaml` → `report.mode`:
- **daily**: Daily summary (all matching news + new items since last push)
- **current**: Current rankings (latest snapshot + new items)
- **incremental**: Delta mode (only new matching news since last push)

### Keyword Filtering System
Located in [config/frequency_words.txt](config/frequency_words.txt):
- **Normal keywords**: Match any word in title
- **Required keywords** (`+word`): Must be present in title
- **Filter keywords** (`!word`): Exclude news containing this word
- **Word groups**: Separated by blank lines for independent tracking

Example:
```
Technology
AI
+Artificial Intelligence
!Entertainment

Economy
Stock Market
```

### Weighting Algorithm
News importance calculated in `NewsAnalyzer.calculate_weight()`:
```python
weight = rank_weight(60%) + frequency_weight(30%) + hotness_weight(10%)
```
- **Rank weight**: Position in trending lists (1-10, configurable threshold)
- **Frequency weight**: Number of appearances across platforms
- **Hotness weight**: Ratio of high-ranking appearances

Weights configurable in `config/config.yaml` → `weight` section.

### Data Storage Format
Files stored in `output/YYYY-MM-DD/txt/HH-MM.txt`:
```
toutiao | Toutiao
1. News Title [URL:https://...] [MOBILE:https://...]
2. Another News Item [URL:...]

baidu | Baidu Hot Search
1. ...
```

Parser uses regex to extract platform names, titles, and URLs.

### Beijing Time Convention
All timestamps use `Asia/Shanghai` timezone via `pytz`. Critical for:
- File naming (`output/` directories) - Format: `YYYY-MM-DD/txt/HH-MM.txt`
- Push window time ranges
- MCP date parsing (`DateUtils.parse_date_input()`)

**Date Format Migration**:
- **Old format** (deprecated, backward compatible): `YYYY年MM月DD日` and `HH时MM分.txt`
- **New format** (current): `YYYY-MM-DD` and `HH-MM.txt`
- ParserService automatically detects and supports both formats
- Use [migrate_output_dates.py](migrate_output_dates.py) to convert old data

### Token Optimization in MCP
MCP tools default to `include_url=False` to save AI tokens. Set to `True` when URLs needed:
```python
await tools.get_latest_news(limit=20, include_url=True)
```

## Configuration Management

### Primary Config: [config/config.yaml](config/config.yaml)
Key sections:
- `app`: Version checking
- `api`: API keys (newsapi_key)
- `crawler`: Request intervals, proxy settings
- `report`: Mode (daily/incremental/current), rank threshold
- `notification`: Enable/disable, push window settings, webhooks
- `weight`: Algorithm weights (rank/frequency/hotness)
- `platforms`: List of news sources with API type configuration

**Example configuration**:
```yaml
api:
  newsapi_key: ""  # Empty if using GitHub Secrets

platforms:
  - id: "reddit-worldnews"
    name: "Reddit World News"
    api: "reddit"
    subreddit: "worldnews"

  - id: "techcrunch"
    name: "TechCrunch"
    api: "newsapi"
    source_id: "techcrunch"
```

### Environment Variable Override (Priority System)

**Environment variables take HIGHEST priority** over `config.yaml`. This enables secure deployment with GitHub Secrets.

**Configuration Priority Order**:
1. **Environment Variables** (GitHub Secrets in Actions) ← Highest Priority
2. **config.yaml** values ← Fallback

**Supported Environment Variables**:

**API Keys**:
- `NEWSAPI_KEY` - News API key (overrides `api.newsapi_key`)

**Core Settings**:
- `ENABLE_CRAWLER` - Enable/disable crawler
- `ENABLE_NOTIFICATION` - Enable/disable notifications
- `REPORT_MODE` - Push mode (daily/incremental/current)

**Notification Webhooks**:
- `FEISHU_WEBHOOK_URL` - Feishu bot webhook
- `DINGTALK_WEBHOOK_URL` - DingTalk bot webhook
- `WEWORK_WEBHOOK_URL` - WeCom bot webhook
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Telegram chat ID
- `EMAIL_FROM`, `EMAIL_PASSWORD`, `EMAIL_TO` - Email configuration
- `EMAIL_SMTP_SERVER`, `EMAIL_SMTP_PORT` - SMTP settings
- `NTFY_SERVER_URL`, `NTFY_TOPIC`, `NTFY_TOKEN` - Ntfy configuration

**Push Window**:
- `PUSH_WINDOW_ENABLED` - Enable push time window
- `PUSH_WINDOW_START` - Window start time (HH:MM)
- `PUSH_WINDOW_END` - Window end time (HH:MM)

Check [docker/entrypoint.sh](docker/entrypoint.sh) for complete list.

## GitHub Secrets Configuration

### Quick Setup Guide

**For News API (Optional)**:
1. Get free API key at https://newsapi.org (100 requests/day)
2. Go to GitHub repository → Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `NEWSAPI_KEY`, Value: Your API key
5. Click "Add secret"

**GitHub Actions Integration**:
The workflow file ([.github/workflows/crawler.yml](.github/workflows/crawler.yml)) automatically passes secrets as environment variables:

```yaml
- name: Run crawler
  env:
    NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
    FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
    # ... other secrets
  run: python main.py
```

**Security Best Practices**:
- ✅ Store ALL sensitive data in GitHub Secrets (not in config.yaml)
- ✅ Keep `config.yaml` webhook fields empty in public repos
- ✅ Use environment variables for production deployment
- ❌ NEVER commit API keys or webhooks to public repositories

See [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) for detailed instructions.

## MCP Server Details

### FastMCP 2.0 Framework
Uses decorators for tool registration:
```python
@mcp.tool()
async def get_latest_news(...) -> ToolResult:
    ...
```

### Error Handling
All tools return standardized `ToolResult`:
```python
ToolResult(
    content=[TextContent(type="text", text="...")],
    isError=False  # or True for errors
)
```

### Caching Strategy
- **News data queries**: 30 min TTL
- **Analytics/search**: 15 min TTL
- **Config/system**: No caching (always fresh)

### Analysis Capabilities
- **Topic Trend Analysis** (`analyze_topic_trend`): 4 modes (trend/lifecycle/viral/prediction)
- **Platform Comparison** (`analyze_data_insights`): Cross-platform attention analysis
- **Sentiment Analysis** (`analyze_sentiment`): Returns AI prompts for LLM analysis
- **Similar News Finder** (`find_similar_news`): SequenceMatcher-based (threshold 0.6)

## Development Notes

### Rate Limiting
- 1000ms default interval between platform requests (configured in `config.yaml`)
- Random jitter added to avoid detection

### Notification Batch Limits
- **Feishu**: 29KB per message
- **DingTalk**: 20KB per message
- **WeWork/Telegram/Email**: Auto-batching implemented in respective senders

### Testing with Historical Data
Project includes test data in `output/` for Nov 1-15, 2025. Use for MCP server testing without running crawler.

### Performance Considerations

**Request Timing by Platform**:
- **Reddit**: ~2-3 seconds per subreddit
- **Hacker News**: ~15-20 seconds (fetches individual stories with rate limiting)
- **News API**: ~1-2 seconds per source
- **NewNow API**: ~1-2 seconds per platform

**Rate Limits**:
- **Reddit**: Unlimited (respectful use recommended)
- **Hacker News**: Unlimited (built-in rate limiting in adapter)
- **News API Free Tier**: 100 requests/day
- **NewNow API**: Unknown (appears unlimited)

**Optimization Tips**:
- For faster crawls: Use only Reddit (fastest free source)
- For comprehensive news: Combine Reddit + Hacker News + News API
- For tech focus: Hacker News + Reddit r/technology + r/programming
- For global news: Reddit r/worldnews + r/news + News API (BBC, Reuters)

### Version Info
- **Main Version**: Check [main.py:34](main.py#L34) for `VERSION`
- **MCP Version**: Check [mcp_server/server.py:27](mcp_server/server.py#L27) for `MCP_VERSION`
- **Python Requirement**: >=3.10

## Additional Documentation

- **[ENGLISH_SOURCES_INTEGRATION.md](ENGLISH_SOURCES_INTEGRATION.md)** - Complete guide to English platform integration, configuration examples, testing procedures
- **[GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)** - Step-by-step guide for configuring API keys and webhooks via GitHub Secrets
- **[english_platforms_adapter.py](english_platforms_adapter.py)** - Source code for English platforms adapter with inline documentation
- **[migrate_output_dates.py](migrate_output_dates.py)** - Utility script for migrating old Chinese date format to new English format
- **[README.md](README.md)** - Main project README with setup instructions and feature overview
