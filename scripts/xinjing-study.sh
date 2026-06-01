#!/bin/bash
# ============================================================
# 心经学习 cron 触发脚本（实时生成版）
# 触发时调用 AI 生成内容，不再依赖预存文件
# ============================================================
set -euo pipefail

WORKSPACE_DIR="/home/cheche/.openclaw/workspace-wanganyu"
PROGRESS_FILE="$WORKSPACE_DIR/memory/xinjing_progress.md"

# 获取当前学习进度
day=1
if [[ -f "$PROGRESS_FILE" ]]; then
    day=$(grep -oE "第[0-9]+天" "$PROGRESS_FILE" | grep -oE "[0-9]+" | tail -1 || echo "1")
fi

# 主函数
case "${1:-}" in
    trigger)
        # cron 触发时，输出标记让上层调用 AI 生成
        echo "XINJING_TRIGGER_DAY_${day}"
        ;;
    next)
        # 更新进度到下一关
        next_day=$((day + 1))
        echo "第 ${next_day} 天" > "$PROGRESS_FILE"
        echo "已更新进度到第 ${next_day} 天"
        ;;
    progress)
        echo "当前进度：第 ${day} 天"
        ;;
    *)
        echo "用法: $0 {trigger|next|progress}"
        echo "  trigger  - cron 触发，输出当天标记"
        echo "  next     - 推进到下一关"
        echo "  progress - 查看当前进度"
        exit 1
        ;;
esac