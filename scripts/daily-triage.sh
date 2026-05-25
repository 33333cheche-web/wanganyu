#!/bin/bash
# ============================================================
# WangAnyu Memory Daily Triage - 每日 P0/P1/P2 自动分拣脚本
# 扫描 daily log，先校验格式，再按标签分发到 P0/P1/P2 月度文件
# cron: 每天 23:59 或每小时检查一次
# ============================================================
set -euo pipefail

log() {
    echo "[$(date '+%F %T')] $*"
}

# 获取日期（默认昨天）
TARGET_DATE="${1:-$(date -d 'yesterday' '+%Y-%m-%d')}"
TODAY_DATE="$(date '+%Y-%m-%d')"

MEMORY_DIR="/home/cheche/.openclaw/workspace-wanganyu/memory"
# 原生读取模式：daily 文件存放在根目录
DAILY_FILE="$MEMORY_DIR/${TARGET_DATE}.md"
# 兼容旧路径（daily/子目录）
OLD_DAILY_FILE="$MEMORY_DIR/daily/${TARGET_DATE}.md"
P0_DIR="$MEMORY_DIR/P0"
P1_DIR="$MEMORY_DIR/P1"
P2_DIR="$MEMORY_DIR/P2"
VALIDATOR="/home/cheche/.openclaw/workspace-wanganyu/scripts/validate-daily-log.sh"

mkdir -p "$P0_DIR" "$P1_DIR" "$P2_DIR"

# 提取年月（用于月度归档文件名）
YEAR_MONTH="${TARGET_DATE:0:7}"  # 2026-04

log "开始分拣: $TARGET_DATE"

# 检查今天是否已经分拣过（避免重复）
P0_FILE="$P0_DIR/${YEAR_MONTH}.md"
if [[ -f "$P0_FILE" ]] && grep -q "📅 ${TARGET_DATE}" "$P0_FILE" 2>/dev/null; then
    log "⚠️  ${TARGET_DATE} 已分拣过，跳过"
    exit 0
fi

# 检查目标文件（优先根目录，兼容旧路径）
if [[ -f "$DAILY_FILE" ]]; then
    SOURCE_FILE="$DAILY_FILE"
    log "使用根目录文件: $DAILY_FILE"
elif [[ -f "$OLD_DAILY_FILE" ]]; then
    SOURCE_FILE="$OLD_DAILY_FILE"
    log "使用旧路径文件: $OLD_DAILY_FILE"
else
    log "文件不存在: $DAILY_FILE 或 $OLD_DAILY_FILE，跳过"
    exit 0
fi

# 分拣前强制校验：每行必须以 #P0/#P1/#P2 开头，且不超过 80 字符
if [[ -x "$VALIDATOR" ]]; then
    if ! "$VALIDATOR" "$SOURCE_FILE"; then
        log "❌ daily log 格式不合规，停止分拣: $SOURCE_FILE"
        exit 1
    fi
else
    log "❌ 校验脚本不存在或不可执行: $VALIDATOR"
    exit 1
fi

# 分拣函数：提取指定标签行，追加到月度文件
triage_tag() {
    local tag="$1"       # #P0, #P1, #P2
    local target_dir="$2"
    local label="$3"     # P0, P1, P2

    local target_file="$target_dir/${YEAR_MONTH}.md"

    # 提取所有该标签行（去掉标签本身前面的 #P0 格式，保留完整行）
    # 格式: #P0 09:27 内容描述
    grep -E "^${tag}[[:space:]]" "$SOURCE_FILE" > /tmp/triage_${label}_tmp.txt 2>/dev/null

    if [[ -s /tmp/triage_${label}_tmp.txt ]]; then
        # 追加到月度文件（带日期分隔符）
        {
            echo ""
            echo "## 📅 ${TARGET_DATE}"
            cat /tmp/triage_${label}_tmp.txt
        } >> "$target_file"

        local count=$(wc -l < /tmp/triage_${label}_tmp.txt)
        log "✅ $label: +${count} 条 → $target_file"
        rm /tmp/triage_${label}_tmp.txt
    else
        log "⏭️  $label: 无新记录"
    fi
}

# 执行分拣
triage_tag "#P0" "$P0_DIR" "P0"
triage_tag "#P1" "$P1_DIR" "P1"
triage_tag "#P2" "$P2_DIR" "P2"

log "分拣完成: $TARGET_DATE"
