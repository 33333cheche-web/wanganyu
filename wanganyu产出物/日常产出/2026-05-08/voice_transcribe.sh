#!/bin/bash
# WANGANYU 语音转文字脚本
# 使用本地 OpenAI Whisper

AUDIO_FILE="$1"
if [ -z "$AUDIO_FILE" ]; then
    echo "Usage: $0 <audio_file>"
    exit 1
fi

# 转换为 wav（whisper 需要）
TEMP_WAV="/tmp/whisper_$$.wav"
ffmpeg -i "$AUDIO_FILE" -ar 16000 -ac 1 -c:a pcm_s16le "$TEMP_WAV" -y 2>/dev/null

# 使用 whisper 转录
whisper "$TEMP_WAV" --model tiny --language Chinese --output_format txt --output_dir /tmp 2>/dev/null

# 读取结果
TXT_FILE="/tmp/whisper_$$.txt"
if [ -f "$TXT_FILE" ]; then
    cat "$TXT_FILE"
    rm -f "$TXT_FILE"
else
    # 尝试直接输出
    whisper "$TEMP_WAV" --model tiny --language Chinese 2>/dev/null | tail -5
fi

rm -f "$TEMP_WAV"
