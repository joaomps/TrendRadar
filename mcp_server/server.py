"""
TrendRadar MCP Server - FastMCP 2.0 Implementation

Provides production-grade MCP tool server using FastMCP 2.0.
Supports both stdio and HTTP transport modes.
"""

import json
from typing import List, Optional, Dict

from fastmcp import FastMCP

from .tools.data_query import DataQueryTools
from .tools.analytics import AnalyticsTools
from .tools.search_tools import SearchTools
from .tools.config_mgmt import ConfigManagementTools
from .tools.system import SystemManagementTools


# Create FastMCP 2.0 application
mcp = FastMCP('trendradar-news')

# Global tool instances (initialized on first request)
_tools_instances = {}


def _get_tools(project_root: Optional[str] = None):
    """Get or create tool instances (singleton pattern)"""
    if not _tools_instances:
        _tools_instances['data'] = DataQueryTools(project_root)
        _tools_instances['analytics'] = AnalyticsTools(project_root)
        _tools_instances['search'] = SearchTools(project_root)
        _tools_instances['config'] = ConfigManagementTools(project_root)
        _tools_instances['system'] = SystemManagementTools(project_root)
    return _tools_instances


# ==================== Data Query Tools ====================

@mcp.tool
async def get_latest_news(
    platforms: Optional[List[str]] = None,
    limit: int = 50,
    include_url: bool = False
) -> str:
    """
    Get the latest batch of crawled news data to quickly understand current trends

    Args:
        platforms: List of platform IDs, e.g. ['zhihu', 'weibo', 'douyin']
                   - If not specified: uses all platforms configured in config.yaml
                   - Supported platforms come from the platforms config in config/config.yaml
                   - Each platform has a corresponding name field (e.g., "Zhihu", "Weibo") for AI recognition
        limit: Result limit, default 50, max 1000
               Note: Actual count may be less than requested, depending on available news
        include_url: Whether to include URL links, default False (saves tokens)

    Returns:
        JSON-formatted news list

    **Important: Data Display Guidelines**
    This tool returns a complete news list (typically 50 items). Please note:
    - **Tool Returns**: Complete 50 items ✅
    - **Display Recommendation**: Show all data to user unless explicitly asked to summarize
    - **User Expectation**: Users may need complete data, be cautious with summarization

    **When to Summarize**:
    - User explicitly says "summarize this" or "highlight key points"
    - When data exceeds 100 items, show partial data and ask if they want to see all

    **Note**: If user asks "why only showing partial", they need the complete data
    """
    tools = _get_tools()
    result = tools['data'].get_latest_news(platforms=platforms, limit=limit, include_url=include_url)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def get_trending_topics(
    top_n: int = 10,
    mode: str = 'current'
) -> str:
    """
    Get frequency statistics for your watched keywords (based on config/frequency_words.txt)

    Note: This tool does NOT automatically extract trending topics. Instead, it counts how often
    your personally configured keywords in config/frequency_words.txt appear in the news.
    You can customize this keyword watchlist.

    Args:
        top_n: Return top N keywords, default 10
        mode: Mode selection
            - daily: Daily cumulative statistics
            - current: Latest batch statistics (default)

    Returns:
        JSON-formatted keyword frequency statistics list
    """
    tools = _get_tools()
    result = tools['data'].get_trending_topics(top_n=top_n, mode=mode)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def get_news_by_date(
    date_query: Optional[str] = None,
    platforms: Optional[List[str]] = None,
    limit: int = 50,
    include_url: bool = False
) -> str:
    """
    Get news data for a specific date, used for historical data analysis and comparison

    Args:
        date_query: Date query, supported formats:
            - Natural language: "today", "yesterday", "day before yesterday", "3 days ago"
            - Standard date: "2024-01-15", "2024/01/15"
            - Default: "today" (saves tokens)
        platforms: List of platform IDs, e.g. ['zhihu', 'weibo', 'douyin']
                   - If not specified: uses all platforms configured in config.yaml
                   - Supported platforms come from the platforms config in config/config.yaml
                   - Each platform has a corresponding name field (e.g., "Zhihu", "Weibo") for AI recognition
        limit: Result limit, default 50, max 1000
               Note: Actual count may be less than requested, depending on available news for that date
        include_url: Whether to include URL links, default False (saves tokens)

    Returns:
        JSON-formatted news list including title, platform, ranking and other info

    **Important: Data Display Guidelines**
    This tool returns a complete news list (typically 50 items). Please note:
    - **Tool Returns**: Complete 50 items ✅
    - **Display Recommendation**: Show all data to user unless explicitly asked to summarize
    - **User Expectation**: Users may need complete data, be cautious with summarization

    **When to Summarize**:
    - User explicitly says "summarize this" or "highlight key points"
    - When data exceeds 100 items, show partial data and ask if they want to see all

    **Note**: If user asks "why only showing partial", they need the complete data
    """
    tools = _get_tools()
    result = tools['data'].get_news_by_date(
        date_query=date_query,
        platforms=platforms,
        limit=limit,
        include_url=include_url
    )
    return json.dumps(result, ensure_ascii=False, indent=2)



