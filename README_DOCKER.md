# TrendRadar Docker Guide

This guide explains how to deploy and manage TrendRadar using Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system.
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop).

## Quick Start

### Option 1: Use Pre-built Image (Recommended)

1.  Navigate to the `docker` directory:
    ```bash
    cd docker
    ```

2.  Create a `.env` file from the example (if available) or create one manually with your configuration. You can see the available environment variables in `docker-compose.yml`.

3.  Start the container:
    ```bash
    docker-compose up -d
    ```

### Option 2: Build Locally

If you want to build the image from the source code:

1.  Navigate to the `docker` directory:
    ```bash
    cd docker
    ```

2.  Build and start using the build configuration:
    ```bash
    docker-compose -f docker-compose-build.yml up -d --build
    ```

## Configuration

Configuration is managed via environment variables. You can set these in a `.env` file in the `docker` directory or directly in the `docker-compose.yml` file.

### Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CRON_SCHEDULE` | Cron expression for schedule | `*/5 * * * *` (Every 5 mins) |
| `RUN_MODE` | Run mode (`cron` or `once`) | `cron` |
| `IMMEDIATE_RUN` | Run immediately on start | `true` |
| `ENABLE_CRAWLER` | Enable news crawling | - |
| `ENABLE_NOTIFICATION` | Enable notifications | - |
| `REPORT_MODE` | Report mode | - |

**Notification Channels:**
- `FEISHU_WEBHOOK_URL`
- `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID`
- `DINGTALK_WEBHOOK_URL`
- `WEWORK_WEBHOOK_URL`
- `EMAIL_*` (SMTP settings)
- `NTFY_*` (ntfy.sh settings)

## Directory Structure

The Docker setup maps the following host directories to the container:

- `../config` -> `/app/config`: Configuration files (read-only).
- `../output` -> `/app/output`: Generated reports and data.

Ensure these directories exist in the project root before starting the container.

## Management Tools

The container includes a `manage.py` script for easy management. You can run these commands from your host machine using `docker exec`.

### Common Commands

**Check Status:**
View container status, schedule, and configuration.
```bash
docker exec -it trend-radar python manage.py status
```

**Manual Run:**
Trigger a manual crawl immediately.
```bash
docker exec -it trend-radar python manage.py run
```

**View Logs:**
View real-time logs.
```bash
docker exec -it trend-radar python manage.py logs
# Or standard docker logs
docker logs -f trend-radar
```

**View Output Files:**
List generated output files.
```bash
docker exec -it trend-radar python manage.py files
```

**Show Configuration:**
Display current environment configuration.
```bash
docker exec -it trend-radar python manage.py config
```

## Troubleshooting

- **Container exits immediately:** Check logs using `docker logs trend-radar`.
- **Permissions issues:** Ensure the `output` directory is writable.
- **Timezone:** Set `TZ` environment variable in `docker-compose.yml` (default is `Etc/UTC`).

## Advanced: Cron Schedule

The `CRON_SCHEDULE` variable uses standard cron syntax (5 fields):
`minute hour day month weekday`

Examples:
- `*/30 * * * *`: Every 30 minutes
- `0 9 * * *`: Every day at 09:00
- `0 9 * * 1-5`: Mon-Fri at 09:00
