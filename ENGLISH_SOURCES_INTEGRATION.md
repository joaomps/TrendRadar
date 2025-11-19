# English News Sources Integration - Complete Guide

**Status**: ✅ **FULLY INTEGRATED**
**Date**: 2025-11-19

---

## 🎉 What's New

TrendRadar now supports **English news sources** alongside the original Chinese platforms! You can now track trending topics from:

### ✅ **Currently Active (Free - No API Key Required)**
- **Reddit** - r/worldnews, r/news, r/technology, r/programming, r/science
- **Hacker News** - Top tech stories

### 🔓 **Available (Requires Free API Key)**
- **News API** - 80,000+ sources including:
  - Technology: TechCrunch, The Verge, Wired, Ars Technica
  - General News: BBC, CNN, Reuters
  - Business: Bloomberg, Business Insider

---

## 📋 Files Modified/Created

### New Files:
1. **[english_platforms_adapter.py](english_platforms_adapter.py)** - Adapter for English platforms
2. **[ENGLISH_PLATFORMS_GUIDE.md](ENGLISH_PLATFORMS_GUIDE.md)** - Detailed platform guide
3. **[ENGLISH_SOURCES_INTEGRATION.md](ENGLISH_SOURCES_INTEGRATION.md)** - This file

### Modified Files:
1. **[config/config.yaml](config/config.yaml)** - Updated with English platforms
2. **[main.py](main.py)** - DataFetcher now supports multiple APIs

---

## 🚀 Quick Start

### Option 1: Use Free Sources Only (Recommended to Start)

**No setup required!** The app is already configured with free Reddit and Hacker News sources.

Just run:
```bash
python main.py
```

You'll see English trending news from:
- Reddit World News
- Reddit News
- Reddit Technology
- Reddit Programming
- Reddit Science
- Hacker News

### Option 2: Add News API Sources (100 requests/day free)

1. **Get API Key** (takes 2 minutes):
   - Visit https://newsapi.org
   - Sign up for free account
   - Copy your API key

2. **Add Key to Config**:
   ```bash
   # Edit config/config.yaml
   vim config/config.yaml
   ```

   Find the `api` section and add your key:
   ```yaml
   api:
     newsapi_key: "YOUR_API_KEY_HERE"
   ```

3. **Uncomment News API Sources** in `config/config.yaml`:
   ```yaml
   platforms:
     # ... existing Reddit/HN sources ...

     # Uncomment these:
     - id: "techcrunch"
       name: "TechCrunch"
       api: "newsapi"
       source_id: "techcrunch"

     - id: "bbc-news"
       name: "BBC News"
       api: "newsapi"
       source_id: "bbc-news"

     # ... etc
   ```

4. **Run**:
   ```bash
   python main.py
   ```

---

## 📊 What You Get

### Reddit Integration
Each Reddit source provides:
- Top 50 hottest posts
- Post title
- Reddit discussion URL
- Upvote score
- Comment count

Example output:
```
reddit-worldnews | Reddit World News
1. Major climate summit reaches breakthrough agreement [URL:...]
2. New space telescope discovers Earth-like planet [URL:...]
...
```

### Hacker News Integration
Provides:
- Top 50 stories
- Story title
- External URL or HN discussion link
- Points score
- Number of comments

Example output:
```
hackernews | Hacker News
1. New Python 3.13 Released with Performance Improvements [URL:...]
2. How We Scaled to 1M Users [URL:...]
...
```

### News API Integration (when configured)
Provides:
- Top 100 headlines per source
- Article title
- Publication URL
- Author
- Published date
- Description

Example output:
```
techcrunch | TechCrunch
1. AI Startup Raises $100M Series B [URL:...]
2. Apple Announces New MacBook Pro [URL:...]
...
```

---

## ⚙️ Configuration Details

### Platform Configuration Format

Each platform in `config/config.yaml` has these fields:

```yaml
- id: "unique-identifier"        # Platform ID (unique)
  name: "Display Name"            # What users see
  api: "reddit|hackernews|newsapi|newsnow"  # Which API to use
  # Additional fields based on API type:
  subreddit: "worldnews"         # For Reddit
  source_id: "techcrunch"        # For News API
```

