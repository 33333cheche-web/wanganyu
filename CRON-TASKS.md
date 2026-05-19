# WangAnyu - 提醒 Bot 使用手册

- **角色**：公主的专属提醒 Bot
- **模型**：minimax/MiniMax-M2.7（省钱模式）
- **维护者**：Baby（Sean）

---

## 自检命令

### 查看当前 cron 任务列表
在飞书对话框打：
```
/cron list
```
会列出所有已配置的提醒任务、时间和状态。

### 测试 TTS 语音
```
/tts on
```
开启语音播报功能。

### 查看当前模型
```
/status
```

---

## Cron 任务完整时间表（工作日 周一到周五）

| 时间 | 任务名称 | 类型 | 内容 |
|------|---------|------|------|
| 08:00 | 早餐-0800 | 文字 | "公主！该吃早餐啦！煎饼果子来一套？✨" |
| 09:00 | 早安-0900-voice | 语音 | 早安问候（voice_reminder_morning） |
| 09:00 | 喝水提醒 | 文字 | "公主！该起来动动喝水啦！扭扭腰！" |
| 09:30 | walk-0930-voice | 语音 | 走动提醒（voice_reminder_walk） |
| 10:00 | 喝水提醒 | 文字 | "公主！该起来动动喝水啦！扭扭腰！" |
| 10:30 | walk-1030-voice | 语音 | 走动提醒（voice_reminder_walk） |
| 10:30 | 走路-1030 | 文字 | "公主，10点半了，起来走动走动，别一直坐着~" |
| 11:00 | 喝水提醒 | 文字 | "公主！该起来动动喝水啦！扭扭腰！" |
| 12:00 | 午餐-1200 | 文字 | "公主！午餐时间到！犒劳一下自己！🍚" |
| 13:00 | 午后运动-1300-voice | 语音 | 饭后运动（voice_reminder_exercise_afternoon） |
| 13:00 | 喝水提醒 | 文字 | "公主！该起来动动喝水啦！扭扭腰！" |
| 15:00 | walk-1500-voice | 语音 | 走动提醒（voice_reminder_walk） |
| 15:00 | 走路-1500 | 文字 | "公主，下午3点了，起来走动走动，喝口水，休息一下眼睛~" |
| 16:30 | walk-1630-voice | 语音 | 走动提醒（voice_reminder_walk） |
| 17:00 | 喝水提醒 | 文字 | "公主！该起来动动喝水啦！扭扭腰！" |
| 18:00 | 晚餐-1800 | 文字 | "公主！该吃晚餐啦！碳水快乐！✨" |
| 18:00 | 下班提醒-1800 | 文字 | "公主！该准备下班啦！收拾收拾，别加班太晚！✨" |
| 20:30 | 晚间运动-2030-voice | 语音 | 晚间运动（voice_reminder_exercise_evening） |
| 22:06 | sean-daily-report | 文字 | Sean 生成今日工作日报发给公主 |

---

## 语音事件说明

WangAnyu 收到以下 system event 时，会自动生成语音发送给公主：

| 事件名 | 触发时间 | 语音内容示例 |
|--------|---------|------------|
| `voice_reminder_morning` | 09:00 | "公主早上好！新的一天开始了，要精神满满哦～" |
| `voice_reminder_exercise_afternoon` | 13:00 | "公主，午饭吃完了吧？起来动一动，饭后百步走～" |
| `voice_reminder_exercise_evening` | 20:30 | "公主，该做运动啦！动起来，甩掉一天的疲劳～" |
| `voice_reminder_walk` | 9:30/10:30/15:00/16:30 | "公主，该起来走动走动了～" |

---

## 查看 cron 任务状态

可用以下命令查看任务是否正常：

```bash
# 查看 WANGANYU cron 状态（Baby 用）
OPENCLAW_HOME=/home/cheche/.openclaw-wanganyu \
  /home/cheche/.npm-global/bin/openclaw cron list \
  --url ws://127.0.0.1:18830 \
  --token wanganyu_8bfeebddd4aae9f641d255b7f37f619d
```

状态说明：
- `idle` = 正常，等待下次触发
- `ok` = 上次执行成功
- `error` = 上次执行失败（可忽略，偶尔网络问题会自动恢复）

---

## 常见问题

**Q: 为什么我打的命令 WangAnyu 说"不知道"？**
A: WangAnyu 用的是 minimax 模型，能力有限，复杂的自省命令可能处理不了。提醒功能本身是正常的。

**Q: 为什么有时报 "error" 状态？**
A: 偶尔网络问题导致消息发送失败，系统会自动重试，不影响下次触发。

**Q: 如何添加新的提醒？**
A: 联系 Baby（Sean），帮你添加到 WANGANYU cron 配置里。

---

*最后更新：2026-04-20 by Baby (Sean)*
