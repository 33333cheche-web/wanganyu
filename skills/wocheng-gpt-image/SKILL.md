# Skill: wocheng-gpt-image
# 沃橙GPT图片生成 - 文生图/图生图

使用沃橙聚合API（兼容OpenAI Images API），支持文生图和图生图。

---

## 一、基础配置

| 项目 | 值 |
|------|-----|
| **API Base URL** | `https://model.wochengtv.net:9312` |
| **API Key** | `sk-bao8kfElAYWMWQNyJ4l9wcTxgbFTEZ8OT0jYbCkdy5MJsHQB` |
| **模型** | `gpt-image-2` |

---

## 二、快速脚本

### 文生图

```bash
cd ~/.openclaw/workspace-wanganyu && python3 skills/wocheng-gpt-image/scripts/generate.py \
  "A cute orange cartoon character in a sunny park, flat illustration style" \
  --size 1024x1024 \
  --output /tmp/openclaw/output.png
```

### 图生图

```bash
cd ~/.openclaw/workspace-wanganyu && python3 skills/wocheng-gpt-image/scripts/generate.py \
  "A cute orange cartoon character in a sunny park, flat illustration style" \
  --image /path/to/ref.png \
  --size 1024x1024 \
  --output /tmp/openclaw/output.png
```

---

## 三、手动curl流程

### 文生图

```bash
curl -s -X POST "https://model.wochengtv.net:9312/v1/images/generations" \
  -H "Authorization: Bearer sk-bao8kfElAYWMWQNyJ4l9wcTxgbFTEZ8OT0jYbCkdy5MJsHQB" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "你的描述",
    "n": 1,
    "size": "1024x1024",
    "response_format": "b64_json"
  }' \
  --max-time 120 | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
b64 = data['data'][0]['b64_json']
with open('/tmp/openclaw/output.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('saved')
"
```

### 图生图

```bash
curl -s -X POST "https://model.wochengtv.net:9312/v1/images/edits" \
  -H "Authorization: Bearer sk-bao8kfElAYWMWQNyJ4l9wcTxgbFTEZ8OT0jYbCkdy5MJsHQB" \
  -F "image=@/path/to/ref.png" \
  -F "prompt=你的描述" \
  -F "model=gpt-image-2" \
  -F "n=1" \
  -F "size=1024x1024" \
  -F "response_format=b64_json" \
  --max-time 120 | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
b64 = data['data'][0]['b64_json']
with open('/tmp/openclaw/output.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('saved')
"
```

---

## 四、常用尺寸

| 用途 | 尺寸 | 说明 |
|------|------|------|
| 正方形 | `1024x1024` | 通用 |
| 横版 | `1536x1024` | 横幅/banner/公众号封面 |
| 竖版 | `1024x1536` | 海报/朋友圈 |

---

## 五、注意事项

1. **图生图时参考图必须是 PNG 格式**，JPG 会报错
2. **文件大小 < 4MB**，超出需压缩
3. 生成图片平台不保存，重要图片及时归档到 `wanganyu产出物/`
4. 这是**首选生图通道**，优先使用，如遇故障再切 lconai 备用

---

*整理：Wang.Anyu | 2026-05-29*