### Supported APIs

| API | Auth Required | Rate Limit | Cost |
|-----|---------------|------------|------|
| `reddit` | No | Unlimited (read-only) | Free |
| `hackernews` | No | Unlimited | Free |
| `newsapi` | Yes (API key) | 100 requests/day | Free tier |
| `newsnow` | No | Unknown | Free |

---

## 🔧 Advanced Configuration

### Adding More Reddit Communities

```yaml
platforms:
  - id: "reddit-artificial"
    name: "Reddit AI"
    api: "reddit"
    subreddit: "artificial"       # r/artificial

  - id: "reddit-machinelearning"
    name: "Reddit ML"
    api: "reddit"
    subreddit: "MachineLearning"  # r/MachineLearning
```

### Hybrid: Chinese + English Sources

Keep both! Uncomment Chinese platforms:

```yaml
platforms:
  # English sources
  - id: "reddit-worldnews"
    name: "Reddit World News"
    api: "reddit"
    subreddit: "worldnews"

  - id: "hackernews"
    name: "Hacker News"
    api: "hackernews"

  # Chinese sources (uncomment to enable)
  - id: "weibo"
    name: "Weibo"
    api: "newsnow"

  - id: "zhihu"
    name: "Zhihu"
    api: "newsnow"
```

This gives you **global trending coverage**!

---

## 🧪 Testing

### Test the Adapter Directly

```bash
python english_platforms_adapter.py
```

Expected output:
```
============================================================
Testing English Platforms Adapter
============================================================

1. Testing Reddit (r/worldnews)...
   Found 50 posts
   Top post: [Latest trending news title]...

2. Testing Hacker News...
   Found 50 stories
   Top story: [Latest HN story]...

3. Testing News API (requires key)...
   ⚠️  News API key not configured (expected without API key)

============================================================
Test complete!
============================================================
```

### Test Full Integration

```bash
# Run the full crawler
python main.py
```

Look for output like:
```
Configured platforms: ['Reddit World News', 'Reddit News', 'Reddit Technology', ...]
Starting data crawl, request interval: 1000ms
✓ Fetched reddit-worldnews successfully (50 items)
✓ Fetched reddit-news successfully (50 items)
✓ Fetched reddit-technology successfully (50 items)
✓ Fetched hackernews successfully (50 items)
...
```

---

## 📈 Performance & Rate Limiting

### Request Timing
- **Reddit**: ~2-3 seconds per subreddit
- **Hacker News**: ~15-20 seconds (fetches individual stories)
- **News API**: ~1-2 seconds per source

### Daily Limits
- **Reddit**: Unlimited (respectful use recommended)
- **Hacker News**: Unlimited (includes automatic rate limiting)
- **News API Free**: 100 requests/day

### Optimization Tips

1. **For faster crawls**: Use only Reddit (fastest)
2. **For comprehensive news**: Add News API sources
3. **For tech focus**: Hacker News + Reddit r/technology + r/programming
4. **For global news**: Reddit r/worldnews + r/news + News API (BBC, Reuters)

---

## 🛠️ Troubleshooting

### "English platforms adapter not found"
**Solution**: The adapter file is in the project root:
```bash
ls -la english_platforms_adapter.py
chmod +x english_platforms_adapter.py
```

### "News API key not configured"
**Solution**: Two options:
1. Use only Reddit/HN (no key needed)
2. Get free key from https://newsapi.org and add to config

### "No data returned" for Reddit
**Possible causes**:
- Subreddit name typo (case-sensitive!)
- Network/firewall blocking Reddit
- Rate limiting (add delays)

**Solution**:
```yaml
# Verify subreddit exists: https://reddit.com/r/SUBREDDIT_NAME
- id: "reddit-worldnews"
  subreddit: "worldnews"  # Not "WorldNews"
```

### Slow Hacker News Fetching
**Expected behavior**: HN fetches individual stories, takes 15-20 seconds.

**To speed up**: The adapter limits to 50 stories (already optimized).

---

## 🔄 Migration from Chinese-Only

### Before (Chinese platforms only):
```yaml
platforms:
  - id: "weibo"
    name: "Weibo"
  - id: "zhihu"
    name: "Zhihu"
```

