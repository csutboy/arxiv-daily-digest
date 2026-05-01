# 运行与维护

本文档说明每日任务如何运行、如何验证、如何排错。

## 每日运行流程

每日任务应按以下顺序执行：

1. 读取已确认配置。
2. 从 arXiv API 抓取过去 48 小时候选论文。
3. 从 Anthropic Research 官方页面抓取过去 7 天候选文章。
4. 用 Base 中的 `Source ID` / `去重键` 和本地 `seen.json` 排除重复条目。
5. 对剩余 arXiv 候选做作者和机构调研；对 Anthropic 候选读取官方文章和相关报告。
6. 按经济学/社会学领域标准筛选。
7. 把纳入条目写入飞书 Base，初始状态为 `是否已推送=false`。
8. 生成中文 Markdown 日报并推送到飞书聊天。
9. 推送成功后更新 Base 状态，并把 source ID 写入本地 seen state。

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

## 本地去重状态

默认状态文件：

```text
~/.local/state/arxiv-daily-digest/seen.json
```

手动标记已推送：

```bash
python3 scripts/arxiv_candidates.py mark-seen 2604.28186 2604.27258
python3 scripts/anthropic_candidates.py mark-seen anthropic:81k-economics
```

如果误标记，可以编辑 `seen.json` 删除对应 source ID。删除后，下次运行仍会被 Base 去重挡住；只有 Base 和本地状态都没有该 ID 时才会重新进入候选。

## Codex 定时任务

在 Codex 中，使用 `references/automation-prompt.md` 填好配置后创建 cron automation。每日任务 prompt 必须自包含，不要依赖当前聊天上下文。

必须写入 prompt 的配置：

- 分类列表
- 是否启用 Anthropic Research 监测和来源 URL
- 推送时间和时区
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
每天固定时间调用对应代理的非交互命令，并传入 references/automation-prompt.md 填充后的完整 prompt。
```

Linux `cron`：

```cron
0 9 * * * <agent-command> "<filled automation prompt>"
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
- 检查本地 `seen.json` 是否可写。
- 检查任务是否在推送失败时错误标记了 seen。

候选过少：

- 增加 lookback 到 72 小时。
- 加入 cross-list 常见分类，如 `cs.SI`、`cs.CY`、`physics.soc-ph`、`stat.AP`。
- 确认 arXiv API 可访问。
- 确认 Anthropic Research 页面可访问。

候选过多：

- 降低 `max_per_category` 和 `max_total`。
- 缩短 lookback。
- 提高机构筛选阈值。

## 发布前检查

```bash
python3 /Users/shuai/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
python3 scripts/arxiv_candidates.py fetch --categories econ.EM,econ.GN,econ.TH --days 7 --max-results 5 --include-seen
python3 scripts/anthropic_candidates.py fetch --days 365 --include-seen
python3 scripts/install_portable.py --dry-run
```

不要提交：

- `.env`
- access token
- app secret
- 实际 Base token
- 实际 chat_id/user_id 配置文件
- 本地 seen state
