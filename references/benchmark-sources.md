# Anthropic-Like Benchmark Sources

This reference defines non-Anthropic institutions to monitor for AI economics, sociology, labor, productivity, social-risk, and governance research. These are not generic "AI policy" sources. They are included because they can produce work comparable to Anthropic Economic Research and Societal Impacts.

## Screening Standard

For every candidate item from these sources, evaluate three dimensions:

1. **Real usage or empirical evidence**
   - AI product usage logs, surveys, interviews, workplace data, occupational/task data, enterprise case studies, cross-country statistics, labor-market data, platform data, or other real-world evidence.
2. **Labor, productivity, or social-risk focus**
   - Work transformation, task change, jobs, wages, productivity, skills, organizations, inequality, power concentration, labor exploitation, digital divide, social behavior, values, safety, or public-interest risk.
3. **Policy or governance translation**
   - Policy recommendations, governance frameworks, evaluation methods, impact assessments, regulation, institutional design, worker participation, public-interest recommendations, or implementation guidance.

Default inclusion rule:

- **High priority**: all three dimensions are present.
- **Eligible**: dimension 1 is present and at least one of dimensions 2 or 3 is present.
- **Review only**: dimensions 2 and 3 are present but real usage/evidence is weak.
- **Exclude**: only generic AI policy commentary, product news, technical model capability work, or safety/alignment content without economics/sociology/social-impact evidence.

For each accepted item, record which dimensions were met in Base and the Markdown summary.

## Frontline AI Company Sources

| Source | URL | Why monitor |
|---|---|---|
| OpenAI Economic Research / OpenAI Signals | `https://openai.com/signals/` | Closest to Anthropic Economic Index when it uses ChatGPT usage data to study work, tasks, productivity, and economic impact. |
| Google AI & Economy Research Program | `https://ai.google/economy/` | AI and the future of work, productivity, growth, diffusion, and scientific discovery, often with economists and external researchers. |
| Google Research TASC / Society-Centered AI | `https://research.google/blog/responsible-ai-at-google-research-technology-ai-society-and-culture/` | Society, culture, economy, vulnerable groups, and participatory evaluation. |
| Google DeepMind sociotechnical evaluation | `https://deepmind.google/blog/evaluating-social-and-ethical-risks-from-generative-ai/` | Human interaction and systemic social/ethical risk evaluation beyond model capability. |
| Microsoft AI Economy Institute | `https://www.microsoft.com/en-us/corporate-responsibility/topics/ai-economy-institute/` | Work, education, productivity, inclusive growth, and AI economic futures. |

## Academic Benchmark Sources

| Source | URL | Why monitor |
|---|---|---|
| Stanford HAI | `https://hai.stanford.edu/about` | Broad AI technical, economic, policy, and societal-impact research. |
| Stanford AI Index | `https://hai.stanford.edu/ai-index/2025-ai-index-report%E2%80%8B` | Annual benchmark report for AI technology, economy, policy, and social impact. |
| Stanford Digital Economy Lab | `https://digitaleconomy.stanford.edu/research/` | AI, digital economy, labor markets, productivity, and new economic measurement. |
| MIT Shaping the Future of Work / Stone Center | `https://shapingwork.mit.edu/` | AI, job quality, wages, labor-market inequality, and work institutions. |
| MIT Work of the Future / GenAI & Work | `https://workofthefuture-taskforce.mit.edu/gen-ai/` | Enterprise cases, interviews, task and skill transformation, organization change. |
| MIT FutureTech | `https://futuretech.mit.edu/research` | Technical progress, economic feasibility, AI diffusion, AI risk repositories, and governance. |
| Oxford Internet Institute: AI & Work | `https://www.oii.ox.ac.uk/research/projects/research-programme-on-ai-work/` | AI and work, platform labor, digital inequality, and hidden labor in AI supply chains. |

## Policy, Social-Impact, and Labor Sources

| Source | URL | Why monitor |
|---|---|---|
| Partnership on AI: AI, Labor, and the Economy | `https://partnershiponai.org/program/ai-labor-and-the-economy/` | Worker participation, shared prosperity, job quality, and multistakeholder governance. |
| Brookings AI and Emerging Technology Initiative | `https://www.brookings.edu/projects/artificial-intelligence-and-emerging-technology-initiative/` | Policy research on AI's economic structure and labor-market impacts. |
| AI Now Institute | `https://ainowinstitute.org/publications/research/executive-summary-artificial-power` | Critical analysis of power concentration, labor exploitation, industrial structure, and regulatory capture. |
| Ada Lovelace Institute | `https://www.adalovelaceinstitute.org/about/our-strategy/` | AI impact assessment, public interest, social/economic impact monitoring. |
| ILO generative AI and jobs | `https://www.ilo.org/publications/generative-ai-and-jobs-2025-update` | Cross-country labor exposure, jobs, task change, and policy implications. |
| OECD AI and labor market | `https://www.oecd.org/en/publications/oecd-employment-outlook-2023_08785bba-en/full-report/artificial-intelligence-and-the-labour-market-introduction_ea35d1c5.html` | AI, employment, skills, labor-market policy, and cross-country evidence. |
| IMF AI topic | `https://www.imf.org/en/topics/artificial-intelligence` | Macroeconomic, distributional, and policy implications of AI. |
| World Bank WDR 2026 | `https://www.worldbank.org/en/publication/wdr2026` | Development, income distribution, governance, and policy tools for digital/AI transformation. |

## Default Priority

If daily volume is constrained, prioritize in this order:

1. OpenAI, Google, Microsoft company-internal economic/societal research.
2. Stanford HAI / AI Index / Digital Economy Lab.
3. MIT Work, Shaping Work, FutureTech.
4. Partnership on AI.
5. AI Now, Ada Lovelace, Oxford Internet Institute.
6. ILO, OECD, IMF, World Bank.

## Base Fields

For these sources, populate:

- `来源`: `Benchmark Institution`
- `Source ID`: `benchmark:<host-and-path-slug>`
- `机构`: source institution
- `Anthropic-like Dimensions`: comma-separated list of `real_usage_data`, `labor_productivity_social_risk`, `policy_governance_translation`
- `对标评分`: `High`, `Eligible`, `Review`, or `Exclude`
- `调研来源`: official URL plus any linked report/data/paper URL

