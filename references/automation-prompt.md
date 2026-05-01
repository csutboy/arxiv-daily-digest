# Automation Prompt Template

Use this template when creating the recurring daily job. Fill all placeholders from the confirmed setup conversation.

```markdown
Use the arxiv-daily-digest skill to run today's economics/sociology research digest from arXiv and Anthropic Research.

Configuration:
- Time zone: Asia/Shanghai
- arXiv category document: https://my.feishu.cn/wiki/DpKwwOoW0i8V9gkx5WNc1qfgneb
- Monitored categories: <CATEGORY_LIST>
- Include cross-listed papers: yes
- Lookback window: 48 hours
- Anthropic Research monitoring: <enabled/disabled>
- Anthropic Research sources:
  - https://www.anthropic.com/research
  - https://www.anthropic.com/research/team/economic-research
  - https://www.anthropic.com/research/team/societal-impacts
- Anthropic lookback window: 7 days
- Daily cap: <MAX_PER_CATEGORY> per category, <MAX_TOTAL> total
- Feishu chat target: <CHAT_ID_OR_USER_ID_AND_TYPE>
- Feishu Base target: <BASE_TOKEN_OR_URL>
- Feishu table target: <TABLE_ID_OR_NAME>
- Local seen state: ~/.local/state/arxiv-daily-digest/seen.json
- Empty-day behavior: <SEND_EMPTY_DIGEST_OR_SKIP>
- India exclusion: strict unless this config explicitly says otherwise

Workflow:
1. Fetch recent arXiv candidates using scripts/arxiv_candidates.py when available.
2. Fetch Anthropic Research candidates using scripts/anthropic_candidates.py when enabled.
3. De-duplicate by Source ID / 去重键 against both Feishu Base and local seen state.
4. Research arXiv author affiliations and background using current web sources; for Anthropic items, read the official article and linked reports/papers.
5. Apply the arXiv institution and India-exclusion policy in references/domain-scope.md.
6. Apply Anthropic relevance rules in references/anthropic-research.md.
7. Summarize accepted items in Chinese Markdown using the skill's required format.
8. Write accepted rows to Feishu Base with 是否已推送=false / 推送状态=未推送.
9. Push the combined Markdown digest to Feishu chat.
10. After successful chat push, update Base rows to 是否已推送=true / 推送状态=已推送 and mark source IDs seen locally.

Output:
- Briefly report whether the run succeeded.
- Include counts: candidates checked, duplicates skipped, accepted, excluded, pushed.
- If failures happen, state which step failed and what should be retried.
```
