---
name: arxiv-daily-digest
description: Daily research monitor for arXiv plus Anthropic Research economics/societal-impact articles. Use when the user wants scheduled arXiv searches, Anthropic AI economics/sociology monitoring, author/institution screening, Markdown academic summaries, Feishu chat pushes, and persistent Feishu Base records without duplicate items.
license: MIT
metadata:
  requires:
    bins: ["lark-cli", "python3"]
  hermes:
    tags: [Research, arXiv, Anthropic, Feishu, Economics, Sociology]
---

# arXiv Daily Digest

Use this skill to configure and run a daily research digest for economics, sociology, computational social science, and AI social/economic impact. The digest must:

- search user-selected arXiv categories, including cross-listed papers
- monitor Anthropic Research official pages for AI economics, AI sociology, societal impacts, labor-market, productivity, and AI-use studies
- research author affiliations and academic background with current web sources
- include only papers from internationally strong economics/sociology institutions or equivalent research organizations
- exclude India-based domestic university/institute papers by default
- summarize accepted papers in Chinese Markdown
- write every accepted paper to Feishu Base
- push the digest to Feishu chat
- avoid duplicate pushes by stable source ID

## Required Context

The user-provided arXiv category document is:

`https://my.feishu.cn/wiki/DpKwwOoW0i8V9gkx5WNc1qfgneb`

When category options are needed, read this document with `lark-cli docs +fetch`. The document may contain embedded sheets; if a sheet cannot be read directly, use the categories in [references/domain-scope.md](references/domain-scope.md) as the fallback list and tell the user.

Anthropic official monitoring sources are:

- `https://www.anthropic.com/research`
- `https://www.anthropic.com/research/team/economic-research`
- `https://www.anthropic.com/research/team/societal-impacts`

Use [scripts/anthropic_candidates.py](scripts/anthropic_candidates.py) when possible. Anthropic items use `anthropic:<slug>` as the stable source ID.

## Setup Workflow

When the user invokes this skill for setup, collect the missing fields before creating any recurring job:

1. arXiv categories to monitor.
   - Default suggestions for economics: `econ.EM`, `econ.GN`, `econ.TH`, plus `q-fin.EC` if the user wants finance/economic crossovers.
   - Default suggestions for sociology/computational social science: `cs.SI`, `cs.CY`, `physics.soc-ph`, `stat.AP`, plus `econ.GN` for socioeconomic work.
2. Daily push time in Beijing time (`Asia/Shanghai`).
3. Anthropic Research monitoring.
   - Default: enabled.
   - Sources: official Research, Economic Research, and Societal Impacts pages.
   - Relevance: AI economics, AI sociology, AI use, labor market, productivity, values, autonomy, work, organization, social impact, policy-facing social science.
4. Feishu chat target.
   - Group chat: `chat_id` (`oc_...`) or group name to search.
   - Direct message: user `open_id` (`ou_...`) or a resolvable user identity.
5. Feishu Base target.
   - Existing Base link/token and table ID/name, or permission to create a new Base.
6. Daily volume cap.
   - Default: max 5 papers per category and max 20 papers total.
7. Empty-day behavior.
   - Default: send one short "no qualifying paper today" message; do not create paper rows.
8. India exclusion mode.
   - Default: strict. Exclude papers whose relevant author affiliations are India-based domestic universities or institutes, including IIT, IISc, ISI, IIIT, IIM, Delhi School of Economics, and Indian state/central universities.

After collecting these fields, restate the configuration and ask for confirmation. Do not create a scheduler, send a Feishu message, or write a Base until the user confirms.

## Scheduling

Use the host platform's real scheduler or automation mechanism. Do not simulate scheduling in normal conversation.

- Codex: use a cron automation when the automation tool is available. The automation prompt should include all confirmed config values, the category document URL, the Base target, the Feishu chat target, and the Beijing-time schedule.
- Claude Code: if no persistent scheduler is available, prepare a cron/launchd command or a repeatable prompt for the user's chosen scheduler. Do not claim that Claude Code will run daily unless an actual scheduler is configured.
- Hermes/OpenClaw: use their cron/task/scheduler facility when present. If unavailable, generate the daily-run prompt and tell the user which scheduler still needs to be configured.

For cross-platform installation and paths, see [references/platforms.md](references/platforms.md).

## Daily Run Workflow

On each scheduled run:

1. Fetch candidates from all enabled sources.
   - arXiv:
     - Use [scripts/arxiv_candidates.py](scripts/arxiv_candidates.py) when possible.
     - Query selected categories with cross-listing included.
     - Use a 48-hour window by default to avoid timezone and arXiv batch timing gaps.
   - Anthropic Research:
     - Use [scripts/anthropic_candidates.py](scripts/anthropic_candidates.py) when possible.
     - Check official Research, Economic Research, and Societal Impacts pages.
     - Use a 7-day default lookback for Anthropic pages because articles are less frequent than arXiv papers.
     - Anthropic official research passes the institution-quality screen by source, but still must pass topic relevance.
