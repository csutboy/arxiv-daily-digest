# Domain Scope

This skill is tuned for economics, sociology, and computational social science. The Feishu arXiv category document is the preferred source for category names, but use this fallback taxonomy when the document or embedded sheets are unavailable.

## Default arXiv Categories

Economics:

- `econ.EM` - Econometrics
- `econ.GN` - General Economics
- `econ.TH` - Theoretical Economics
- `q-fin.EC` - Economics / quantitative finance crossover
- `stat.AP`, `stat.ME` - applied/statistical methods when the topic is clearly economic

Sociology and computational social science:

- `cs.SI` - Social and Information Networks
- `cs.CY` - Computers and Society
- `physics.soc-ph` - Physics and Society
- `stat.AP` - applied statistics for social data
- `econ.GN` - socioeconomic and policy-facing work

Cross-listed papers are eligible. If a paper's primary category is outside the monitored categories but it is cross-listed into one of them, keep it in the candidate pool and label both primary and matched categories.

## Institution Screen

Include a paper only when at least one relevant author signal is strong enough:

- lead, corresponding, senior, or clearly central author is affiliated with an internationally top economics/sociology department, policy school, business school, or social science research group
- author is affiliated with a high-signal research organization, central bank, international institution, or top industry research lab
- author has a clearly established publication record in economics, sociology, political economy, demography, computational social science, networks, or policy research

Do not use a single global ranking mechanically. Use current web sources and domain judgment.

## Core Economics Institutions

Strong default includes:

- MIT, Harvard, Stanford, Princeton, University of Chicago, UC Berkeley, Yale, Northwestern, Columbia, NYU, University of Pennsylvania, Brown, Duke, UCLA, UC San Diego, Cornell, Boston University, University of Michigan, University of Wisconsin-Madison
- LSE, Oxford, Cambridge, UCL, Warwick, University of Zurich, Bocconi, Toulouse School of Economics, Paris School of Economics, Sciences Po, Barcelona School of Economics, Stockholm University, University of Copenhagen
- Chicago Booth, Wharton, Stanford GSB, MIT Sloan, Harvard Business School, Kellogg, Columbia Business School, NYU Stern, Berkeley Haas, London Business School, INSEAD, HEC Paris
- NBER, CEPR, IZA, J-PAL, World Bank, IMF, OECD, BIS, Federal Reserve Board and regional Federal Reserve Banks, ECB, Bank of England

This is not exhaustive. Equivalent institutions may be included if source-backed evidence shows comparable field strength.

## Core Sociology / Social Science Institutions

Strong default includes:

- Harvard, Stanford, Princeton, UC Berkeley, University of Chicago, Columbia, NYU, Yale, University of Michigan, UCLA, Northwestern, Cornell, Duke, University of Pennsylvania, UNC Chapel Hill, University of Wisconsin-Madison, Brown
- Oxford, Cambridge, LSE, UCL, Sciences Po, EHESS, European University Institute, University of Amsterdam, University of Copenhagen, Stockholm University, WZB Berlin Social Science Center
- Max Planck Institute for Demographic Research, Max Planck Institute for the Study of Societies, Santa Fe Institute, Oxford Internet Institute
- Microsoft Research, Google Research, Meta Core Data Science, Microsoft Research New England, Stanford HAI, MIT Media Lab when the paper is substantively social-science-facing

For computational social science, a top CS/network science affiliation can qualify only if the research question is social, economic, policy, or institutional rather than generic ML.

## India Exclusion

Default mode is strict. Exclude papers whose relevant author affiliations are India-based domestic universities or institutes, including but not limited to:

- IIT, IISc, ISI, IIIT, IIM
- Delhi School of Economics
- Indian central/state/private universities
- India-based domestic research institutes and policy schools

If a paper mixes a top international institution with an India-based domestic institution, include only when the top international author is clearly lead/corresponding/senior or intellectually central. Otherwise exclude and note the ambiguity.

## Exclusion Reasons

Use one of these reasons in Base when rejecting candidates:

- duplicate arXiv ID
- outside economics/sociology scope
- institution below threshold
- author background not verifiable
- India domestic institution exclusion
- insufficient abstract/PDF information
- low research value for this digest

## Research Evidence

For each accepted paper, collect source URLs for:

- arXiv abstract page
- PDF or HTML source when useful
- author profile or department page
- institution/lab page or reliable profile page
- citation/profile source when used to justify author strength

If evidence is weak, exclude by default.
