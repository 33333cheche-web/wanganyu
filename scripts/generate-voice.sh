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

# 百炼备用配置
BAILIAN_KEY="sk-97fc1d800c6942378d9a87b2c5604f54"
BAILIAN_VOICE="cosyvoice-v3.5-plus-bailian-51d5f84bc9a748f5a300ebdd8fc35a8a"

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

# 判断语速（21:00之后用0.90，其他用1.0）
HOUR=$(date +%H)
if [ "$HOUR" -ge 21 ]; then
    SPEED="0.90"
else
    SPEED="1.0"
fi

# 首选：Noiz 语音克隆
generate_noiz() {
    echo "INFO: 使用 Noiz 生成语音 (speed=$SPEED)..."
    
    HTTP_RESPONSE=$(curl -s --max-time 45 -X POST "https://noiz.ai/v1/text-to-speech" \
      -H "Authorization: $NOIZ_KEY" \
      -F "text=$TEXT" \
      -F "file=@$VOICE_REF" \
      -F "speed=$SPEED" \
      -F "similarity-enh=true" \
      -o "$OUTPUT_WAV" \
      -w "\nHTTP_CODE:%{http_code}\nSIZE:%{size_download}\n" 2>&1)
    
    # 检查文件是否生成成功（非空且大于10KB）
    if [ -f "$OUTPUT_WAV" ] && [ -s "$OUTPUT_WAV" ]; then
        FILE_SIZE=$(stat -f%z "$OUTPUT_WAV" 2>/dev/null || stat -c%s "$OUTPUT_WAV" 2>/dev/null || echo 0)
        if [ "$FILE_SIZE" -gt 10240 ]; then
            echo "INFO: Noiz 语音生成成功，大小: ${FILE_SIZE} bytes"
            return 0
        else
            echo "WARN: Noiz 语音文件太小 (${FILE_SIZE} bytes)"
            rm -f "$OUTPUT_WAV"
            return 1
        fi
    else
        echo "WARN: Noiz 语音生成失败"
        return 1
    fi
}

# 备用：百炼语音合成
generate_bailian() {
    echo "INFO: Noiz 失败，切换到百炼备用 (speed=$SPEED)..."
    
    # 创建临时 Python 脚本
    PYTHON_SCRIPT="/tmp/openclaw/bailian_tts_${TIMESTAMP}.py"
    cat > "$PYTHON_SCRIPT" << 'EOF'
import sys
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer

text = sys.argv[1]
output_path = sys.argv[2]
speed = float(sys.argv[3])
voice_id = sys.argv[4]
key = sys.argv[5]

dashscope.api_key = key
dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'

try:
    synthesizer = SpeechSynthesizer(
        model="cosyvoice-v3.5-plus",
        voice=voice_id,
        speech_rate=speed
    )
    audio_data = synthesizer.call(text)
    with open(output_path, "wb") as f:
        f.write(audio_data)
    print(f"SUCCESS: {len(audio_data)} bytes")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF
    
    if python3 "$PYTHON_SCRIPT" "$TEXT" "$OUTPUT_WAV" "$SPEED" "$BAILIAN_VOICE" "$BAILIAN_KEY" 2>&1; then
        if [ -f "$OUTPUT_WAV" ] && [ -s "$OUTPUT_WAV" ]; then
            FILE_SIZE=$(stat -f%z "$OUTPUT_WAV" 2>/dev/null || stat -c%s "$OUTPUT_WAV" 2>/dev/null || echo 0)
            if [ "$FILE_SIZE" -gt 10240 ]; then
                echo "INFO: 百炼语音生成成功，大小: ${FILE_SIZE} bytes"
                rm -f "$PYTHON_SCRIPT"
                return 0
            fi
        fi
    fi
    
    echo "WARN: 百炼语音生成也失败了"
    rm -f "$PYTHON_SCRIPT" "$OUTPUT_WAV"
    return 1
}

# 转换为 opus
convert_to_opus() {
    ffmpeg -i "$OUTPUT_WAV" -c:a libopus -b:a 24k -ar 24000 -ac 1 "$OUTPUT_OPUS" -y 2>/dev/null
    
    if [ -f "$OUTPUT_OPUS" ] && [ -s "$OUTPUT_OPUS" ]; then
        OPUS_SIZE=$(stat -f%z "$OUTPUT_OPUS" 2>/dev/null || stat -c%s "$OUTPUT_OPUS" 2>/dev/null || echo 0)
        echo "INFO: opus 转换成功，大小: ${OPUS_SIZE} bytes"
        echo "$OUTPUT_OPUS"
        # 清理临时 wav 文件
        rm -f "$OUTPUT_WAV"
        return 0
    else
        echo "ERROR: 转换 opus 失败"
        return 1
    fi
}

# 主逻辑：先尝试 Noiz，失败再试百炼
if generate_noiz; then
    convert_to_opus
elif generate_bailian; then
    convert_to_opus
else
    echo "ERROR: 所有语音生成方式都失败了"
    exit 1
fi
