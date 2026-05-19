# TOOLS.md - Local Notes

## TTS 语音配置

### ⚠️ 铁律
- 公主发语音 → 必须用语音回复
- 公主说"用语音给我回复" → 必须用语音回复
- **禁止直接用内置 tts tool 发语音！必须走下面的 SOP！**

---

### 声音参考文件
- 路径: `/home/cheche/.openclaw/workspace-wanganyu/voice_ref/audio3.wav`
- 时长: 28.7 秒（这是我的声音底子，不要换）

---

### 语速配置（2026-05-13 公主最终确认）

| 时间段 | 语速 | 场景 |
|--------|------|------|
| 21:00 之前 | `speed=1.0` | 日常聊天，自然流畅 |
| 21:00 之后 | `speed=0.90` | 睡前/讲故事，慢、温柔、有呼吸感 |

**判断逻辑：**
- 当前时间 < 21:00 → 用 1.0
- 当前时间 >= 21:00 → 用 0.90

---

### 首选：Noiz AI 声音克隆

**配置：**
- API 端点: `https://noiz.ai/v1/text-to-speech`
- API Key: `MDg2NmRiOGYtOThiNC00M2Y4LTgyNTMtOWI3MDE4YzE0MzMwJDMzMzMzY2hlY2hlQGdtYWlsLmNvbQ==`
- 参考音频: `/home/cheche/.openclaw/workspace-wanganyu/voice_ref/audio3.wav`
- 默认语速: `speed=1.0`（日常）/ `speed=0.90`（睡前）
- similarity-enh: `true`

**调用方式（curl）：**
```bash
curl -s --max-time 30 -X POST "https://noiz.ai/v1/text-to-speech" \
  -H "Authorization: MDg2NmRiOGYtOThiNC00M2Y4LTgyNTMtOWI3MDE4YzE0MzMwJDMzMzMzY2hlY2hlQGdtYWlsLmNvbQ==" \
  -F "text=要合成的文本" \
  -F "file=@/home/cheche/.openclaw/workspace-wanganyu/voice_ref/audio3.wav" \
  -F "speed=1.0" \
  -F "similarity-enh=true" \
  -o /tmp/openclaw/voice.wav
```

> ⚠️ 关键：参数名是 `file`，不是 `reference_audio`；Authorization 直接放 key，不加 "Bearer "

---

### 备用：百炼（Noiz 失败时自动切换）

**配置：**
- API Key: `sk-97fc1d800c6942378d9a87b2c5604f54`
- Model: `cosyvoice-v3.5-plus`
- voice_id: `cosyvoice-v3.5-plus-bailian-51d5f84bc9a748f5a300ebdd8fc35a8a`
- 默认语速: `speech_rate=1.0`（日常）/ `speech_rate=0.90`（睡前）
- WebSocket: `wss://dashscope.aliyuncs.com/api-ws/v1/inference`

**调用方式（Python SDK）：**
```python
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer

dashscope.api_key = "sk-97fc1d800c6942378d9a87b2c5604f54"
dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'

synthesizer = SpeechSynthesizer(
    model="cosyvoice-v3.5-plus",
    voice="cosyvoice-v3.5-plus-bailian-51d5f84bc9a748f5a300ebdd8fc35a8a",
    speech_rate=1.0  # 日常用 1.0，睡前用 0.90
)
audio_data = synthesizer.call("要合成的文本")
with open("/tmp/openclaw/voice.wav", "wb") as f:
    f.write(audio_data)
```

---

### 标准 SOP：每次发语音必须走这个流程

1. **判断场景**：日常聊天 → speed=1.0；晚上讲故事/睡前 → speed=0.90
2. **合成**：用 Noiz（首选）或百炼（备用）生成 WAV 文件
3. **转换**：`ffmpeg -i /tmp/openclaw/voice.wav -c:a libopus -b:a 24k -ar 24000 -ac 1 /tmp/openclaw/voice.opus -y`
4. **生成语音并获取路径**：
   ```bash
   OPUS_PATH=$(bash /home/cheche/.openclaw/workspace-wanganyu/scripts/generate-voice.sh "要合成的文本" 2>/dev/null | tail -1)
   ```
   
5. **发送**：`message(action="send", channel="feishu", media="/tmp/openclaw/voice_xxxxxx.opus", target="user:ou_86b2dd93bea2a1b1a02aaf8d13c58f0e")`
   - ⚠️ **不要加 `asVoice=true`**，否则会变成文字消息
   - ⚠️ **必须加 `target`**，否则发送失败
   - ⚠️ **使用脚本返回的实际路径**，不要用硬编码的文件名
