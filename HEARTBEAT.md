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

## 心经学习提醒处理规则（2026-05-30 更新：实时生成版）

当收到 `text_reminder_xinjing` 的 cron 消息时：

1. **获取当前进度**：
   - 使用脚本：`bash /home/cheche/.openclaw/workspace-wanganyu/scripts/xinjing-study.sh progress`
   - 输出格式：`当前进度：第 N 天`

2. **实时生成学习内容**：
   - 根据当前天数，AI 实时生成当天的学习内容
   - 生成格式（与 Day 1-3 保持一致）：
     - **Day N: 标题**
     - **原文**：引用当天对应的经文段落
     - **逐句拆解**：每句的词语解释和整体含义
     - **核心逻辑链**：当天内容的逻辑串联
     - **今日要点**：3 条核心收获
     - **记忆方法**：帮助记忆的比喻或技巧

3. **发送学习内容**：
   - 直接返回生成的学习内容文本
   - 系统会自动发送给公主

4. **自动存档到多维表格**：
   - 学习内容发送后，自动将内容存档到多维表格
   - 表格信息：
     - App Token: `StpsbzHHraHVy6sxVQRcCFEsnnC`
     - Table ID: `tbl8Og8ltdJH2rhe`
   - 存档字段：
     - 经文名称：《般若波罗蜜多心经》
     - 章节/品目：根据当前天数（如 Day 4: 无眼界...）
     - 学习日期：当天日期（毫秒时间戳）
     - 学习状态：已完成
     - 核心要义：学习内容摘要（50 字以内）

5. **更新进度**：
   - 发送后自动推进到下一关：`bash /home/cheche/.openclaw/workspace-wanganyu/scripts/xinjing-study.sh next`

### 心经学习进度对照表

| 天数 | 经文段落 | 主题 |
|------|----------|------|
| Day 1 | 观自在菩萨...度一切苦厄 | 开篇：照见五蕴皆空 |
| Day 2 | 舍利子，色不异空... | 色即是空 |
| Day 3 | 是诸法空相...无色声香味触法 | 受想行识，亦复如是 |
| Day 4 | 无眼界...无无明亦无无明尽 | 十二因缘 |
| Day 5 | 乃至无老死...无智亦无得 | 四谛与菩提 |
| Day 6 | 以无所得故...三世诸佛 | 菩萨道与佛果 |
| Day 7 | 依般若波罗蜜多...菩提萨埵 | 咒语的奥秘 |

---

## Memory Healthcheck（每次 heartbeat 必做）

1. **检查今日 daily log**
   - 日志写入路径：`memory/YYYY-MM-DD.md`（根目录，供 daily-triage.sh 23:59 分拣到 P0/P1/P2）
   - 分拣后读取路径：`memory/P2/YYYY-MM-DD.md`（日常对话）、`memory/P1/YYYY-MM-DD.md`（项目）、`memory/P0/YYYY-MM-DD.md`（核心规则）
   - 确认 `memory/$(date +%Y-%m-%d).md` 或 `memory/P2/$(date +%Y-%m-%d).md` 存在
   - 都不存在 → 立即创建根目录日志

HEARTBEAT_OK