2. Deduplicate before expensive research.
   - Query the Feishu Base for existing `去重键` and `Source ID`.
   - Also check the local state file, default `~/.local/state/arxiv-daily-digest/seen.json`.
   - Skip any source ID already present in either place.
3. Research authors and affiliations.
   - Use the arXiv page/PDF, author pages, department profiles, lab pages, Google Scholar/Semantic Scholar/OpenAlex pages, and institution pages.
   - For Anthropic items, read the official article and any linked paper/report materials; author-background investigation is optional unless named external authors appear.
   - Do not rely on model memory for affiliation quality. Use current source-backed evidence.
   - Record source URLs in the Base `调研来源` field.
4. Screen papers.
   - Apply [references/domain-scope.md](references/domain-scope.md) for arXiv.
   - Apply [references/anthropic-research.md](references/anthropic-research.md) for Anthropic items.
   - Include only economics/sociology/social-science-relevant arXiv papers with a credible institution/author signal.
   - Exclude India-based domestic university/institute arXiv papers under the default strict rule.
   - For Anthropic items, exclude only if they are not about AI economics, sociology, social impact, labor/productivity, values, autonomy, or policy-facing social science.
5. Summarize accepted papers in Chinese Markdown.
6. Write accepted papers to Feishu Base.
7. Push the Markdown digest to Feishu chat.
8. Mark successfully pushed source IDs as seen only after the Base write and Feishu push have both succeeded.

If the Base write succeeds but Feishu push fails, leave `是否已推送=false` or update `推送状态=推送失败`, and do not mark the paper seen in the local state. Retry on the next run.

## Feishu Requirements

Before using Feishu:

- Read the local `lark-shared`, `lark-im`, and `lark-base` skill instructions if available.
- Use `lark-cli im +messages-send` for chat pushes. It sends with bot identity, so the bot must already be in the target chat or have a direct-message relationship.
- Use `lark-cli base +...` shortcuts for Base operations. Do not call raw `bitable/v1` APIs unless the local Base skill explicitly requires it.
- For Wiki links, resolve the actual object type/token first when needed. Do not treat a `/wiki/` token as a Base token.

See [references/feishu-workflow.md](references/feishu-workflow.md) for the Base schema, write order, and message format.

## Summary Format

Use Chinese Markdown. Each accepted paper should follow this shape:

```markdown
### 1. <论文题目>
- 来源: <arXiv 或 Anthropic Research>
- ID: <arXiv ID 或 anthropic:slug> | 分类/栏目: <primary/cross-list 或 Anthropic team>
- 发布时间: <YYYY-MM-DD>
- 作者与机构: <核心作者、机构、背景判断>
- 研究问题: <1-2 句>
- 方法/数据: <1-2 句>
- 主要发现: <2-4 点>
- 价值和意义: <为什么值得读>
- 纳入理由: <机构/作者/问题价值>
- 链接: <abstract/article URL> | PDF/报告: <pdf/report URL if any>
```

At the top of the digest, include:

- date
- selected categories
- number of candidates checked
- number accepted
- number skipped as duplicates
- number excluded for institution/author-screen reasons

## Quality Bar

- Prefer precision over volume. A day with zero accepted papers is acceptable.
- Do not include papers only because the title sounds relevant.
- For author background, distinguish confirmed affiliations from inferred affiliations.
- If institutional quality is ambiguous, exclude by default and note the reason in internal notes/Base.
- Cross-listed papers are eligible, but the summary must show both primary and matched categories.
- Anthropic Research official Economic Research and Societal Impacts posts are eligible by default if topic-relevant.
- Never push duplicate source IDs.

## Resources

- [references/domain-scope.md](references/domain-scope.md): arXiv category defaults and institution-screening rules.
- [references/anthropic-research.md](references/anthropic-research.md): Anthropic Research source and relevance rules.
- [references/feishu-workflow.md](references/feishu-workflow.md): Feishu Base schema and chat/Base operations.
- [references/platforms.md](references/platforms.md): cross-platform installation notes.
- [references/automation-prompt.md](references/automation-prompt.md): template for the recurring daily job prompt.
- [scripts/arxiv_candidates.py](scripts/arxiv_candidates.py): arXiv candidate fetcher and local seen-state manager.
- [scripts/anthropic_candidates.py](scripts/anthropic_candidates.py): Anthropic Research candidate fetcher and local seen-state manager.
- [scripts/install_portable.py](scripts/install_portable.py): symlink installer for Claude Code, OpenClaw, and Hermes.
