#!/bin/bash
# WangAnyu 文字提醒随机文案生成脚本
# 用法: bash generate-text-reminder.sh <提醒类型>
# 输出: 随机选择的文案（直接输出到stdout）

# 配置
MESSAGES_FILE="/home/cheche/.openclaw/workspace-wanganyu/config/text_reminder_messages.txt"

# 检查参数
if [ -z "$1" ]; then
    echo "用法: bash generate-text-reminder.sh <提醒类型>"
    echo "支持类型: water, breakfast, lunch, dinner, offwork, walk_text"
    exit 1
fi

REMINDER_TYPE="$1"

# 检查文案池文件
if [ ! -f "$MESSAGES_FILE" ]; then
    echo "ERROR: 文案池文件不存在: $MESSAGES_FILE"
    exit 1
fi

# 读取该类型的所有文案，随机选择一条
TEXT=$(grep "^${REMINDER_TYPE}|" "$MESSAGES_FILE" | cut -d'|' -f2 | shuf -n 1)

if [ -z "$TEXT" ]; then
    echo "ERROR: 未找到类型 '${REMINDER_TYPE}' 的文案"
    exit 1
fi

# 直接输出文案（用于cron任务读取）
echo "$TEXT"
