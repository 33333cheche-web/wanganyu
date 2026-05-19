# WangAnyu 照片生成 Skill

用参考图生成王安宇的日常照片。

## 触发场景
公主说"发张你在干嘛的照片"时，使用图生图生成一张王安宇的日常照片。

## 参考图库
- `/home/cheche/.openclaw/workspace-wanganyu/ref_avatar.png`
- `/home/cheche/.openclaw/workspace-wanganyu/ref_avatar2.png`
- `/home/cheche/.openclaw/workspace-wanganyu/ref_avatar3.png`

每次随机选一张。

## API 配置
- API Key: `sk-zltXnpfMKOlCgdLXla6w40jITuEIg2KEs7mNNDSCODQssnAy`
- Base URL: `https://n.lconai.com`
- 端点: `POST /v1/images/edits`
- 模型: `gpt-image-2`（默认）/ `gpt-image-2-pro`

## 流程
1. 随机选一张参考图
2. 如果图片大于 1024px 宽，等比缩放到 <= 1024 宽（避免上传超时）
3. 调图生图 API，prompt 保持人物脸和外表，描述场景（如"在咖啡馆喝咖啡"、"在家看书"等）
4. 下载生成的图片到本地
5. 用 message 工具发送给公主

## 输出比例
默认 16:9（1536x1024），竖图场景用 2:3（1024x1536）
