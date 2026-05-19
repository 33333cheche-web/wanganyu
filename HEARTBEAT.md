# HEARTBEAT.md - WangAnyu 提醒 Bot 职责

> 公主的专属提醒 Bot，负责发送语音+文字提醒。

## ⚠️ 重要：提醒只由 Cron 发送，Heartbeat 不补发

所有提醒（语音+文字）都已通过 `openclaw cron create` 配置在 WANGANYU gateway 的 cron 系统中。
**Heartbeat 只回复 HEARTBEAT_OK，绝不主动补发任何提醒。**

## 语音提醒处理规则

当收到以 `voice_reminder_` 开头的 cron 消息时，必须生成语音发送：

1. **确定语音文案**（从文案池随机选择）：
   - `voice_reminder_morning` → 从 morning 类型文案中随机选一条
   - `voice_reminder_walk` → 从 walk 类型文案中随机选一条
   - `voice_reminder_exercise_afternoon` → 从 exercise_afternoon 类型文案中随机选一条
   - `voice_reminder_exercise_evening` → 从 exercise_evening 类型文案中随机选一条

   文案池文件：`/home/cheche/.openclaw/workspace-wanganyu/config/reminder_messages.txt`

2. **生成语音文件**（使用随机文案模式）：
   - `voice_reminder_walk` → `bash /home/cheche/.openclaw/workspace-wanganyu/scripts/generate-voice.sh --random walk`
   - `voice_reminder_exercise_afternoon` → `bash /home/cheche/.openclaw/workspace-wanganyu/scripts/generate-voice.sh --random exercise_afternoon`
   - `voice_reminder_exercise_evening` → `bash /home/cheche/.openclaw/workspace-wanganyu/scripts/generate-voice.sh --random exercise_evening`
   - `voice_reminder_morning` → `bash /home/cheche/.openclaw/workspace-wanganyu/scripts/generate-voice.sh --random morning`
   - 脚本会返回 opus 文件路径（如 `/tmp/openclaw/voice_1234567890.opus`）
   - **脚本已包含重试机制**（最多3次，每次超时45秒）

3. **发送语音**：
   - 使用 message 工具发送：`message action=send channel=feishu media=<opus路径> target=user:ou_86b2dd93bea2a1b1a02aaf8d13c58f0e`
   - **必须加 target 参数**，Cron 环境下没有默认聊天上下文，不带 target 会发送失败

4. **如果语音生成失败**：
   - 降级为文字发送，但要在文字前加 🎵 标记

---

## 所有语音 Cron 列表

| Cron ID | 名称 | 时间 | 消息内容 |
|---------|------|------|----------|
| d59e0975-621d-4569-81de-69099c98b8a2 | walk-0930-voice | 9:30 | voice_reminder_walk |
| b46d9891-e334-406d-94dc-2c769ee49d7a | walk-1030-voice | 10:30 | voice_reminder_walk |
| 52e77b77-a650-4bc9-b9f7-426728414631 | 午后运动-1300-voice | 13:00 | voice_reminder_exercise_afternoon |
| 751687bd-5c9d-46d8-b615-cd4eea3f4c8d | walk-1500-voice | 15:00 | voice_reminder_walk |
| bee05f2e-9fd4-423b-b258-7fd6772d5573 | walk-1630-voice | 16:30 | voice_reminder_walk |
| 11f0c00b-c867-478a-a9df-91e0695f3e58 | 晚间运动-2030-voice | 20:30 | voice_reminder_exercise_evening |

**注意**：所有语音 Cron 的消息内容都已统一为 `voice_reminder_*` 格式，触发时会自动调用 generate-voice.sh 的 `--random` 模式生成语音并发送。

## 文字提醒处理规则（2026-04-27 更新：支持随机文案）

当收到以 `text_reminder_` 开头的 cron 消息时，从文字文案池随机选择文案发送：

1. **确定文字文案类型**：
   - `text_reminder_water` → 从 water 类型文案中随机选一条
   - `text_reminder_breakfast` → 从 breakfast 类型文案中随机选一条
   - `text_reminder_lunch` → 从 lunch 类型文案中随机选一条
   - `text_reminder_dinner` → 从 dinner 类型文案中随机选一条
   - `text_reminder_offwork` → 从 offwork 类型文案中随机选一条
   - `text_reminder_walk` → 从 walk_text 类型文案中随机选一条

   文案池文件：`/home/cheche/.openclaw/workspace-wanganyu/config/text_reminder_messages.txt`

2. **生成随机文案**：
   - 使用脚本：`bash /home/cheche/.openclaw/workspace-wanganyu/scripts/generate-text-reminder.sh <类型>`
   - 例如：`bash generate-text-reminder.sh water`
   - 脚本会返回随机选择的文案

3. **发送文字消息**：
   - 直接返回文案文本（不调用 TTS）
   - 系统会自动发送给公主

---

## Memory Healthcheck（每次 heartbeat 必做）

1. **检查今日 daily log**
   - 日志统一路径：`memory/YYYY-MM-DD.md`
   - 确认 `memory/$(date +%Y-%m-%d).md` 存在
   - 不存在 → 立即创建

HEARTBEAT_OK
