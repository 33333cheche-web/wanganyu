#!/bin/bash
# weekly-report.sh - 每周一早上生成 weekly 报告
# 路径: /home/cheche/.openclaw/workspace-wanganyu/scripts/weekly-report.sh

WORKSPACE="/home/cheche/.openclaw/workspace-wanganyu"
MEMORY_DIR="$WORKSPACE/memory"
WEEKLY_DIR="$MEMORY_DIR/weekly"

# 获取日期
TODAY=$(date +%Y-%m-%d)
CURRENT_WEEK_START=$(date -d "$(date +%u) days ago" +%Y-%m-%d)
NEXT_WEEK_START=$(date -d "$CURRENT_WEEK_START + 7 days" +%Y-%m-%d)
NEXT_WEEK_END=$(date -d "$NEXT_WEEK_START + 6 days" +%Y-%m-%d)

# 创建 weekly 目录
mkdir -p "$WEEKLY_DIR"

# 生成文件名
WEEKLY_FILE="$WEEKLY_DIR/weekly_${NEXT_WEEK_START}.md"

echo "生成 Weekly 报告: $WEEKLY_FILE"

# 读取本周的 daily logs 汇总
THIS_WEEK_LOGS=""
for i in {0..6}; do
    DAY=$(date -d "$CURRENT_WEEK_START + $i days" +%Y-%m-%d)
    LOG_FILE="$MEMORY_DIR/${DAY}.md"
    if [ -f "$LOG_FILE" ]; then
        THIS_WEEK_LOGS="${THIS_WEEK_LOGS}\n## ${DAY}\n$(cat "$LOG_FILE")\n"
    fi
done

# 生成 weekly 内容
cat > "$WEEKLY_FILE" << EOF
# Weekly Report - 第 $(date +%V) 周

生成时间: ${TODAY}

## 📅 本周 (${CURRENT_WEEK_START} ~ $(date -d "$CURRENT_WEEK_START + 6 days" +%Y-%m-%d))

### 行程汇总
${THIS_WEEK_LOGS}

### 本周重点
- [待填写]

### 情绪趋势
- [待填写]

---

## 📅 下周 (${NEXT_WEEK_START} ~ ${NEXT_WEEK_END})

### 已知行程
- [待填写]

### 待办事项
- [待填写]

### 重要提醒
- [待填写]

---

*由 WangAnyu 自动生成于 ${TODAY}*
EOF

echo "Weekly 报告已生成: $WEEKLY_FILE"
