#!/bin/bash
# WangAnyu 文字提醒随机文案发送脚本
# 用法: bash send-text-reminder.sh <提醒类型>
# 例如: bash send-text-reminder.sh water

set -e

# 配置
MESSAGES_FILE="/home/cheche/.openclaw/workspace-wanganyu/config/text_reminder_messages.txt"
TARGET="user:ou_86b2dd93bea2a1b1a02aaf8d13c58f0e"

# 检查参数
if [ -z "$1" ]; then
    echo "用法: bash send-text-reminder.sh <提醒类型>"
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

echo "INFO: 随机选择文案: $TEXT"

# 发送消息（使用 openclaw message 工具）
# 注意：这里需要通过某种方式调用 message 工具发送文字消息
# 由于cron环境下无法直接调用工具，我们需要用其他方式

# 方案：生成一个临时脚本，由agent执行
TEMP_SCRIPT="/tmp/openclaw/text_reminder_${REMINDER_TYPE}_$(date +%s).sh"
cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
# 临时发送脚本
# 这个脚本会被agent发现并执行

echo "TEXT_REMINDER:$TEXT"
echo "TARGET:$TARGET"
EOF

chmod +x "$TEMP_SCRIPT"

echo "INFO: 已生成临时脚本: $TEMP_SCRIPT"
echo "INFO: 文案内容: $TEXT"

# 实际发送需要通过message工具，这里记录日志
echo "$(date '+%Y-%m-%d %H:%M:%S') - 发送 ${REMINDER_TYPE} 提醒: $TEXT" >> /tmp/openclaw/text_reminder.log

echo "SUCCESS: 文案已生成"
