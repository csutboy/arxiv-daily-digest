# AI Economy/Society Daily Digest Skill

一个面向经济学、社会学、计算社会科学和 AI 社会/经济影响研究的跨平台代理 skill。它会帮助代理每天从 arXiv、Anthropic Research，以及严格对标 Anthropic 的 AI 经济/社会影响研究机构抓取候选内容，按分类、作者背景、机构质量、真实使用数据、劳动/生产率/社会风险和政策/治理建议筛选，生成中文 Markdown 学术摘要，写入飞书多维表格，并推送到飞书聊天。

当前支持作为 skill 安装到：

- Codex
- Claude Code
- Hermes
- OpenClaw

## 核心能力

- 按 arXiv 分类筛选经济学和社会学相关论文。
- 支持 cross-list 论文，例如主分类不是 `econ.*`，但 cross-list 到 `econ.TH` 时仍可纳入候选。
- 固定监测 Anthropic Research、Economic Research、Societal Impacts 官方页面，纳入 AI 经济学、AI 社会学、劳动市场、生产率、AI 使用和社会影响研究。
- 固定监测 OpenAI、Google、Microsoft、Stanford、MIT、Oxford Internet Institute、Partnership on AI、Brookings、AI Now、Ada Lovelace、ILO、OECD、IMF、World Bank 等 Anthropic-like benchmark sources。
- 对 benchmark sources 按三维标准筛选：是否研究真实使用数据；是否关注劳动、生产率或社会风险；是否把研究转成政策或治理建议。
- 对作者和机构做网页调研，只纳入国际一流或同等级强机构的论文。
- 默认严格排除印度本地大学和研究机构论文。
- 生成中文 Markdown 摘要，包含题目、发表时间、作者背景、研究问题、方法/数据、研究发现、价值意义和纳入理由。
- 写入飞书 Base，长期记录每篇论文的筛选状态、摘要、来源和推送状态。
- 推送到飞书聊天。
- 通过稳定 source ID + Feishu Base + 本地状态文件三重约束避免重复推送。

## 两个每日任务

这个 skill 拆成两个相互独立的 monitor：

| Monitor | 默认时间（北京时间） | 内容 | 本地状态文件 |
|---|---:|---|---|
| arXiv Monitor | 09:00 | 只监控 arXiv 分类与 cross-list 论文 | `~/.local/state/arxiv-daily-digest/arxiv-seen.json` |
| Institution Monitor | 11:00 | 监控 Anthropic Research 和对标机构研究成果 | `~/.local/state/arxiv-daily-digest/institution-seen.json` |

两条任务可以推送到同一个飞书聊天，也可以配置到不同聊天；默认共用同一个 Feishu Base，并通过 `监控任务`、`来源`、`Source ID` 和 `去重键` 区分记录。

## 目录结构

```text
arxiv-daily-digest/
├── SKILL.md
├── README.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── docs/
│   ├── CONFIGURATION.md
│   └── OPERATIONS.md
├── references/
│   ├── anthropic-research.md
│   ├── automation-prompt.md
│   ├── benchmark-sources.md
│   ├── domain-scope.md
│   ├── feishu-workflow.md
│   └── platforms.md
└── scripts/
    ├── anthropic_candidates.py
    ├── arxiv_candidates.py
    ├── benchmark_candidates.py
    ├── institution_candidates.py
    └── install_portable.py
```

## 安装

把仓库放到任意本地目录后，可以直接把同一个 skill 软链接到多个代理平台：

```bash
python3 scripts/install_portable.py
```

默认安装目标：

```text
~/.codex/skills/arxiv-daily-digest
~/.claude/skills/arxiv-daily-digest
~/.openclaw/skills/arxiv-daily-digest
~/.hermes/skills/arxiv-daily-digest
```

如果你已经把仓库克隆到 `~/.codex/skills/arxiv-daily-digest`，Codex 会直接读取该目录。Claude Code、OpenClaw 和 Hermes 会通过软链接读取同一份文件，避免多份 skill 内容漂移。

## 前置依赖

本 skill 本身不保存任何密钥。运行每日任务的机器需要：

- `python3`
- `lark-cli`
- 能访问 arXiv API 和网页搜索
- 能访问 Anthropic 官方研究页面
- 能访问 OpenAI、Google、Microsoft、Stanford、MIT、OII、PAI、Brookings、AI Now、Ada Lovelace、ILO、OECD、IMF、World Bank 等官方页面
- 已配置好的飞书应用权限
- 可用的飞书聊天目标
- 可写入的飞书多维表格

飞书侧通常需要：

- 机器人能发送消息到目标群或用户
- 机器人或用户有 Base 写权限
- `lark-cli` 已完成必要的 app 配置和授权

详细配置见 [docs/CONFIGURATION.md](docs/CONFIGURATION.md)。

## 快速使用

