#!/bin/bash
# WangAnyu 照片生成脚本
# 用参考图生成王安宇的日常照片

set -e

API_KEY="sk-zltXnpfMKOlCgdLXla6w40jITuEIg2KEs7mNNDSCODQssnAy"
BASE_URL="https://n.lconai.com"
WORKSPACE="/home/cheche/.openclaw/workspace-wanganyu"
COUNTER_FILE="/tmp/openclaw/ref_counter.txt"

# 参考图列表
REF_FILES=("$WORKSPACE/ref_avatar.png" "$WORKSPACE/ref_avatar2.png" "$WORKSPACE/ref_avatar3.png" "$WORKSPACE/ref_avatar4.jpg" "$WORKSPACE/ref_avatar5.jpg" "$WORKSPACE/ref_avatar6.jpg")

# 轮询选择参考图（确保每张都用上，不重复）
if [ -f "$COUNTER_FILE" ]; then
    COUNTER=$(cat "$COUNTER_FILE")
else
    COUNTER=0
fi

RANDOM_IDX=$((COUNTER % ${#REF_FILES[@]}))
REF_IMAGE="${REF_FILES[$RANDOM_IDX]}"
echo "Using reference [$RANDOM_IDX]: $REF_IMAGE"

# 更新计数器
NEXT_COUNTER=$(((COUNTER + 1) % ${#REF_FILES[@]}))
echo "$NEXT_COUNTER" > "$COUNTER_FILE"

# 检查并缩放图片（如果宽大于1024）
python3 << EOF
from PIL import Image
import sys
img = Image.open("$REF_IMAGE")
w, h = img.size
print(f"Original size: {w}x{h}")
if w > 1024:
    new_w = 1024
    new_h = int(h * (1024.0 / w))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    print(f"Resized to: {new_w}x{new_h}")
img.save("/tmp/openclaw/ref_for_upload.png", "PNG")
EOF

REF_FOR_UPLOAD="/tmp/openclaw/ref_for_upload.png"

# 第一参数是场景描述
SCENE="${1:-sitting at a desk working on laptop, warm evening lighting, realistic photo style}"

# 随机选择角度和构图变化
ANGLE_OPTIONS=(
    "natural candid shot, slightly off-center"
    "medium shot, looking slightly away from camera"
    "close-up portrait, soft focus background"
    "three-quarter view, natural pose"
    "over-the-shoulder angle, casual composition"
    "eye-level shot, relaxed expression"
)
ANGLE_IDX=$((RANDOM % ${#ANGLE_OPTIONS[@]}))
ANGLE="${ANGLE_OPTIONS[$ANGLE_IDX]}"

# 调用图生图 API
# 使用 image 模式（非 pro），1k 分辨率
# 加强面部保持权重
FACE_WEIGHT="CRITICAL: Preserve the exact same face, facial structure, eyes, nose, mouth, and skin tone from the reference image. Do NOT change the face."

FULL_PROMPT="${FACE_WEIGHT} Keep the person's face and appearance exactly the same, ${SCENE}, ${ANGLE}, realistic photo style"

echo "Calling API with prompt: $FULL_PROMPT"
RESPONSE=$(curl -s --max-time 120 -X POST "$BASE_URL/v1/images/edits" \
  -H "Authorization: Bearer $API_KEY" \
  -F "image=@$REF_FOR_UPLOAD" \
  -F "prompt=${FULL_PROMPT}" \
  -F "model=gpt-image-2" \
  -F "n=1" \
  -F "size=1024x1024" \
  -F "response_format=url")

echo "Response: $RESPONSE"

# 提取 URL（取第一张）
IMAGE_URL=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][0]['url'])")

# 下载图片（带重试）
OUTPUT_PNG="/tmp/openclaw/wanganyu_photo_$(date +%s).png"
for i in 1 2 3; do
    curl -s --max-time 60 "$IMAGE_URL" -o "$OUTPUT_PNG"
    FILE_SIZE=$(stat -c%s "$OUTPUT_PNG" 2>/dev/null || echo 0)
    if [ "$FILE_SIZE" -gt 10000 ]; then
        echo "Downloaded successfully: $FILE_SIZE bytes"
        break
    else
        echo "Retry $i..."
        sleep 2
    fi
done

# 转换成 JPG 确保兼容性
OUTPUT_FILE="/tmp/openclaw/wanganyu_photo_$(date +%s).jpg"
python3 << EOF
from PIL import Image
img = Image.open("$OUTPUT_PNG")
# 转换 RGBA 到 RGB（JPG 不支持透明）
if img.mode == 'RGBA':
    img = img.convert('RGB')
img.save("$OUTPUT_FILE", "JPEG", quality=95)
print(f"Converted to JPG: {OUTPUT_FILE}")
EOF

# 验证图片
file "$OUTPUT_FILE"
echo "Image saved to: $OUTPUT_FILE"
echo "$OUTPUT_FILE"