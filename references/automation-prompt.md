# Automation Prompt Templates

Create two recurring jobs from this skill. Fill placeholders from the confirmed setup conversation.

## arXiv Monitor - Daily 09:00 Beijing Time

```markdown
Use the arxiv-daily-digest skill to run today's arXiv Monitor.

Configuration:
- Monitor: arXiv Monitor
- Schedule: daily 09:00 Asia/Shanghai
- arXiv category document: https://my.feishu.cn/wiki/DpKwwOoW0i8V9gkx5WNc1qfgneb
- Monitored categories: <CATEGORY_LIST>
- Include cross-listed papers: yes
- Lookback window: 48 hours
- Daily cap: <MAX_PER_CATEGORY> per category, <MAX_TOTAL> total
- Feishu chat target: <CHAT_ID_OR_USER_ID_AND_TYPE>
- Feishu Base target: <BASE_TOKEN_OR_URL>
- Feishu table target: <TABLE_ID_OR_NAME>
- Local seen state: ~/.local/state/arxiv-daily-digest/arxiv-seen.json
- Empty-day behavior: <SEND_EMPTY_DIGEST_OR_SKIP>
- India exclusion: strict unless this config explicitly says otherwise

Workflow:
1. Fetch recent arXiv candidates using scripts/arxiv_candidates.py.
2. De-duplicate by Source ID / 去重键 against both Feishu Base and the arXiv local seen state.
3. Research author affiliations and background using current web sources.
4. Apply the arXiv institution and India-exclusion policy in references/domain-scope.md.
5. Summarize accepted papers in Chinese Markdown using the skill's required format.
6. Write accepted rows to Feishu Base with 监控任务=arXiv Monitor, 是否已推送=false, 推送状态=未推送.
7. Push the arXiv Markdown digest to Feishu chat.
8. After successful chat push, update Base rows to 是否已推送=true / 推送状态=已推送 and mark arXiv IDs seen locally.

Output:
- Briefly report whether the arXiv run succeeded.
- Include counts: candidates checked, duplicates skipped, accepted, excluded, pushed.
- If failures happen, state which step failed and what should be retried.
```

## Institution Monitor - Daily 11:00 Beijing Time

```markdown
Use the arxiv-daily-digest skill to run today's Institution Monitor.

Configuration:
- Monitor: Institution Monitor
- Schedule: daily 11:00 Asia/Shanghai
- Anthropic Research monitoring: enabled
- Anthropic Research sources:
  - https://www.anthropic.com/research
  - https://www.anthropic.com/research/team/economic-research
  - https://www.anthropic.com/research/team/societal-impacts
- Anthropic lookback window: 7 days
- Benchmark institution monitoring: enabled
- Benchmark standard: require Anthropic-like evidence across real usage/data, labor/productivity/social-risk focus, and policy/governance translation; include only High or Eligible scores unless explicitly configured otherwise.
- Benchmark lookback window: 30 days
- Daily cap: <MAX_TOTAL> total
- Feishu chat target: <CHAT_ID_OR_USER_ID_AND_TYPE>
- Feishu Base target: <BASE_TOKEN_OR_URL>
- Feishu table target: <TABLE_ID_OR_NAME>
- Local seen state: ~/.local/state/arxiv-daily-digest/institution-seen.json
- Empty-day behavior: <SEND_EMPTY_DIGEST_OR_SKIP>

Workflow:
1. Fetch institution candidates using scripts/institution_candidates.py.
2. De-duplicate by Source ID / 去重键 against both Feishu Base and the institution local seen state.
3. Read official articles and linked reports/papers for accepted candidates.
4. Apply Anthropic relevance rules in references/anthropic-research.md.
5. Apply benchmark three-dimension rules in references/benchmark-sources.md.
6. Summarize accepted institution items in Chinese Markdown using the skill's required format.
7. Write accepted rows to Feishu Base with 监控任务=Institution Monitor, 是否已推送=false, 推送状态=未推送.
8. Push the institution Markdown digest to Feishu chat.
9. After successful chat push, update Base rows to 是否已推送=true / 推送状态=已推送 and mark source IDs seen locally.

Output:
- Briefly report whether the institution run succeeded.
- Include counts: candidates checked, duplicates skipped, accepted, excluded, source_errors, pushed.
- If failures happen, state which source or step failed and what should be retried.
```
