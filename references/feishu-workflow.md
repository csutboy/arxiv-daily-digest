# Feishu Workflow

Use `lark-cli` for all Feishu chat and Base operations. Read the local `lark-shared`, `lark-im`, and `lark-base` skills before executing commands.

## Base Schema

Create or verify a table named `arXiv Daily Digest` with these fields. Field names are Chinese because the digest is Chinese Markdown.

| 字段 | 类型 | 用途 |
|---|---|---|
| 日期 | datetime | digest date in Asia/Shanghai |
| 来源 | select | `arXiv` or `Anthropic Research` |
| Source ID | text | stable dedupe key, e.g. arXiv ID or `anthropic:slug` |
| 分类 | text or multi-select | matched monitored categories |
| Primary Category | text | arXiv primary category |
| Cross-list Categories | text | all arXiv categories |
| arXiv ID | text | stable arXiv ID without version suffix; blank for Anthropic items |
| Anthropic Team | text | Economic Research / Societal Impacts / Anthropic Research |
| 标题 | text | paper title |
| 作者 | text | author list |
| 机构 | text | confirmed affiliations |
| 发布时间 | datetime | arXiv published date |
| 更新时间 | datetime | arXiv updated date |
| 论文链接 | url or text | arXiv abstract URL or Anthropic article URL |
| PDF 链接 | url or text | PDF/report URL if available |
| 作者背景 | text | source-backed author background |
| 机构评级 | select | `一流`, `同等级强机构`, `不确定`, `排除` |
| 筛选状态 | select | `候选`, `已纳入`, `已排除`, `待复核` |
| 排除原因 | text | reason when excluded |
| 研究问题 | text | concise research question |
| 方法/数据 | text | method/data summary |
| 研究发现 | text | key findings |
| 价值意义 | text | academic/practical value |
| 纳入理由 | text | why this paper passed the screen |
| Markdown 摘要 | text | final per-paper Markdown block |
| 调研来源 | text | source URLs, one per line |
| 是否已推送 | checkbox | true after successful Feishu chat push |
| 推送时间 | datetime | actual push time |
| 推送状态 | select | `未推送`, `已推送`, `推送失败` |
| 去重键 | text | normally same as Source ID |

If creating a new Base, create the Base in `Asia/Shanghai`, then create the table and fields. If using an existing Base, list fields first and add only missing fields.

## Write Order

1. Fetch candidate source IDs from arXiv and Anthropic Research.
2. Check duplicate state:
   - Base: scan/query `Source ID` or `去重键`.
   - Local state file: `~/.local/state/arxiv-daily-digest/seen.json`.
3. For accepted papers, write Base rows with `是否已推送=false` and `推送状态=未推送`.
4. Push the combined Markdown digest to Feishu chat.
5. Update accepted rows to `是否已推送=true`, `推送状态=已推送`, and set `推送时间`.
6. Mark the same source IDs as seen with the matching script:
   - arXiv: `scripts/arxiv_candidates.py mark-seen`
   - Anthropic: `scripts/anthropic_candidates.py mark-seen`

If step 4 fails, keep rows as unpushed and do not mark seen.

## Useful Commands

Search for a group chat by name:

```bash
lark-cli im +chat-search --query "<group name>" --as bot
```

Send Markdown to a group:

```bash
lark-cli im +messages-send --chat-id oc_xxx --markdown "<markdown>" --as bot
```

Send Markdown to a direct message:

```bash
lark-cli im +messages-send --user-id ou_xxx --markdown "<markdown>" --as bot
```

Create a Base:

```bash
lark-cli base +base-create --name "arXiv Daily Digest" --time-zone Asia/Shanghai
```

Create a table with minimal first field, then add fields:

```bash
lark-cli base +table-create --base-token app_xxx --name "arXiv Daily Digest"
lark-cli base +field-list --base-token app_xxx --table-id tbl_xxx
lark-cli base +field-create --base-token app_xxx --table-id tbl_xxx --json '{"name":"arXiv ID","type":"text"}'
```

Write a record:

```bash
lark-cli base +record-upsert \
  --base-token app_xxx \
  --table-id tbl_xxx \
  --json '{"来源":"arXiv","Source ID":"2601.12345","arXiv ID":"2601.12345","标题":"...","是否已推送":false,"推送状态":"未推送"}'
```

Update a record after push:

```bash
lark-cli base +record-upsert \
  --base-token app_xxx \
  --table-id tbl_xxx \
  --record-id rec_xxx \
  --json '{"是否已推送":true,"推送状态":"已推送","推送时间":"2026-05-01 09:00:00"}'
```

Before writing records, always inspect real field definitions with `+field-list`; do not write formula, lookup, or system fields.

## Digest Header

Use this Markdown header:

```markdown
## 经济学/社会学研究日报 - <YYYY-MM-DD>

- 监控分类: <categories>
- Anthropic Research: <enabled/disabled>
- 候选论文: <n>
- 新纳入: <n>
- 重复跳过: <n>
- 机构/范围排除: <n>
- Base: <link or token>
```

When no papers qualify, send:

```markdown
## 经济学/社会学研究日报 - <YYYY-MM-DD>

今日检查了 <n> 个候选条目，未发现符合分类、机构/来源和主题筛选标准的新内容。
```
