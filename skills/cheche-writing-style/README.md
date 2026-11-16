# cheche-writing-style · 安装与使用（先看这份 README）

> 这是一份 **WorkBuddy 技能包**（agent skill）。装好后，在对话里用大白话提需求即可自动生效。

---

## 一、这个技能是做什么的

把方案、PPT、幻灯片、培训课件、公众号文案改成**正规方案体**，去掉口语化的「AI 味」。
一句话：回答「**这句话该怎么写**」。

包含：三条铁律、**三层判据优先级**（功能与语境 > 个人文风 > 通用规则）、文风十条、
A/B/C 三级禁用词表（附真实替换案例）、**通用 AI 句式黑名单**（11 类句式家族的可扫触发词 +
17 项"看着像 AI 味但实测站不住"的不收录清单）、句式改造对照、**编辑纪律**（功能位、最小改动、
改动可溯源、信息守恒、负面清单）与逐页修改**对照表**的标准格式。

---

## 二、安装（约 30 秒）

1. 解压本压缩包，得到一个文件夹 `cheche-writing-style/`
2. 把这个文件夹**整个**放进技能目录：

   | 用途 | 放哪里 |
   |---|---|
   | 只给自己用（推荐） | Windows：`C:\Users\<你的用户名>\.workbuddy\skills\`<br>macOS / Linux：`~/.workbuddy/skills/` |
   | 团队共享 | `<项目根目录>/.workbuddy/skills/` |

3. 重启客户端，或**新开一个会话**——技能会自动出现在技能列表里。

装好后的目录应当长这样：

```
~/.workbuddy/skills/cheche-writing-style/
├── SKILL.md                        ← 技能主文件（铁律 + 三层优先级 + 文风十条 + 工作流）
├── references/
│   ├── banned-words.md            ← A/B/C 三级词表 + 真实替换案例
│   ├── ai-tells.md                ← 通用 AI 句式黑名单（11 类 + 不收录 17 项）
│   ├── style-rules.md             ← 句式改造对照
│   ├── edit-discipline.md         ← 编辑纪律（功能位 / 最小改动 / 负面清单）
│   └── revision-log-format.md     ← 逐页修改对照表的标准格式
└── scripts/
    ├── check_wording.py           ← 文案体检脚本
    └── gen_revision_log.py        ← 生成对照表 + 交付前强校验
```

> ⚠️ 文件夹名必须保持 `cheche-writing-style` 不变，改名会导致技能无法被识别。

---

## 三、怎么用

不需要记命令，直接说需求即可，例如：

- "帮我把这份方案的文风改一下" / "去掉 AI 味"
- "这份课件读起来不像正规方案，按我的风格改"
- "审一下这份文案"
- "这是新版，按上次那样再改一遍"

---

## 四、随包工具

- `scripts/check_wording.py` —— 文案体检：扫 A 级禁用词、B 级慎用词、自称、可疑句式。
  - 用法：`python scripts/check_wording.py <文件>`（支持 `.html` / `.md` / `.txt`）
  - 指定"我方主体名"：`python scripts/check_wording.py 文件.html --brand 你的主体名`
  - 多个主体名用逗号分隔：`--brand 沃橙,凯西`
- `scripts/gen_revision_log.py` —— 生成《文字修改对照表》并做**交付前强校验**（本技能自带，不依赖别的技能）
  - 两个输入口：`--changes changes.json`（HTML 改稿时由 deck-edit 产出）、`--pairs 改动清单.txt`（纯文字改稿时手写）
  - 清单一行一条：`页码 || 位置 || 原文 || 改后 || 说明`
  - 多条 `--changes` 按顺序链式归约（A→B、B→C 合成 A→C），输出净结果，不露中间态
  - `--verify 新文件` 逐条校验表中「改后」文案能否命中，未命中即报错
  - 用法：`python scripts/gen_revision_log.py --pairs 清单.txt --out 对照表.md --verify 新文件.md`

---

## 五、使用前要确认的一件事

本技能**跨项目通用**。开工前提一下这个项目的四项信息（说不清也没关系，会被追问）：

- **我方主体名**（文档里怎么称呼"我们"，如公司名）
- **客户 / 甲方名**
- **产品与专有术语**（哪些词是行业术语、不能当作"AI 味"删掉）
- **语种与体例**（中文简体？数字用阿拉伯数字还是中文？）

> 技能文档里出现的「沃橙 / 凯西 / WorkBuddy」都是**样本项目的例证**，不是规则本身。
> 换到自己的项目，主体名按实际替换，**不要照抄**。

---

## 六、依赖

无外部依赖。只用到 Python 3 标准库。

配套关系（各技能独立可用，按需组合）：
- 文字要落回 HTML 幻灯片 → 用 `cheche-html-deck-edit`
- 从零写方案 → 用 `cheche-proposal-writing`
