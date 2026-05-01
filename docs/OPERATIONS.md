# 运行与维护

本文档说明每日任务如何运行、如何验证、如何排错。

## 每日运行流程

本 skill 有两条每日任务。

### arXiv Monitor - 09:00 北京时间

arXiv Monitor 只处理 arXiv 论文：

1. 读取已确认配置。
2. 从 arXiv API 抓取过去 48 小时候选论文。
3. 用 Base 中的 `Source ID` / `去重键` 和本地 `arxiv-seen.json` 排除重复条目。
4. 对候选做作者和机构调研。
5. 按经济学/社会学领域标准、机构标准和 India exclusion 筛选。
6. 把纳入条目写入飞书 Base，初始状态为 `监控任务=arXiv Monitor`、`是否已推送=false`。
7. 生成中文 Markdown 日报并推送到飞书聊天。
8. 推送成功后更新 Base 状态，并把 arXiv source ID 写入本地 seen state。

### Institution Monitor - 11:00 北京时间

Institution Monitor 只处理机构研究成果：

1. 读取已确认配置。
2. 从 Anthropic Research 官方页面抓取过去 7 天候选文章。
3. 从 Anthropic-like benchmark sources 抓取过去 30 天候选。
4. 用 Base 中的 `Source ID` / `去重键` 和本地 `institution-seen.json` 排除重复条目。
5. 读取官方文章、报告、paper 或 linked materials。
6. 按 Anthropic relevance rules 和三维 benchmark 标准筛选。
7. 把纳入条目写入飞书 Base，初始状态为 `监控任务=Institution Monitor`、`是否已推送=false`。
8. 生成中文 Markdown 日报并推送到飞书聊天。
9. 推送成功后更新 Base 状态，并把 institution source ID 写入本地 seen state。

只有 Base 写入和飞书推送都成功后，才能标记 seen。

## 手动抓取候选

```bash
python3 scripts/arxiv_candidates.py fetch \
  --categories econ.EM,econ.GN,econ.TH \
  --days 2 \
  --max-results 100
```

抓取 Anthropic Research 候选：

```bash
python3 scripts/anthropic_candidates.py fetch \
  --days 7
```

抓取 benchmark source 候选：

```bash
python3 scripts/benchmark_candidates.py fetch \
  --days 30
```

抓取 Institution Monitor 聚合候选：

```bash
python3 scripts/institution_candidates.py fetch \
  --anthropic-days 7 \
  --benchmark-days 30
```

包含本地已 seen 的论文：

```bash
python3 scripts/arxiv_candidates.py fetch \
  --categories econ.TH \
  --days 7 \
  --max-results 20 \
  --include-seen
```

包含本地已 seen 的 Anthropic 条目：

```bash
python3 scripts/anthropic_candidates.py fetch \
  --days 30 \
  --include-seen
```

包含本地已 seen 的 benchmark 条目：

```bash
python3 scripts/benchmark_candidates.py fetch \
  --days 365 \
  --include-seen
```

## 本地去重状态

默认状态文件：

```text
~/.local/state/arxiv-daily-digest/arxiv-seen.json
~/.local/state/arxiv-daily-digest/institution-seen.json
```

手动标记已推送：

```bash
python3 scripts/arxiv_candidates.py mark-seen 2604.28186 2604.27258
python3 scripts/institution_candidates.py mark-seen anthropic:81k-economics benchmark:openai-com-signals
```

如果误标记，可以编辑对应 seen 文件删除 source ID。删除后，下次运行仍会被 Base 去重挡住；只有 Base 和本地状态都没有该 ID 时才会重新进入候选。

## Codex 定时任务

在 Codex 中，使用 `references/automation-prompt.md` 里的两个模板创建两条 cron automation。每日任务 prompt 必须自包含，不要依赖当前聊天上下文。

必须写入 prompt 的配置：

- monitor 名称：`arXiv Monitor` 或 `Institution Monitor`
- 推送时间和时区：09:00 / 11:00 Asia/Shanghai
- arXiv Monitor: 分类列表、cross-list、India exclusion、`arxiv-seen.json`
- Institution Monitor: Anthropic Research 来源、benchmark 来源、include_scores、`institution-seen.json`
- 飞书聊天目标
- Base token / URL
- table ID / name
- 每日篇数上限
- 是否推送空报
- 本地 seen state 路径

## Claude Code / Hermes / OpenClaw

这些平台的 scheduler 能力取决于本地安装和配置。skill 只定义工作流，不假装自己拥有后台定时能力。

如果平台没有内建定时任务，使用系统 scheduler：

macOS `launchd`：

```text
09:00 调用 arXiv Monitor prompt。
11:00 调用 Institution Monitor prompt。
```

Linux `cron`：

```cron
0 9 * * * <agent-command> "<filled automation prompt>"
0 11 * * * <agent-command> "<filled institution automation prompt>"
```

具体命令取决于你使用的代理 CLI。

## Feishu 常见问题

消息发不出去：

- 确认机器人已加入目标群。
- 确认使用的是 `--as bot`。
- 确认应用有 `im:message:send_as_bot` 权限。
- 先用 `lark-cli im +messages-send --dry-run` 检查请求。

Base 写不进去：

- 确认 Base token 不是 wiki token。
- 如果用户给的是 wiki 链接，先解析真实对象 token。
- 先运行 `lark-cli base +field-list` 确认字段名和字段类型。
- 不要写公式、lookup、系统字段。

重复推送：

- 检查 Base 是否有 `Source ID` 和 `去重键` 字段。
- 检查本地 `arxiv-seen.json` 或 `institution-seen.json` 是否可写。
- 检查任务是否在推送失败时错误标记了 seen。

候选过少：

- 增加 lookback 到 72 小时。
- 加入 cross-list 常见分类，如 `cs.SI`、`cs.CY`、`physics.soc-ph`、`stat.AP`。
- 确认 arXiv API 可访问。
- 确认 Anthropic Research 页面可访问。
- 确认 benchmark source 官方页面可访问；部分官网可能返回 403 或 TLS 错误，脚本会记录到 `source_errors` 并继续处理其他来源。

候选过多：

- 降低 `max_per_category` 和 `max_total`。
- 缩短 lookback。
- 提高机构筛选阈值。

## 发布前检查

```bash
python3 /Users/shuai/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
python3 scripts/arxiv_candidates.py fetch --categories econ.EM,econ.GN,econ.TH --days 7 --max-results 5 --include-seen
python3 scripts/anthropic_candidates.py fetch --days 365 --include-seen
python3 scripts/benchmark_candidates.py fetch --days 365 --include-seen
python3 scripts/institution_candidates.py fetch --anthropic-days 7 --benchmark-days 30 --include-seen
python3 scripts/install_portable.py --dry-run
```

不要提交：

- `.env`
- access token
- app secret
- 实际 Base token
- 实际 chat_id/user_id 配置文件
- 本地 seen state
