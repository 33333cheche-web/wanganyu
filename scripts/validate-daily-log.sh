#!/usr/bin/env bash
# 校验 daily log：每行必须以 #P0/#P1/#P2 开头，且单行不超过 80 字符。
set -euo pipefail

MEMORY_DIR="/home/cheche/.openclaw/workspace-wanganyu/memory"
TARGET="${1:-${MEMORY_DIR}/$(date '+%Y-%m-%d').md}"

if [[ "$TARGET" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  TARGET="${MEMORY_DIR}/${TARGET}.md"
fi

if [[ ! -f "$TARGET" ]]; then
  echo "ERROR: file not found: $TARGET"
  exit 2
fi

awk '
BEGIN { bad=0; tagged=0 }
/^#P[012] / {
  tagged++
  if (length($0) > 80) {
    bad++
    printf "LONG line %d len=%d: %s\n", NR, length($0), $0
  }
  next
}
{
  bad++
  printf "UNTAGGED line %d len=%d: %s\n", NR, length($0), $0
}
END {
  printf "tagged=%d bad=%d\n", tagged, bad
  if (tagged == 0 || bad > 0) exit 1
}
' "$TARGET"