### After (English platforms):
```yaml
platforms:
  - id: "reddit-worldnews"
    name: "Reddit World News"
    api: "reddit"
    subreddit: "worldnews"

  - id: "hackernews"
    name: "Hacker News"
    api: "hackernews"
```

### Or Hybrid (both):
```yaml
platforms:
  # English
  - id: "reddit-worldnews"
    name: "Reddit World News"
    api: "reddit"
    subreddit: "worldnews"

  # Chinese
  - id: "weibo"
    name: "Weibo"
    api: "newsnow"
```

**No code changes needed** - just update config!

---

## 📚 Available News API Sources

### Technology
- `techcrunch` - TechCrunch
- `the-verge` - The Verge
- `wired` - Wired
- `ars-technica` - Ars Technica
- `engadget` - Engadget
- `hacker-news` - Hacker News (via News API)
- `recode` - Recode
- `techradar` - TechRadar
- `the-next-web` - The Next Web

### General News
- `bbc-news` - BBC News
- `cnn` - CNN
- `abc-news` - ABC News
- `associated-press` - Associated Press
- `reuters` - Reuters
- `nbc-news` - NBC News
- `cbs-news` - CBS News
- `usa-today` - USA Today

### Business
- `bloomberg` - Bloomberg
- `financial-times` - Financial Times
- `business-insider` - Business Insider
- `fortune` - Fortune
- `the-economist` - The Economist
- `the-wall-street-journal` - WSJ

Full list: https://newsapi.org/sources

---

## 🎯 Recommended Configurations

### For Tech Enthusiasts:
```yaml
platforms:
  - id: "hackernews"
    name: "Hacker News"
    api: "hackernews"

  - id: "reddit-programming"
    name: "Reddit Programming"
    api: "reddit"
    subreddit: "programming"

  - id: "reddit-technology"
    name: "Reddit Technology"
    api: "reddit"
    subreddit: "technology"

  # If you have News API key:
  - id: "techcrunch"
    name: "TechCrunch"
    api: "newsapi"
    source_id: "techcrunch"
```

### For Global News:
```yaml
platforms:
  - id: "reddit-worldnews"
    name: "Reddit World News"
    api: "reddit"
    subreddit: "worldnews"

  - id: "reddit-news"
    name: "Reddit News"
    api: "reddit"
    subreddit: "news"

  # With News API key:
  - id: "bbc-news"
    name: "BBC News"
    api: "newsapi"
    source_id: "bbc-news"

  - id: "reuters"
    name: "Reuters"
    api: "newsapi"
    source_id: "reuters"
```

### For Everything:
```yaml
platforms:
  # Free sources
  - id: "reddit-worldnews"
    name: "Reddit World News"
    api: "reddit"
    subreddit: "worldnews"

  - id: "reddit-technology"
    name: "Reddit Technology"
    api: "reddit"
    subreddit: "technology"

  - id: "hackernews"
    name: "Hacker News"
    api: "hackernews"

  # News API sources (with key)
  - id: "bbc-news"
    name: "BBC News"
    api: "newsapi"
    source_id: "bbc-news"

  - id: "techcrunch"
    name: "TechCrunch"
    api: "newsapi"
    source_id: "techcrunch"

  # Chinese sources (optional)
  - id: "weibo"
    name: "Weibo"
    api: "newsnow"
```

---

## ✅ Summary

**What's Working:**
- ✅ Reddit integration (5 subreddits configured)
- ✅ Hacker News integration
- ✅ News API support (ready when you add key)
- ✅ Hybrid Chinese + English support
- ✅ Backward compatibility with existing data

**Next Steps:**
1. **Test it**: `python main.py`
2. **Optional**: Get News API key for more sources
3. **Customize**: Add your favorite subreddits or News API sources

**Support:**
- See [ENGLISH_PLATFORMS_GUIDE.md](ENGLISH_PLATFORMS_GUIDE.md) for detailed API info
- Test adapter: `python english_platforms_adapter.py`
- Check config: `cat config/config.yaml`

---

**Enjoy tracking English trending news!** 🎉
