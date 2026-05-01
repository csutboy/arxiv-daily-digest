# Anthropic Research Monitoring

Monitor Anthropic official research pages as a fixed source for AI economics, AI sociology, labor-market, productivity, organizational, value, autonomy, and societal-impact research.

## Official Sources

- `https://www.anthropic.com/research`
- `https://www.anthropic.com/research/team/economic-research`
- `https://www.anthropic.com/research/team/societal-impacts`

Use `scripts/anthropic_candidates.py` when possible. The script assigns source IDs in the form:

```text
anthropic:<article-slug>
```

Examples:

- `anthropic:81k-economics`
- `anthropic:labor-market-impacts`
- `anthropic:claude-personal-guidance`

## Relevance Rules

Include Anthropic items when they are about:

- AI and labor markets
- AI productivity and work transformation
- AI use across countries, sectors, occupations, or organizations
- economic measurement, surveys, adoption, enterprise use, or automation
- AI personal guidance, values, autonomy, social behavior, or societal impacts
- policy-facing social science when it directly concerns AI's economic or social effects

Exclude Anthropic items when they are purely:

- model interpretability without social/economic implications
- biosecurity, biology, or science capability evaluation unrelated to social/economic impact
- alignment/security engineering with no economics/sociology angle
- product announcements with no research findings

## Screening Difference From arXiv

Anthropic official research passes the institution-quality screen by source. Do not apply the arXiv university/institution whitelist to Anthropic posts.

Still require:

- topic relevance
- identifiable publication date
- stable official URL
- source-backed summary from the Anthropic article or linked report/paper

## Summary Requirements

For each accepted Anthropic item, summarize:

- title
- publication date
- Anthropic team or source page
- research question
- data/method or evidence base
- main findings
- economic/sociological value
- why it should be monitored
- official URL

Use the same Base and Feishu push flow as arXiv items. Dedupe by `anthropic:<slug>`.
