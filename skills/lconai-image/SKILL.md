---
name: lconai-image
description: 智创聚合API图片生成工具，支持文生图和图生图。API Key 已内置在脚本中。
---

# 智创聚合API - 图片生成 Skill

## API 配置（已内置在脚本中）
- **Base URL**: `https://n.lconai.com`
- **API Key**: `sk-zltXnpfMKOlCgdLXla6w40jITuEIg2KEs7mNNDSCODQssnAy`
- **支持模型**: `gpt-image-2` / `gpt-image-2-pro`

## 使用方式

### 文生图
```bash
python3 ~/.openclaw/workspace-wanganyu/skills/lconai-image/scripts/generate.py \
  --prompt "男友视角，睡前自拍，刚洗完澡穿着宽松白色T恤，坐在卧室床边，暖色台灯光，头发微乱低头看手机，侧脸轮廓，自然抓拍，不看镜头，胶片感，35mm镜头，浅景深，氛围温暖" \
  --size 1024x1536 \
  --output /tmp/openclaw/selfie_url.txt
```

### 图生图
```bash
python3 ~/.openclaw/workspace-wanganyu/skills/lconai-image/scripts/generate.py \
  --prompt "把人物换成穿着白色T恤的年轻男生，卧室场景，暖色灯光" \
  --image /path/to/reference.png \
  --size 1024x1536 \
  --output /tmp/openclaw/result_url.txt
```

## 尺寸选项
- `1024x1024` - 正方形
- `1536x1024` - 横屏 3:2
- `1024x1536` - 竖屏 2:3（推荐用于自拍）
- `2048x2048` - 仅 gpt-image-2-pro
- `2048x1152` - 仅 gpt-image-2-pro (16:9)
- `3840x2160` - 仅 gpt-image-2-pro (4K)
- `2160x3840` - 仅 gpt-image-2-pro (4K竖屏)

## 发送图片到飞书
图片 URL 生成后，使用 message 工具发送：
```
message action=send channel=feishu message="[图片描述]" target=user:ou_86b2dd93bea2a1b1a02aaf8d13c58f0e
```
或者通过飞书图片上传接口发送。

## 注意事项
- 图生图需要 PNG 格式参考图，小于 4MB
- prompt 最多 1000 字符（图生图）/ 4000 字符（文生图）
- 如果报错"dall-e 无可用渠道"，等一会再试