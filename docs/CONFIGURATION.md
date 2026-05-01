# 配置说明

本文档说明第一次启用 `arxiv-daily-digest` 时需要准备的信息。当前 skill 同时支持 arXiv 和 Anthropic Research 官方页面。

## 1. 选择 arXiv 分类

配置阶段至少选择一个分类。常用组合：

经济学基础组合：

```text
econ.EM,econ.GN,econ.TH
```

经济学 + 金融交叉：

```text
econ.EM,econ.GN,econ.TH,q-fin.EC
```

社会学 / 计算社会科学：

```text
cs.SI,cs.CY,physics.soc-ph,stat.AP,econ.GN
```

如果论文主分类不在监控列表，但 cross-list 到监控分类，默认仍进入候选池。

## 2. 启用 Anthropic Research 监测

默认启用 Anthropic Research 官方来源：

```text
https://www.anthropic.com/research
https://www.anthropic.com/research/team/economic-research
https://www.anthropic.com/research/team/societal-impacts
```

纳入范围：

- AI 经济学
- AI 社会学
- 劳动力市场和职业影响
- 生产率、组织和企业使用
- AI 使用调查和经济指数
- 价值观、个人指导、自治性和社会影响
- 与 AI 社会/经济影响直接相关的政策研究

Anthropic 官方研究默认通过机构质量筛选，但仍需通过主题相关性筛选。去重键使用 `anthropic:<article-slug>`。

## 3. 设置推送时间

所有时间按北京时间 `Asia/Shanghai` 处理。

建议时间：

```text
每天 09:00
```

arXiv 的发布时间和版本更新时间可能跨时区，因此每日任务默认抓取过去 48 小时候选。Anthropic Research 更新频率较低，默认抓取过去 7 天。两类来源都用稳定 source ID 去重。

## 4. 准备飞书聊天目标

飞书推送需要二选一：

- 群聊 `chat_id`，形如 `oc_xxx`
- 用户 `open_id`，形如 `ou_xxx`

群聊推送要求：

- 飞书机器人已经加入目标群
- 应用有发送消息权限
- `lark-cli im +messages-send` 能用 bot 身份发送消息

如果只有群名，可以先用：

```bash
lark-cli im +chat-search --query "<群名>" --as bot
```

## 5. 准备飞书 Base

可以使用已有 Base，也可以让代理创建新 Base。

已有 Base 需要：

- Base URL 或 base token
- 表 ID 或表名
- 当前执行身份有写入权限

推荐表名：

```text
arXiv Daily Digest
```

推荐字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| 日期 | datetime | 日报日期 |
| 来源 | select | `arXiv` 或 `Anthropic Research` |
| Source ID | text | 稳定去重键，如 arXiv ID 或 `anthropic:slug` |
| 分类 | text / multi-select | 命中的监控分类 |
| Primary Category | text | arXiv 主分类 |
| Cross-list Categories | text | 全部 arXiv 分类 |
| arXiv ID | text | arXiv 论文 ID；Anthropic 条目可留空 |
| Anthropic Team | text | Economic Research / Societal Impacts 等 |
| 标题 | text | 论文标题 |
| 作者 | text | 作者列表 |
| 机构 | text | 机构信息 |
| 发布时间 | datetime | arXiv 发布时间 |
| 更新时间 | datetime | arXiv 更新时间 |
| 论文链接 | url / text | arXiv abstract 或 Anthropic article 链接 |
| PDF 链接 | url / text | PDF 或报告链接 |
| 作者背景 | text | 作者调研摘要 |
| 机构评级 | select | `一流`、`同等级强机构`、`不确定`、`排除` |
| 筛选状态 | select | `候选`、`已纳入`、`已排除`、`待复核` |
| 排除原因 | text | 未纳入原因 |
| 研究问题 | text | 研究问题 |
| 方法/数据 | text | 方法和数据 |
| 研究发现 | text | 主要发现 |
| 价值意义 | text | 学术价值和现实意义 |
| 纳入理由 | text | 为什么推送 |
| Markdown 摘要 | text | 最终推送块 |
| 调研来源 | text | 来源 URL |
| 是否已推送 | checkbox | 推送成功后为 true |
| 推送时间 | datetime | 实际推送时间 |
| 推送状态 | select | `未推送`、`已推送`、`推送失败` |
| 去重键 | text | 通常等于 Source ID |

## 6. 机构筛选标准

默认只纳入：

- 国际一流经济学、社会学、政策学院、商学院或相关研究中心
- 同等级的国际组织、央行、顶级研究实验室
- 作者有可验证的强学术背景

默认排除：

- 机构无法验证的论文
- 机构明显低于阈值的论文
- 印度本地大学和研究机构论文，包括 IIT、IISc、ISI、IIIT、IIM 等

如果论文有多个机构，只在国际强机构作者是 lead、corresponding、senior 或明显核心贡献者时纳入。

Anthropic Research 官方条目不走上述机构白名单筛选。它们来自 Anthropic 官方研究源，只按主题相关性、研究价值和是否重复筛选。

## 7. 推荐配置模板

```yaml
timezone: Asia/Shanghai
categories:
  - econ.EM
  - econ.GN
  - econ.TH
  - cs.SI
  - cs.CY
  - physics.soc-ph
lookback_hours: 48
max_per_category: 5
max_total: 20
include_cross_list: true
anthropic_research:
  enabled: true
  sources:
    - https://www.anthropic.com/research
    - https://www.anthropic.com/research/team/economic-research
    - https://www.anthropic.com/research/team/societal-impacts
  lookback_days: 7
india_exclusion: strict
empty_day_behavior: send_empty_digest
local_seen_state: ~/.local/state/arxiv-daily-digest/seen.json
```
