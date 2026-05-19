---
name: minimax-understand-image
description: 使用 MiniMax MCP 进行图像理解和分析。触发条件：(1) 用户要求分析图片，理解图像、描述图片内容 (2) 需要识别图片中的物体、文字、场景 (3) 使用 MiniMax 的 understand_image 功能
---

# minimax-understand-image

使用 MiniMax MCP 服务器进行图像理解和分析。

## 前置依赖

1. **uvx**: `which uvx` 确认已安装
2. **MCP 服务器**: `uvx minimax-coding-plan-mcp --help` 确认可用
3. **API Key**: `~/.openclaw/config/minimax.json` 中配置了 MiniMax API Key

## 使用方式

```bash
python3 {curDir}/scripts/understand_image.py <图片路径或URL> "<对图片的提问>"
```

## 示例

```bash
# 描述图片内容
python3 {curDir}/scripts/understand_image.py ~/image.jpg "详细描述这张图片的内容"

# 使用 URL
python3 {curDir}/scripts/understand_image.py "https://example.com/image.jpg" "这张图片展示了什么？"
```