# ==================== Advanced Data Analysis Tools ====================

@mcp.tool
async def analyze_topic_trend(
    topic: str,
    analysis_type: str = "trend",
    date_range: Optional[Dict[str, str]] = None,
    granularity: str = "day",
    threshold: float = 3.0,
    time_window: int = 24,
    lookahead_hours: int = 6,
    confidence_threshold: float = 0.7
) -> str:
    """
    Unified topic trend analysis tool - Integrates multiple trend analysis modes

    Args:
        topic: Topic keyword (required)
        analysis_type: Analysis type, options:
            - "trend": Trending analysis (track topic popularity changes)
            - "lifecycle": Lifecycle analysis (complete cycle from emergence to decline)
            - "viral": Anomaly detection (identify suddenly viral topics)
            - "predict": Topic prediction (predict future potential trends)
        date_range: Date range (for trend and lifecycle modes), optional
                    - **Format**: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"} (must be standard date format)
                    - **Note**: AI must calculate and fill in specific dates based on current date, cannot use natural language like "today"
                    - **Calculation examples**:
                      - User says "last 7 days" → AI calculates: {"start": "2025-11-11", "end": "2025-11-17"} (assuming today is 11-17)
                      - User says "last week" → AI calculates: {"start": "2025-11-11", "end": "2025-11-17"} (Monday to Sunday of last week)
                      - User says "this month" → AI calculates: {"start": "2025-11-01", "end": "2025-11-17"} (Nov 1st to today)
                    - **Default**: Analyzes last 7 days if not specified
        granularity: Time granularity (trend mode), default "day" (only supports day, as underlying data is aggregated daily)
        threshold: Popularity surge multiplier threshold (viral mode), default 3.0
        time_window: Detection time window in hours (viral mode), default 24
        lookahead_hours: Prediction hours ahead (predict mode), default 6
        confidence_threshold: Confidence threshold (predict mode), default 0.7

    Returns:
        JSON format trend analysis results

    **AI Usage Instructions:**
    When users use relative time expressions (like "last 7 days", "past week", "last month"),
    AI must calculate specific YYYY-MM-DD format dates based on current date (obtained from <env>).

    **Important**: date_range does not accept natural language like "today", "yesterday" - must be YYYY-MM-DD format!

    Examples (assuming today is 2025-11-17):
        - User: "Analyze AI trends over the last 7 days"
          → analyze_topic_trend(topic="Artificial Intelligence", analysis_type="trend", date_range={"start": "2025-11-11", "end": "2025-11-17"})
        - User: "Check Tesla's popularity this month"
          → analyze_topic_trend(topic="Tesla", analysis_type="lifecycle", date_range={"start": "2025-11-01", "end": "2025-11-17"})
        - analyze_topic_trend(topic="Bitcoin", analysis_type="viral", threshold=3.0)
        - analyze_topic_trend(topic="ChatGPT", analysis_type="predict", lookahead_hours=6)
    """
    tools = _get_tools()
    result = tools['analytics'].analyze_topic_trend_unified(
        topic=topic,
        analysis_type=analysis_type,
        date_range=date_range,
        granularity=granularity,
        threshold=threshold,
        time_window=time_window,
        lookahead_hours=lookahead_hours,
        confidence_threshold=confidence_threshold
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def analyze_data_insights(
    insight_type: str = "platform_compare",
    topic: Optional[str] = None,
    date_range: Optional[Dict[str, str]] = None,
    min_frequency: int = 3,
    top_n: int = 20
) -> str:
    """
    Unified data insights analysis tool - Integrates multiple data analysis modes

    Args:
        insight_type: Insight type, options:
            - "platform_compare": Platform comparison analysis (compare different platforms' attention to topics)
            - "platform_activity": Platform activity statistics (track platform posting frequency and active times)
            - "keyword_cooccur": Keyword co-occurrence analysis (analyze patterns of keywords appearing together)
        topic: Topic keyword (optional, applicable for platform_compare mode)
        date_range: **【Object Type】** Date range (optional)
                    - **Format**: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
                    - **Example**: {"start": "2025-01-01", "end": "2025-01-07"}
                    - **Important**: Must be object format, cannot pass integers
        min_frequency: Minimum co-occurrence frequency (keyword_cooccur mode), default 3
        top_n: Return top N results (keyword_cooccur mode), default 20

    Returns:
        JSON format data insights analysis results

    Examples:
        - analyze_data_insights(insight_type="platform_compare", topic="Artificial Intelligence")
        - analyze_data_insights(insight_type="platform_activity", date_range={"start": "2025-01-01", "end": "2025-01-07"})
        - analyze_data_insights(insight_type="keyword_cooccur", min_frequency=5, top_n=15)
    """
    tools = _get_tools()
    result = tools['analytics'].analyze_data_insights_unified(
        insight_type=insight_type,
        topic=topic,
        date_range=date_range,
        min_frequency=min_frequency,
        top_n=top_n
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def analyze_sentiment(
    topic: Optional[str] = None,
    platforms: Optional[List[str]] = None,
    date_range: Optional[Dict[str, str]] = None,
    limit: int = 50,
    sort_by_weight: bool = True,
    include_url: bool = False
) -> str:
    """
    Analyze sentiment trends and popularity metrics of news topics

    Args:
        topic: Topic keyword (optional)
        platforms: List of platform IDs, e.g. ['zhihu', 'weibo', 'douyin']
                   - If not specified: uses all platforms configured in config.yaml
                   - Supported platforms come from the platforms config in config/config.yaml
                   - Each platform has a corresponding name field (e.g., "Zhihu", "Weibo") for AI recognition
        date_range: **【Object Type】** Date range (optional)
                    - **Format**: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
                    - **Example**: {"start": "2025-01-01", "end": "2025-01-07"}
                    - **Important**: Must be object format, cannot pass integers
        limit: Return news limit, default 50, max 100
               Note: This tool deduplicates news titles (same title from different platforms kept only once),
               so actual return count may be less than requested limit
        sort_by_weight: Whether to sort by popularity weight, default True
        include_url: Whether to include URL links, default False (saves tokens)

    Returns:
        JSON-formatted analysis results including sentiment distribution, popularity trends and related news

    **Important: Data Display Guidelines**
    - This tool returns complete analysis results and news list
    - **Default Display**: Show complete analysis results (including all news)
    - Only filter and summarize when user explicitly requests "summary" or "key points"
    """
    tools = _get_tools()
    result = tools['analytics'].analyze_sentiment(
        topic=topic,
        platforms=platforms,
        date_range=date_range,
        limit=limit,
        sort_by_weight=sort_by_weight,
        include_url=include_url
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def find_similar_news(
    reference_title: str,
    threshold: float = 0.6,
    limit: int = 50,
    include_url: bool = False
) -> str:
    """
    Find other news items similar to a reference news title

    Args:
        reference_title: News title (complete or partial)
        threshold: Similarity threshold, 0-1 range, default 0.6
                   Note: Higher threshold means stricter matching, fewer results returned
        limit: Result limit, default 50, max 100
               Note: Actual return count depends on similarity matching, may be less than requested
        include_url: Whether to include URL links, default False (saves tokens)

    Returns:
        JSON-formatted list of similar news items including similarity scores

    **Important: Data Display Guidelines**
    - This tool returns a complete list of similar news
    - **Default Display**: Show all returned news (including similarity scores)
    - Only filter and summarize when user explicitly requests "summary" or "key points"
    """
    tools = _get_tools()
    result = tools['analytics'].find_similar_news(
        reference_title=reference_title,
        threshold=threshold,
        limit=limit,
        include_url=include_url
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def generate_summary_report(
    report_type: str = "daily",
    date_range: Optional[Dict[str, str]] = None
) -> str:
    """
    Daily/Weekly summary report generator - Automatically generates trending topic summary reports

    Args:
        report_type: Report type (daily/weekly)
        date_range: **【Object Type】** Custom date range (optional)
                    - **Format**: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
                    - **Example**: {"start": "2025-01-01", "end": "2025-01-07"}
                    - **Important**: Must be object format, cannot pass integers

    Returns:
        JSON-formatted summary report including Markdown-formatted content
    """
    tools = _get_tools()
    result = tools['analytics'].generate_summary_report(
        report_type=report_type,
        date_range=date_range
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== Intelligent Search Tools ====================

@mcp.tool
async def search_news(
    query: str,
    search_mode: str = "keyword",
    date_range: Optional[Dict[str, str]] = None,
    platforms: Optional[List[str]] = None,
    limit: int = 50,
    sort_by: str = "relevance",
    threshold: float = 0.6,
    include_url: bool = False
) -> str:
    """
    Unified search interface supporting multiple search modes

    Args:
        query: Search keyword or content snippet
        search_mode: Search mode, options:
            - "keyword": Exact keyword matching (default, best for searching specific topics)
            - "fuzzy": Fuzzy content matching (best for searching content snippets, filters results with similarity below threshold)
            - "entity": Entity name search (best for searching people/locations/organizations)
        date_range: Date range (optional)
                    - **Format**: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
                    - **Example**: {"start": "2025-01-01", "end": "2025-01-07"}
                    - **Note**: AI must calculate specific date format based on user's natural language (e.g., "last 7 days")
                    - **Default**: Queries today's news if not specified
                    - **Important**: start and end can be identical (for single-day queries)
        platforms: List of platform IDs, e.g. ['zhihu', 'weibo', 'douyin']
                   - If not specified: uses all platforms configured in config.yaml
                   - Supported platforms come from the platforms config in config/config.yaml
                   - Each platform has a corresponding name field (e.g., "Zhihu", "Weibo") for AI recognition
        limit: Result limit, default 50, max 1000
               Note: Actual return count depends on search matching results (especially in fuzzy mode, low-similarity results are filtered)
        sort_by: Sort option, values:
            - "relevance": Sort by relevance (default)
            - "weight": Sort by news weight
            - "date": Sort by date
        threshold: Similarity threshold (fuzzy mode only), 0-1 range, default 0.6
                   Note: Higher threshold means stricter matching, fewer results returned
        include_url: Whether to include URL links, default False (saves tokens)

    Returns:
        JSON-formatted search results including title, platform, ranking and other info

    **Important: Data Display Guidelines**
    - This tool returns a complete search result list
    - **Default Display**: Show all returned news without summarization or filtering
    - Only summarize when user explicitly requests "summary" or "key points"

    **AI Usage Instructions:**
    When users use relative time expressions (like "last 7 days", "past week", "last month"),
    AI must calculate specific YYYY-MM-DD format dates based on current date (obtained from <env>).

    **Important**: date_range does not accept natural language like "today", "yesterday" - must be YYYY-MM-DD format!

    **Calculation Rules** (assuming today is 2025-11-17 from <env>):
    - "today" → Do not pass date_range (defaults to today)
    - "last 7 days" → {"start": "2025-11-11", "end": "2025-11-17"}
    - "past week" → {"start": "2025-11-11", "end": "2025-11-17"}
    - "last week" → Calculate last Monday to Sunday, e.g. {"start": "2025-11-11", "end": "2025-11-17"}
    - "this month" → {"start": "2025-11-01", "end": "2025-11-17"}
    - "last 30 days" → {"start": "2025-10-19", "end": "2025-11-17"}

    Examples (assuming today is 2025-11-17):
        - User: "Today's AI news" → search_news(query="Artificial Intelligence")
        - User: "AI news from last 7 days" → search_news(query="Artificial Intelligence", date_range={"start": "2025-11-11", "end": "2025-11-17"})
        - Specific date: search_news(query="Artificial Intelligence", date_range={"start": "2025-01-01", "end": "2025-01-07"})
        - Fuzzy search: search_news(query="Tesla price cut", search_mode="fuzzy", threshold=0.4)
    """
    tools = _get_tools()
    result = tools['search'].search_news_unified(
        query=query,
        search_mode=search_mode,
        date_range=date_range,
        platforms=platforms,
        limit=limit,
        sort_by=sort_by,
        threshold=threshold,
        include_url=include_url
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def search_related_news_history(
    reference_text: str,
    time_preset: str = "yesterday",
    threshold: float = 0.4,
    limit: int = 50,
    include_url: bool = False
) -> str:
    """
    Search historical data for news related to a reference seed news item

    Args:
        reference_text: Reference news title (complete or partial)
        time_preset: Time range preset, options:
            - "yesterday": Yesterday
            - "last_week": Last week (7 days)
            - "last_month": Last month (30 days)
            - "custom": Custom date range (requires start_date and end_date)
        threshold: Relevance threshold, 0-1 range, default 0.4
                   Note: Combined similarity calculation (70% keyword overlap + 30% text similarity)
                   Higher threshold means stricter matching, fewer results returned
        limit: Result limit, default 50, max 100
               Note: Actual return count depends on relevance matching results, may be less than requested
        include_url: Whether to include URL links, default False (saves tokens)

    Returns:
        JSON-formatted list of related news items including relevance scores and time distribution

    **Important: Data Display Guidelines**
    - This tool returns a complete list of related news
    - **Default Display**: Show all returned news (including relevance scores)
    - Only filter and summarize when user explicitly requests "summary" or "key points"
    """
    tools = _get_tools()
    result = tools['search'].search_related_news_history(
        reference_text=reference_text,
        time_preset=time_preset,
        threshold=threshold,
        limit=limit,
        include_url=include_url
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== Configuration and System Management Tools ====================

@mcp.tool
async def get_current_config(
    section: str = "all"
) -> str:
    """
    Get current system configuration

    Args:
        section: Configuration section, options:
            - "all": All configuration (default)
            - "crawler": Crawler configuration
            - "push": Push notification configuration
            - "keywords": Keyword configuration
            - "weights": Weight algorithm configuration

    Returns:
        JSON-formatted configuration information
    """
    tools = _get_tools()
    result = tools['config'].get_current_config(section=section)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def get_system_status() -> str:
    """
    Get system runtime status and health check information

    Returns system version, data statistics, cache status and other information

    Returns:
        JSON-formatted system status information
    """
    tools = _get_tools()
    result = tools['system'].get_system_status()
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
async def trigger_crawl(
    platforms: Optional[List[str]] = None,
    save_to_local: bool = False,
    include_url: bool = False
) -> str:
    """
    Manually trigger a crawl task (with optional persistence)

    Args:
        platforms: Specify list of platform IDs, e.g. ['zhihu', 'weibo', 'douyin']
                   - If not specified: uses all platforms configured in config.yaml
                   - Supported platforms come from the platforms config in config/config.yaml
                   - Each platform has a corresponding name field (e.g., "Zhihu", "Weibo") for AI recognition
                   - Note: Failed platforms will be listed in the failed_platforms field of results
        save_to_local: Whether to save to local output directory, default False
        include_url: Whether to include URL links, default False (saves tokens)

    Returns:
        JSON-formatted task status information containing:
        - platforms: List of successfully crawled platforms
        - failed_platforms: List of failed platforms (if any)
        - total_news: Total number of crawled news items
        - data: News data

    Examples:
        - Temporary crawl: trigger_crawl(platforms=['zhihu'])
        - Crawl and save: trigger_crawl(platforms=['weibo'], save_to_local=True)
        - Use default platforms: trigger_crawl()  # Crawls all platforms configured in config.yaml
    """
    tools = _get_tools()
    result = tools['system'].trigger_crawl(platforms=platforms, save_to_local=save_to_local, include_url=include_url)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== Server Startup Entry ====================

def run_server(
    project_root: Optional[str] = None,
    transport: str = 'stdio',
    host: str = '0.0.0.0',
    port: int = 3333
):
    """
    Start MCP Server

    Args:
        project_root: Project root directory path
        transport: Transport mode, 'stdio' or 'http'
        host: Listen address for HTTP mode, default 0.0.0.0
        port: Listen port for HTTP mode, default 3333
    """
    # Initialize tool instances
    _get_tools(project_root)

    # Print startup information
    print()
    print("=" * 60)
    print("  TrendRadar MCP Server - FastMCP 2.0")
    print("=" * 60)
    print(f"  Transport mode: {transport.upper()}")

    if transport == 'stdio':
        print("  Protocol: MCP over stdio (standard input/output)")
        print("  Description: Communicates with MCP clients via standard input/output")
    elif transport == 'http':
        print(f"  Listen address: http://{host}:{port}")
        print(f"  HTTP endpoint: http://{host}:{port}/mcp")
        print("  Protocol: MCP over HTTP (production)")

    if project_root:
        print(f"  Project directory: {project_root}")
    else:
        print("  Project directory: Current directory")

    print()
    print("  Registered tools:")
    print("    === Core Data Query (P0 Priority) ===")
    print("    1. get_latest_news        - Get latest news")
    print("    2. get_news_by_date       - Query news by date (supports natural language)")
    print("    3. get_trending_topics    - Get trending topics")
    print()
    print("    === Intelligent Search Tools ===")
    print("    4. search_news                  - Unified news search (keyword/fuzzy/entity)")
    print("    5. search_related_news_history  - Historical related news search")
    print()
    print("    === Advanced Data Analysis ===")
    print("    6. analyze_topic_trend      - Unified topic trend analysis (popularity/lifecycle/viral/prediction)")
    print("    7. analyze_data_insights    - Unified data insight analysis (platform comparison/activity/keyword co-occurrence)")
    print("    8. analyze_sentiment        - Sentiment trend analysis")
    print("    9. find_similar_news        - Find similar news")
    print("    10. generate_summary_report - Daily/Weekly summary generation")
    print()
    print("    === Configuration and System Management ===")
    print("    11. get_current_config      - Get current system configuration")
    print("    12. get_system_status       - Get system runtime status")
    print("    13. trigger_crawl           - Manually trigger crawl task")
    print("=" * 60)
    print()

    # Run server based on transport mode
    if transport == 'stdio':
        mcp.run(transport='stdio')
    elif transport == 'http':
        # HTTP mode (production recommended)
        mcp.run(
            transport='http',
            host=host,
            port=port,
            path='/mcp'  # HTTP endpoint path
        )
    else:
        raise ValueError(f"Unsupported transport mode: {transport}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='TrendRadar MCP Server - News trending aggregation MCP tool server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
For detailed configuration instructions, see: README-Cherry-Studio.md
        """
    )
    parser.add_argument(
        '--transport',
        choices=['stdio', 'http'],
        default='stdio',
        help='Transport mode: stdio (default) or http (production)'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Listen address for HTTP mode, default 0.0.0.0'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=3333,
        help='Listen port for HTTP mode, default 3333'
    )
    parser.add_argument(
        '--project-root',
        help='Project root directory path'
    )

    args = parser.parse_args()

    run_server(
        project_root=args.project_root,
        transport=args.transport,
        host=args.host,
        port=args.port
    )
