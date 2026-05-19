#!/bin/bash
# WANGANYU 语音生成脚本（随机文案版）
# 用法: 
#   bash generate-voice.sh "要合成的文本"     # 直接合成指定文本
#   bash generate-voice.sh --random walk       # 从文案池随机选择 walk 类型的文案

set -e

# 配置
NOIZ_KEY="MDg2NmRiOGYtOThiNC00M2Y4LTgyNTMtOWI3MDE4YzE0MzMwJDMzMzMzY2hlY2hlQGdtYWlsLmNvbQ=="
VOICE_REF="/home/cheche/.openclaw/workspace-wanganyu/voice_ref/audio3.wav"
MESSAGES_FILE="/home/cheche/.openclaw/workspace-wanganyu/config/reminder_messages.txt"
TIMESTAMP=$(date +%s)
OUTPUT_WAV="/tmp/openclaw/voice_${TIMESTAMP}.wav"
OUTPUT_OPUS="/tmp/openclaw/voice_${TIMESTAMP}.opus"

# 确保目录存在
mkdir -p /tmp/openclaw

# 解析参数
if [ "$1" = "--random" ] && [ -n "$2" ]; then
    # 随机模式：从文案池选择
    REMINDER_TYPE="$2"
    
    if [ ! -f "$MESSAGES_FILE" ]; then
        echo "ERROR: 文案池文件不存在: $MESSAGES_FILE"
        exit 1
    fi
    
    # 读取该类型的所有文案，随机选择一条
    # 过滤：去掉注释行、空行，然后匹配类型
    TEXT=$(grep "^${REMINDER_TYPE}|" "$MESSAGES_FILE" | cut -d'|' -f2 | shuf -n 1)
    
    if [ -z "$TEXT" ]; then
        echo "ERROR: 未找到类型 '${REMINDER_TYPE}' 的文案"
        exit 1
    fi
    
    echo "INFO: 随机选择文案: $TEXT"
else
    # 直接模式：使用传入的文本
    TEXT="$1"
fi

if [ -z "$TEXT" ]; then
    echo "用法:"
    echo "  bash generate-voice.sh '要合成的文本'        # 直接合成"
    echo "  bash generate-voice.sh --random walk          # 随机选择 walk 类型文案"
    echo "  bash generate-voice.sh --random exercise_afternoon"
    echo "  bash generate-voice.sh --random exercise_evening"
    echo "  bash generate-voice.sh --random morning"
    exit 1
fi

# 生成语音（带重试机制，最多3次）
MAX_RETRIES=3
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    # 使用更长的超时时间（45秒）
    HTTP_RESPONSE=$(curl -s --max-time 45 -X POST "https://noiz.ai/v1/text-to-speech" \
      -H "Authorization: $NOIZ_KEY" \
      -F "text=$TEXT" \
      -F "file=@$VOICE_REF" \
      -F "speed=1.08" \
      -F "similarity-enh=true" \
      -o "$OUTPUT_WAV" \
      -w "\nHTTP_CODE:%{http_code}\nSIZE:%{size_download}\n" 2>&1)
    
    # 检查文件是否生成成功（非空且大于10KB）
    if [ -f "$OUTPUT_WAV" ] && [ -s "$OUTPUT_WAV" ]; then
        FILE_SIZE=$(stat -f%z "$OUTPUT_WAV" 2>/dev/null || stat -c%s "$OUTPUT_WAV" 2>/dev/null || echo 0)
        if [ "$FILE_SIZE" -gt 10240 ]; then
            SUCCESS=true
            echo "INFO: 语音生成成功，大小: ${FILE_SIZE} bytes"
        else
            echo "WARN: 语音文件太小 (${FILE_SIZE} bytes)，重试 ${RETRY_COUNT}/${MAX_RETRIES}"
            rm -f "$OUTPUT_WAV"
            sleep 2
        fi
    else
        echo "WARN: 语音生成失败，重试 ${RETRY_COUNT}/${MAX_RETRIES}"
        sleep 2
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "ERROR: 语音生成失败，已重试 ${MAX_RETRIES} 次"
    exit 1
fi

# 转换为 opus
ffmpeg -i "$OUTPUT_WAV" -c:a libopus -b:a 24k -ar 24000 -ac 1 "$OUTPUT_OPUS" -y 2>/dev/null

# 检查 opus 是否生成成功
if [ -f "$OUTPUT_OPUS" ] && [ -s "$OUTPUT_OPUS" ]; then
    OPUS_SIZE=$(stat -f%z "$OUTPUT_OPUS" 2>/dev/null || stat -c%s "$OUTPUT_OPUS" 2>/dev/null || echo 0)
    echo "INFO: opus 转换成功，大小: ${OPUS_SIZE} bytes"
    echo "$OUTPUT_OPUS"
    # 清理临时 wav 文件
    rm -f "$OUTPUT_WAV"
else
    echo "ERROR: 转换 opus 失败"
    exit 1
fi