在支持 skills 的代理里调用：

```text
Use $arxiv-daily-digest to configure two Feishu pushes: arXiv Monitor at 09:00 and Institution Monitor at 11:00 Beijing time.
```

配置阶段会询问：

- 要监控的 arXiv 分类
- arXiv Monitor 推送时间，默认北京时间 09:00
- Institution Monitor 是否启用 Anthropic Research 官方来源监测，默认启用
- Institution Monitor 是否启用 Anthropic-like benchmark sources，默认启用
- Institution Monitor 推送时间，默认北京时间 11:00
- 飞书聊天目标
- 飞书 Base 目标
- 每日最多推送多少篇
- 没有符合条件论文时是否推送空报

确认后，代理应使用所在平台的定时任务能力创建每日运行任务。Codex 可使用 automation；Claude Code、Hermes、OpenClaw 取决于本地是否启用对应 scheduler。

## 默认关注领域

经济学：

- `econ.EM`
- `econ.GN`
- `econ.TH`
- `q-fin.EC`

社会学 / 计算社会科学：

- `cs.SI`
- `cs.CY`
- `physics.soc-ph`
- `stat.AP`
- `econ.GN`

完整筛选规则见 [references/domain-scope.md](references/domain-scope.md)。

Anthropic Research 默认来源：

- `https://www.anthropic.com/research`
- `https://www.anthropic.com/research/team/economic-research`
- `https://www.anthropic.com/research/team/societal-impacts`

完整筛选规则见 [references/anthropic-research.md](references/anthropic-research.md)。

Benchmark sources 默认包括：

- OpenAI Signals
- Google AI & Economy / Google Research TASC / Google DeepMind sociotechnical evaluation
- Microsoft AI Economy Institute
- Stanford HAI / AI Index / Digital Economy Lab
- MIT Shaping the Future of Work / Work of the Future / FutureTech
- Oxford Internet Institute AI & Work
- Partnership on AI, Brookings, AI Now, Ada Lovelace
- ILO, OECD, IMF, World Bank

完整筛选规则见 [references/benchmark-sources.md](references/benchmark-sources.md)。

## 候选抓取脚本

测试 arXiv 抓取：

```bash
python3 scripts/arxiv_candidates.py fetch \
  --categories econ.EM,econ.GN,econ.TH \
  --days 2 \
  --max-results 50
```

测试 Anthropic Research 抓取：

```bash
python3 scripts/anthropic_candidates.py fetch \
  --days 7
```

测试 benchmark source 抓取：

```bash
python3 scripts/benchmark_candidates.py fetch \
  --days 30
```

测试 11 点机构聚合抓取：

```bash
python3 scripts/institution_candidates.py fetch \
  --anthropic-days 7 \
  --benchmark-days 30
```

标记本地已推送条目：

```bash
python3 scripts/arxiv_candidates.py mark-seen 2604.28186
python3 scripts/institution_candidates.py mark-seen anthropic:81k-economics benchmark:openai-com-signals
```

默认本地状态文件：

```text
~/.local/state/arxiv-daily-digest/arxiv-seen.json
~/.local/state/arxiv-daily-digest/institution-seen.json
```

## 每日输出格式

推送消息是中文 Markdown，顶部包含运行统计：

```markdown
## arXiv 经济学/社会学日报 - 2026-05-01

- 监控分类: econ.EM, econ.GN, econ.TH
- 候选论文: 42
- 新纳入: 5
- 重复跳过: 3
- 机构/范围排除: 34
```

```markdown
## AI 机构研究日报 - 2026-05-01

- Anthropic Research: enabled
- Benchmark sources: enabled
- 候选条目: 18
- 新纳入: 4
- 重复跳过: 2
- 主题/对标排除: 12
```

每篇论文/研究条目包含：

- 题目和 arXiv 链接
- Anthropic 官方文章链接
- Benchmark source 官方页面、报告或研究链接
- 发布时间
- 作者与机构背景
- 研究问题
- 方法/数据
- 主要发现
- 价值和意义
- 纳入理由
- Anthropic-like 三维对标结果
- 调研来源

## 安全设计

- 不提交飞书 token、app secret、GitHub token 或任何访问凭证。
- 不把用户的实际 Base token/chat_id 写进仓库。
- 推送前必须确认飞书目标和消息内容。
- 只有 Base 写入和飞书推送都成功后，才把 source ID 标记为已推送。

## 文档

- [docs/CONFIGURATION.md](docs/CONFIGURATION.md): 运行前配置和飞书 Base 设计。
- [docs/OPERATIONS.md](docs/OPERATIONS.md): 每日运行、排错、去重和跨平台代理注意事项。
- [references/automation-prompt.md](references/automation-prompt.md): 定时任务 prompt 模板。
- [references/feishu-workflow.md](references/feishu-workflow.md): agent 执行飞书操作时使用的低层流程。
