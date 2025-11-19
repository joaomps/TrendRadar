# GitHub Secrets Setup Guide

This guide shows you how to configure News API and other sensitive credentials using GitHub Secrets.

---

## 📝 Overview

GitHub Secrets allow you to store sensitive information (like API keys and webhook URLs) securely without exposing them in your repository. The application automatically uses these secrets when running in GitHub Actions.

---

## 🔐 Adding News API Key

### Step 1: Get Your News API Key

1. Visit **https://newsapi.org**
2. Click **Get API Key** or **Sign Up**
3. Create a free account
4. Copy your API key (looks like: `abc123def456...`)

### Step 2: Add to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** (top right)
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add the secret:
   - **Name**: `NEWSAPI_KEY`
   - **Value**: Paste your API key (e.g., `abc123def456ghi789...`)
6. Click **Add secret**

### Step 3: Verify Setup

The GitHub Actions workflow (`.github/workflows/crawler.yml`) is already configured to use this secret:

```yaml
env:
  NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
```

### Step 4: Enable News API Sources

Uncomment News API platforms in `config/config.yaml`:

```yaml
platforms:
  # ... existing Reddit/HN sources ...

  # Technology News
  - id: "techcrunch"
    name: "TechCrunch"
    api: "newsapi"
    source_id: "techcrunch"

  - id: "the-verge"
    name: "The Verge"
    api: "newsapi"
    source_id: "the-verge"

  # General News
  - id: "bbc-news"
    name: "BBC News"
    api: "newsapi"
    source_id: "bbc-news"
```

### Step 5: Test It

1. Commit and push your changes
2. Trigger the workflow:
   - Go to **Actions** tab
   - Select **Hot News Crawler**
   - Click **Run workflow**
3. Check the logs - you should see News API sources being fetched

---

## 🎯 Priority Order

The application uses this priority for configuration values:

**1. Environment Variables** (GitHub Secrets) ← **Highest Priority**
**2. Config File** (`config/config.yaml`) ← **Fallback**

Example:
```yaml
# config.yaml
api:
  newsapi_key: ""  # Can be empty - GitHub Secret takes priority
```

In GitHub Actions, `NEWSAPI_KEY` secret overrides the config file value.

---

## 📋 All Available Secrets

Here's a complete list of secrets you can configure:

### API Keys
| Secret Name | Purpose | Required For |
|-------------|---------|--------------|
| `NEWSAPI_KEY` | News API access | English news sources (TechCrunch, BBC, etc.) |

### Notification Webhooks
| Secret Name | Purpose | Service |
|-------------|---------|---------|
| `FEISHU_WEBHOOK_URL` | Feishu bot webhook | Feishu notifications |
| `DINGTALK_WEBHOOK_URL` | DingTalk bot webhook | DingTalk notifications |
| `WEWORK_WEBHOOK_URL` | WeCom bot webhook | WeCom notifications |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Telegram notifications |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | Telegram notifications |

### Email Configuration
| Secret Name | Purpose | Example |
|-------------|---------|---------|
| `EMAIL_FROM` | Sender email | `your-email@gmail.com` |
| `EMAIL_PASSWORD` | Email password/app password | `abcd1234efgh5678` |
| `EMAIL_TO` | Recipient email(s) | `recipient@example.com` |
| `EMAIL_SMTP_SERVER` | SMTP server (optional) | `smtp.gmail.com` |
| `EMAIL_SMTP_PORT` | SMTP port (optional) | `587` |

### Ntfy Configuration
| Secret Name | Purpose | Example |
|-------------|---------|---------|
| `NTFY_SERVER_URL` | Ntfy server URL | `https://ntfy.sh` |
| `NTFY_TOPIC` | Ntfy topic name | `my-topic-name` |
| `NTFY_TOKEN` | Ntfy access token | `tk_abc123...` |

---

## 🔧 How It Works

### In GitHub Actions:

1. **Workflow file** (`.github/workflows/crawler.yml`) passes secrets as environment variables:
   ```yaml
   env:
     NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
     FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
     # ... etc
   ```

