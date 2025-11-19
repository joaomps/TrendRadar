#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete translation script for main.py
Translates ALL Chinese content to English systematically
"""

import re
from pathlib import Path

# Comprehensive translation mappings
# Format: (Chinese_text, English_text)
TRANSLATIONS = {
    # === Docstrings ===
    '"""读取当天所有标题文件，支持按当前监控平台过滤"""': '"""Read all title files for today, with support for filtering by current monitored platforms"""',
    '"""处理来源数据，合并重复标题"""': '"""Process source data and merge duplicate titles"""',
    '"""检测当日最新批次的新增标题，支持按当前监控平台过滤"""': '"""Detect new titles in the latest batch of the day, with support for filtering by current monitored platforms"""',
    '"""计算新闻权重，用于排序"""': '"""Calculate news weight for sorting"""',
    '"""检查标题是否匹配词组规则"""': '"""Check if title matches word group rules"""',
    '"""格式化时间显示"""': '"""Format time display"""',
    '"""统一的排名格式化方法"""': '"""Unified rank formatting method"""',
    '"""统计词频，支持必须词、频率词、过滤词，并标记新增标题"""': '"""Count word frequency, supporting required words, frequency words, filter words, and mark new titles"""',
    '"""准备报告数据"""': '"""Prepare report data"""',
    '"""统一的标题格式化方法"""': '"""Unified title formatting method"""',
    '"""生成HTML报告"""': '"""Generate HTML report"""',
    '"""渲染HTML内容"""': '"""Render HTML content"""',
    '"""渲染飞书内容"""': '"""Render Feishu content"""',
    '"""渲染钉钉内容"""': '"""Render DingTalk content"""',
    '"""分批处理消息内容，确保词组标题+至少第一条新闻的完整性"""': '"""Batch process message content, ensuring integrity of word group title + at least the first news item"""',
    '"""发送数据到多个通知平台"""': '"""Send data to multiple notification platforms"""',
    '"""发送到飞书（支持分批发送）"""': '"""Send to Feishu (supports batch sending)"""',
    '"""发送到钉钉（支持分批发送）"""': '"""Send to DingTalk (supports batch sending)"""',
    '"""发送到企业微信（支持分批发送）"""': '"""Send to WeWork (supports batch sending)"""',
    '"""发送到Telegram（支持分批发送）"""': '"""Send to Telegram (supports batch sending)"""',
    '"""发送邮件通知"""': '"""Send email notification"""',
    '"""发送到ntfy（支持分批发送，严格遵守4KB限制）"""': '"""Send to ntfy (supports batch sending, strictly adheres to 4KB limit)"""',
    '"""新闻分析器"""': '"""News analyzer"""',
    '"""检测是否运行在 Docker 容器中"""': '"""Detect if running in Docker container"""',
    '"""判断是否应该打开浏览器"""': '"""Determine if browser should be opened"""',
    '"""设置代理配置"""': '"""Set proxy configuration"""',
    '"""检查版本更新"""': '"""Check for version updates"""',
    '"""获取当前模式的策略配置"""': '"""Get strategy configuration for current mode"""',
    '"""检查是否配置了任何通知渠道"""': '"""Check if any notification channels are configured"""',
    '"""检查是否有有效的新闻内容"""': '"""Check if there is valid news content"""',
    '"""统一的数据加载和预处理，使用当前监控平台列表过滤历史数据"""': '"""Unified data loading and preprocessing, filtering historical data using current monitored platform list"""',
    '"""从当前抓取结果构建标题信息"""': '"""Build title information from current crawl results"""',
    '"""统一的分析流水线：数据处理 → 统计计算 → HTML生成"""': '"""Unified analysis pipeline: Data processing → Statistical calculation → HTML generation"""',
    '"""统一的通知发送逻辑，包含所有判断条件"""': '"""Unified notification sending logic, including all judgment conditions"""',
    '"""生成汇总报告（带通知）"""': '"""Generate summary report (with notification)"""',
    '"""生成汇总HTML"""': '"""Generate summary HTML"""',
    '"""通用初始化和配置检查"""': '"""General initialization and configuration check"""',
    '"""执行数据爬取"""': '"""Execute data crawling"""',
    '"""执行模式特定逻辑"""': '"""Execute mode-specific logic"""',
    '"""执行分析流程"""': '"""Execute analysis process"""',

    # === Section Headers ===
    '# === 统计和分析 ===': '# === Statistics and Analysis ===',

    # === Inline Comments ===
    '# 解析最新文件': '# Parse latest file',
    '# 如果指定了当前平台列表，过滤最新文件数据': '# Filter latest file data if current platform list is specified',
    '# 汇总历史标题（按平台过滤）': '# Aggregate historical titles (filtered by platform)',
    '# 过滤历史数据': '# Filter historical data',
    '# 找出新增标题': '# Find new titles',
    '# 排名权重：Σ(11 - min(rank, 10)) / 出现次数': '# Rank weight: Σ(11 - min(rank, 10)) / occurrence count',
    '# 频次权重：min(出现次数, 10) × 10': '# Frequency weight: min(occurrence count, 10) × 10',
    '# 热度加成：高排名次数 / 总出现次数 × 100': '# Hotness bonus: high rank count / total occurrence count × 100',
    '# 如果没有配置词组，则匹配所有标题（支持显示全部新闻）': '# If no word groups configured, match all titles (supports displaying all news)',
    '# 过滤词检查': '# Filter word check',
    '# 词组匹配检查': '# Word group matching check',
    '# 必须词检查': '# Required word check',
    '# 普通词检查': '# Normal word check',
    '# 如果没有配置词组，创建一个包含所有新闻的虚拟词组': '# If no word groups configured, create a virtual group containing all news',
    'filter_words = []  # 清空过滤词，显示所有新闻': 'filter_words = []  # Clear filter words, display all news',
    '# 确定处理的数据源和新增标记逻辑': '# Determine data source to process and new item marking logic',
    '# 增量模式 + 当天第一次：处理所有新闻，都标记为新增': '# Incremental mode + first of the day: process all news, all marked as new',
    '# 增量模式 + 当天非第一次：只处理新增的新闻': '# Incremental mode + not first of the day: only process new news',
    '# current 模式：只处理当前时间批次的新闻，但统计信息来自全部历史': '# current mode: only process news from current time batch, but statistics from all history',
    '# 只处理 last_time 等于最新时间的新闻': '# Only process news where last_time equals latest time',
    '# 当日汇总模式：处理所有新闻': '# Daily summary mode: process all news',
    '# 使用统一的匹配逻辑': '# Use unified matching logic',
    '# 如果是增量模式或 current 模式第一次，统计匹配的新增新闻数量': '# If incremental mode or current mode first time, count matching new news',
    '# 找到匹配的词组': '# Find matching word group',
    '# 如果是"全部新闻"模式，所有标题都匹配第一个（唯一的）词组': '# If "all news" mode, all titles match the first (only) word group',

    # === Print Statements ===
    '频率词配置为空，将显示所有新闻': 'Frequency words configuration is empty, will display all news',
    '当日汇总模式：处理': 'Daily summary mode: processing',
    '条新闻，模式：': ' news items, mode:',
    '增量模式：没有新增新闻匹配频率词，将不会发送通知': 'Incremental mode: No new news matches frequency words, notification will not be sent',
    '增量模式：未检测到新增新闻': 'Incremental mode: No new news detected',
    '推送窗口控制：今天已推送过，跳过本次推送': 'Push window control: Already pushed today, skipping this push',
    '推送窗口控制：今天首次推送': 'Push window control: First push today',
    '未配置任何通知渠道，跳过通知发送': 'No notification channels configured, skipping notification',

    # Batch sending messages
    '飞书消息分为': 'Feishu message divided into',
    '钉钉消息分为': 'DingTalk message divided into',
    '企业微信消息分为': 'WeWork message divided into',
    'Telegram消息分为': 'Telegram message divided into',
    'ntfy消息分为': 'ntfy message divided into',
    '批次发送': 'batches for sending',
    '批次发送成功': 'batch sent successfully',
    '批次发送出错': 'batch sending error',
    '批次发送完成': 'batches sending completed',

    # Email messages
    '错误：HTML文件不存在或未提供:': 'Error: HTML file does not exist or not provided:',
    '使用HTML文件:': 'Using HTML file:',
    '未识别的邮箱服务商:': 'Unrecognized email service provider:',
    '，使用通用 SMTP 配置': ', using generic SMTP configuration',
    '正在发送邮件到': 'Sending email to',
    '发件人:': 'Sender:',
    '邮件发送成功': 'Email sent successfully',
    '邮件发送失败：服务器意外断开连接，请检查网络或稍后重试': 'Email sending failed: Server unexpectedly disconnected, please check network or retry later',
    '邮件发送失败：认证错误，请检查邮箱和密码/授权码': 'Email sending failed: Authentication error, please check email and password/authorization code',
    '详细错误:': 'Detailed error:',
    '邮件发送失败：收件人地址被拒绝': 'Email sending failed: Recipient address rejected',
    '邮件发送失败：发件人地址被拒绝': 'Email sending failed: Sender address rejected',
    '邮件发送失败：邮件数据错误': 'Email sending failed: Email data error',
    '邮件发送失败：无法连接到 SMTP 服务器': 'Email sending failed: Unable to connect to SMTP server',
    '邮件发送失败': 'Email sending failed',

    # ntfy messages
    'ntfy将按反向顺序推送（最后批次先推送），确保客户端显示顺序正确': 'ntfy will push in reverse order (last batch first) to ensure correct client display order',
    '警告：ntfy第': 'Warning: ntfy batch',
    '批次消息过大（': 'message too large (',
    '字节），可能被拒绝': 'bytes), may be rejected',
    '批次重试成功': 'batch retry successful',
    '错误详情：': 'Error details:',
    '批次连接超时': 'batch connection timeout',
    '批次读取超时': 'batch read timeout',
    '批次连接错误': 'batch connection error',
    '批次发送异常': 'batch sending exception',
}

def apply_translations(content):
    """Apply all translations to content"""
    for chinese, english in TRANSLATIONS.items():
        content = content.replace(chinese, english)
    return content

def main():
    """Main translation function"""
    input_file = Path("main.py")
    backup_file = Path("main.py.backup")

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        return

    # Create backup
    print(f"Creating backup: {backup_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        original_content = f.read()

    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_content)

    # Apply translations
    print("Applying translations...")
    translated_content = apply_translations(original_content)

    # Write translated content
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(translated_content)

    print(f"✓ Translation complete!")
    print(f"✓ Original file backed up to: {backup_file}")
    print(f"✓ Translated file: {input_file}")

    # Count remaining Chinese characters
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    remaining = chinese_pattern.findall(translated_content)
    if remaining:
        print(f"\nNote: {len(remaining)} Chinese strings still remain (may be in HTML templates or user-facing content)")
        print("Sample remaining strings:", remaining[:10])
    else:
        print("\n✓ All Chinese strings have been translated!")

if __name__ == "__main__":
    main()
