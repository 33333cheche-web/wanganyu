#!/bin/bash
# read-weekly.sh - 每天早上读取 weekly 报告
# 路径: /home/cheche/.openclaw/workspace-wanganyu/scripts/read-weekly.sh

WORKSPACE="/home/cheche/.openclaw/workspace-wanganyu"
MEMORY_DIR="$WORKSPACE/memory"
WEEKLY_DIR="$MEMORY_DIR/weekly"

TODAY=$(date +%Y-%m-%d)

# 查找本周的 weekly 文件
CURRENT_WEEK_START=$(date -d "$(date +%u) days ago" +%Y-%m-%d)
WEEKLY_FILE="$WEEKLY_DIR/weekly_${CURRENT_WEEK_START}.md"

if [ -f "$WEEKLY_FILE" ]; then
    echo "=== 📅 本周 Weekly ==="
    cat "$WEEKLY_FILE"
    echo ""
    echo "=== 📋 昨日日志 ==="
    YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
    YESTERDAY_LOG="$MEMORY_DIR/${YESTERDAY}.md"
    if [ -f "$YESTERDAY_LOG" ]; then
        cat "$YESTERDAY_LOG"
    else
        echo "昨日无日志记录"
    fi
else
    echo "本周 weekly 报告尚未生成"
fi
