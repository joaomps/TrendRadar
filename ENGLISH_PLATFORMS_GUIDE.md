# Replacing Chinese Platforms with English News Sources

## Current Architecture

TrendRadar currently uses the **NewNow API** (`newsnow.busiyi.world`) which aggregates trending topics from Chinese platforms:
- Weibo (微博)
- Douyin (抖音)
- Zhihu (知乎)
- Baidu Hot Search (百度热搜)
- Toutiao (今日头条)
- etc.

The API call: `https://newsnow.busiyi.world/api/s?id={platform_id}&latest`

---

## Options for English Platforms

### Option 1: Use Multi-Platform Aggregators (Recommended)

**News API** (https://newsapi.org)
- **Coverage**: 80,000+ sources worldwide
- **Free Tier**: 100 requests/day, 30-day history
- **Languages**: English, 14+ others
- **Sources**: BBC, CNN, TechCrunch, Reddit, etc.
- **Endpoints**:
  - Top headlines: `/v2/top-headlines`
  - Everything: `/v2/everything`
  - Sources: `/v2/sources`

**Example sources you can add**:
```yaml
platforms:
  - id: "techcrunch"
    name: "TechCrunch"
    category: "technology"
  - id: "bbc-news"
    name: "BBC News"
    category: "general"
  - id: "cnn"
    name: "CNN"
    category: "general"
  - id: "hacker-news"
    name: "Hacker News"
    category: "technology"
  - id: "reddit-worldnews"
    name: "Reddit World News"
    category: "general"
```

**Implementation**:
```python
# Replace in main.py DataFetcher class
def fetch_data(self, platform_id):
    url = f"https://newsapi.org/v2/top-headlines"
    params = {
        'sources': platform_id,
        'apiKey': self.newsapi_key,
        'pageSize': 100
    }
    response = requests.get(url, params=params)
    return self.parse_newsapi_response(response.json())
```

---

### Option 2: Use Individual Platform APIs

**Direct API Integration**:

1. **Reddit API** (Free)
   - Trending posts from r/worldnews, r/technology, r/news
   - Endpoint: `https://www.reddit.com/r/{subreddit}/hot.json`
   - No API key needed for read-only

2. **Hacker News API** (Free)
   - Top stories, trending tech news
   - Endpoint: `https://hacker-news.firebaseio.com/v0/topstories.json`
   - Completely free, no auth

3. **Product Hunt API** (Free tier)
   - Trending products and tech
   - Requires API key

4. **Twitter/X Trending** (Paid)
   - Trending topics by location
   - Requires API v2 (paid)

5. **Google Trends** (Free via pytrends)
   - Trending searches
   - Python library: `pytrends`

---

### Option 3: Web Scraping (Not Recommended)

Scrape trending sections from:
- news.ycombinator.com (Hacker News)
- reddit.com/r/all
- trends.google.com

**Cons**:
- Against ToS for many sites
- Fragile (breaks with HTML changes)
- Rate limiting issues

---

## Recommended Implementation Plan

### Phase 1: Add News API Support

**1. Get API Key**:
```bash
# Sign up at https://newsapi.org
# Free tier: 100 requests/day
```

**2. Update Configuration** (`config/config.yaml`):
```yaml
api:
  newsapi_key: "${NEWSAPI_KEY}"  # Or hardcode for testing

platforms:
  # Technology Sources
  - id: "techcrunch"
    name: "TechCrunch"
    api: "newsapi"
  - id: "the-verge"
    name: "The Verge"
    api: "newsapi"
  - id: "ars-technica"
    name: "Ars Technica"
    api: "newsapi"
  - id: "wired"
    name: "Wired"
    api: "newsapi"

  # General News
  - id: "bbc-news"
    name: "BBC News"
    api: "newsapi"
  - id: "cnn"
    name: "CNN"
    api: "newsapi"
  - id: "associated-press"
    name: "Associated Press"
    api: "newsapi"

  # Business
  - id: "bloomberg"
    name: "Bloomberg"
    api: "newsapi"
  - id: "financial-times"
    name: "Financial Times"
    api: "newsapi"
```

**3. Update DataFetcher** (`main.py`):
```python
class DataFetcher:
    def __init__(self, config):
        self.newsapi_key = config.get('api', {}).get('newsapi_key', '')
        # ... existing code ...

    def fetch_data(self, platform_info):
        api_type = platform_info.get('api', 'newsnow')

        if api_type == 'newsapi':
            return self.fetch_from_newsapi(platform_info['id'])
        elif api_type == 'reddit':
            return self.fetch_from_reddit(platform_info['id'])
        elif api_type == 'hackernews':
            return self.fetch_from_hackernews()
        else:
            # Fallback to original NewNow API
            return self.fetch_from_newsnow(platform_info['id'])

    def fetch_from_newsapi(self, source_id):
        """Fetch from News API"""
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'sources': source_id,
            'apiKey': self.newsapi_key,
            'pageSize': 100,
            'language': 'en'
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get('status') != 'ok':
            raise Exception(f"News API error: {data.get('message')}")

        # Transform to TrendRadar format
        items = []
        for idx, article in enumerate(data.get('articles', []), 1):
            items.append({
                'rank': idx,
                'title': article['title'],
                'url': article['url'],
                'publishedAt': article['publishedAt']
            })

        return {
            'id': source_id,
            'items': items
        }

    def fetch_from_reddit(self, subreddit):
        """Fetch from Reddit"""
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        headers = {'User-Agent': 'TrendRadar/1.0'}
        params = {'limit': 100}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()

        items = []
        for idx, post in enumerate(data['data']['children'], 1):
            post_data = post['data']
            items.append({
                'rank': idx,
                'title': post_data['title'],
                'url': f"https://reddit.com{post_data['permalink']}",
                'score': post_data['score']
            })

        return {
            'id': f"reddit-{subreddit}",
            'items': items
        }

    def fetch_from_hackernews(self):
        """Fetch from Hacker News"""
        # Get top story IDs
        ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        ids = requests.get(ids_url, timeout=10).json()[:100]

        items = []
        for idx, story_id in enumerate(ids[:30], 1):  # Limit to 30 for speed
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story = requests.get(item_url, timeout=5).json()

            if story and story.get('title'):
                items.append({
                    'rank': idx,
                    'title': story['title'],
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'score': story.get('score', 0)
                })

        return {
            'id': 'hackernews',
            'items': items
        }
```

---

### Phase 2: Add Free Sources (No API Key)

**Reddit Configuration**:
```yaml
platforms:
  - id: "worldnews"
    name: "Reddit World News"
    api: "reddit"
  - id: "technology"
    name: "Reddit Technology"
    api: "reddit"
  - id: "news"
    name: "Reddit News"
    api: "reddit"
  - id: "programming"
    name: "Reddit Programming"
    api: "reddit"
```

**Hacker News Configuration**:
```yaml
platforms:
  - id: "hackernews"
    name: "Hacker News"
    api: "hackernews"
```

---

### Phase 3: Hybrid Approach (Best of Both)

Keep some Chinese sources AND add English sources:

```yaml
platforms:
  # English Sources (via News API)
  - id: "techcrunch"
    name: "TechCrunch"
    api: "newsapi"
  - id: "bbc-news"
    name: "BBC News"
    api: "newsapi"

  # Free English Sources
  - id: "hackernews"
    name: "Hacker News"
    api: "hackernews"
  - id: "worldnews"
    name: "Reddit World News"
    api: "reddit"

  # Keep Chinese Sources (original API)
  - id: "zhihu"
    name: "Zhihu"
    api: "newsnow"
  - id: "weibo"
    name: "Weibo"
    api: "newsnow"
```

This gives you both English and Chinese trending news!

---

## Quick Start: Add English Sources Today

### Step 1: Install News API (Free)

1. Sign up at https://newsapi.org
2. Get your API key
3. Add to `.env` or `config.yaml`:
```bash
export NEWSAPI_KEY="your_key_here"
```

### Step 2: Update Code

Create a new file: `english_platforms_adapter.py`

```python
"""Adapter for English news platforms"""

import requests
from typing import Dict, List

class EnglishPlatformsAdapter:
    """Fetch from English news sources"""

    def __init__(self, newsapi_key: str = None):
        self.newsapi_key = newsapi_key

    def fetch_newsapi(self, source_id: str) -> Dict:
        """Fetch from News API"""
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'sources': source_id,
            'apiKey': self.newsapi_key,
            'pageSize': 100,
            'language': 'en'
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get('status') != 'ok':
            raise Exception(f"News API error: {data.get('message')}")

        items = []
        for idx, article in enumerate(data.get('articles', []), 1):
            items.append({
                'rank': idx,
                'title': article['title'],
                'url': article['url'],
                'description': article.get('description', ''),
                'publishedAt': article.get('publishedAt', '')
            })

        return {'id': source_id, 'items': items}

    def fetch_reddit(self, subreddit: str) -> Dict:
        """Fetch from Reddit"""
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        headers = {'User-Agent': 'TrendRadar/1.0'}
        params = {'limit': 100}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()

        items = []
        for idx, post in enumerate(data['data']['children'], 1):
            post_data = post['data']
            items.append({
                'rank': idx,
                'title': post_data['title'],
                'url': f"https://reddit.com{post_data['permalink']}",
                'score': post_data['score'],
                'comments': post_data['num_comments']
            })

        return {'id': f"reddit-{subreddit}", 'items': items}

    def fetch_hackernews(self) -> Dict:
        """Fetch from Hacker News"""
        ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        ids = requests.get(ids_url, timeout=10).json()[:30]

        items = []
        for idx, story_id in enumerate(ids, 1):
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story = requests.get(item_url, timeout=5).json()

            if story and story.get('title'):
                items.append({
                    'rank': idx,
                    'title': story['title'],
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'score': story.get('score', 0)
                })

        return {'id': 'hackernews', 'items': items}
```

### Step 3: Test It

```python
# Test the adapter
from english_platforms_adapter import EnglishPlatformsAdapter

adapter = EnglishPlatformsAdapter(newsapi_key="your_key")

# Test News API
techcrunch = adapter.fetch_newsapi('techcrunch')
print(f"TechCrunch top story: {techcrunch['items'][0]['title']}")

# Test Reddit (no key needed!)
reddit_tech = adapter.fetch_reddit('technology')
print(f"Reddit tech top post: {reddit_tech['items'][0]['title']}")

# Test Hacker News (no key needed!)
hn = adapter.fetch_hackernews()
print(f"HN top story: {hn['items'][0]['title']}")
```

---

## Available English Sources (News API)

### Technology
- techcrunch, the-verge, ars-technica, wired, engadget, hacker-news, recode, techradar, the-next-web

### Business
- bloomberg, financial-times, business-insider, fortune, the-economist, the-wall-street-journal

### General News
- bbc-news, cnn, abc-news, associated-press, reuters, nbc-news, cbs-news, usa-today

### Entertainment
- entertainment-weekly, ign, polygon, buzzfeed, mtv-news

### Science
- national-geographic, new-scientist

### Sports
- espn, fox-sports, nfl-news, talksport

Full list: https://newsapi.org/sources

---

## Cost Comparison

| Service | Free Tier | Paid Plans | Best For |
|---------|-----------|------------|----------|
| News API | 100 req/day | $449/mo unlimited | Multi-source aggregation |
| Reddit API | Unlimited reads | Free | Free trending content |
| Hacker News | Unlimited | Free | Tech news |
| NewNow (current) | Unlimited? | Free | Chinese platforms |

**Recommendation**: Start with Reddit + Hacker News (both free), add News API if you need more sources.

---

## Next Steps

Would you like me to:

1. **Implement the adapter** - Create `english_platforms_adapter.py` with Reddit + Hacker News support (free, no API key)
2. **Update main.py** - Modify DataFetcher to support multiple APIs
3. **Update config** - Add English platform configurations
4. **Create hybrid config** - Keep Chinese sources + add English ones

Let me know which approach you prefer!