2. **Application code** (`main.py`) reads environment variables with fallback to config file:
   ```python
   config["NEWSAPI_KEY"] = os.environ.get("NEWSAPI_KEY", "").strip() \
                           or api_config.get("newsapi_key", "")
   ```

3. **Priority**:
   - If `NEWSAPI_KEY` environment variable exists → use it
   - Otherwise → use value from `config.yaml`
   - Otherwise → empty string

### Locally:

When running locally (not in GitHub Actions):
- Application reads from `config/config.yaml` directly
- You can add your API key to the config file (don't commit it!)
- Or set environment variable: `export NEWSAPI_KEY="your_key"`

---

## 🛡️ Security Best Practices

### ✅ DO:
- ✅ Store all sensitive data in GitHub Secrets
- ✅ Keep `config/config.yaml` webhook fields empty if using fork
- ✅ Add secrets before enabling notifications
- ✅ Use different secrets for production/testing

### ❌ DON'T:
- ❌ **NEVER** commit API keys or webhooks to config file in public repos
- ❌ Don't share your secrets with others
- ❌ Don't use personal credentials for bots
- ❌ Don't expose secrets in logs

### For Public Forks:

If you forked this repository:

**config/config.yaml should look like:**
```yaml
api:
  newsapi_key: ""  # EMPTY - use GitHub Secret

webhooks:
  feishu_url: ""  # EMPTY - use GitHub Secret
  dingtalk_url: ""  # EMPTY
  # ... all empty
```

**GitHub Secrets should contain:**
- `NEWSAPI_KEY`: Your actual API key
- `FEISHU_WEBHOOK_URL`: Your actual webhook
- etc.

---

## 🧪 Testing Secrets

### Test Locally (Without Secrets):

```bash
# Run without News API (uses free Reddit/HN sources only)
python main.py
```

### Test Locally (With Secrets):

```bash
# Set environment variable
export NEWSAPI_KEY="your_api_key_here"

# Run
python main.py
```

### Test in GitHub Actions:

1. Add secrets in repository settings
2. Go to Actions tab
3. Click **Hot News Crawler** workflow
4. Click **Run workflow** → **Run workflow**
5. Check logs to verify secrets are working

**Expected output:**
```
✓ Fetched reddit-worldnews successfully (50 items)
✓ Fetched hackernews successfully (50 items)
✓ Fetched techcrunch successfully (100 items)  ← News API working!
```

---

## 🔍 Troubleshooting

### "News API key not configured"

**Cause**: Secret not set or named incorrectly

**Solution**:
1. Verify secret name is exactly `NEWSAPI_KEY` (case-sensitive)
2. Check secret value is not empty
3. Re-run workflow after adding secret

### "News API error: apiKeyInvalid"

**Cause**: Invalid API key

**Solution**:
1. Copy API key again from newsapi.org
2. Update GitHub Secret
3. Make sure no extra spaces in the key

### "401 Unauthorized" for News API

**Cause**: API key expired or rate limit exceeded

**Solution**:
1. Check your News API dashboard for usage
2. Free tier: 100 requests/day
3. Wait until reset (midnight UTC) or upgrade plan

### Workflow not using secrets

**Cause**: Secrets not passed to workflow

**Solution**:
1. Check `.github/workflows/crawler.yml` has:
   ```yaml
   env:
     NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
   ```
2. Verify secret exists in repository settings
3. Re-run workflow

---

## 📚 Quick Reference

### Add Secret:
1. Repository → Settings
2. Secrets and variables → Actions
3. New repository secret
4. Name: `NEWSAPI_KEY`, Value: `your_key`
5. Add secret

### Use in Code:
```python
# Automatically handled - no code changes needed!
newsapi_key = CONFIG.get('NEWSAPI_KEY', '')
```

### Verify:
```bash
# In GitHub Actions logs, you should see:
✓ Fetched [newsapi-source] successfully
```

---

## 🎉 Done!

Once you've added `NEWSAPI_KEY` to GitHub Secrets and uncommented News API sources in `config/config.yaml`, your application will:

✅ Fetch from Reddit (free)
✅ Fetch from Hacker News (free)
✅ Fetch from News API sources (TechCrunch, BBC, etc.)
✅ Keep all credentials secure
✅ Work automatically in GitHub Actions

**No more configuration needed!**
