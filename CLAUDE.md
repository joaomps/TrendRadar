# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrendRadar is a news aggregation and trend analysis tool that collects hot topics from 11+ mainstream platforms (Zhihu, Weibo, Douyin, Baidu, Bilibili, etc.) and provides intelligent filtering, analysis, and multi-channel notifications. The project consists of two main components:

1. **News Crawler & Notification System** ([main.py](main.py) - 4,554 lines)
2. **AI Analysis MCP Server** ([mcp_server/](mcp_server/) - Model Context Protocol server for AI assistants)

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
News Sources (11+ platforms via newsnow API)
    ↓ DataFetcher (with retry logic)
Raw JSON Data
    ↓ NewsAnalyzer (parse & save)
TXT Files (output/YYYY-MM-DD/txt/HH-MM.txt)
    ↓ Notification System
[Webhooks: Feishu/DingTalk/WeWork/Telegram/Email]
    ↓ ParserService (for MCP)
AI Analysis Tools (13 tools via MCP server)
```

### Core Components

**News Crawler ([main.py](main.py)):**
- `PushRecordManager`: Tracks daily push history (7-day retention)
- `DataFetcher`: Fetches data from newsnow API with retries (2 attempts, 3-5s backoff)
- `NewsAnalyzer`: Processes, filters, weights, and generates reports

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
- File naming (`output/` directories)
- Push window time ranges
- MCP date parsing (`DateUtils.parse_date_input()`)

### Token Optimization in MCP
MCP tools default to `include_url=False` to save AI tokens. Set to `True` when URLs needed:
```python
await tools.get_latest_news(limit=20, include_url=True)
```

## Configuration Management

### Primary Config: [config/config.yaml](config/config.yaml)
Key sections:
- `app`: Version checking
- `crawler`: Request intervals, proxy settings
- `report`: Mode (daily/incremental/current), rank threshold
- `notification`: Enable/disable, push window settings, webhooks
- `weight`: Algorithm weights (rank/frequency/hotness)
- `platforms`: List of 11+ news sources with IDs

### Environment Variable Override
Environment variables take priority over `config.yaml`:
- Core: `ENABLE_CRAWLER`, `ENABLE_NOTIFICATION`, `REPORT_MODE`
- Webhooks: `FEISHU_WEBHOOK_URL`, `DINGTALK_WEBHOOK_URL`, `TELEGRAM_BOT_TOKEN`, etc.
- Push window: `PUSH_WINDOW_ENABLED`, `PUSH_WINDOW_START`, `PUSH_WINDOW_END`

Check [docker/entrypoint.sh](docker/entrypoint.sh) for complete list of supported env vars.

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

### Version Info
- **Main Version**: Check [main.py:34](main.py#L34) for `VERSION`
- **MCP Version**: Check [mcp_server/server.py:27](mcp_server/server.py#L27) for `MCP_VERSION`
- **Python Requirement**: >=3.10
