# Platform Notes

This package uses a portable `SKILL.md` core. The same directory can be symlinked into multiple agent skill folders.

## Install Paths

- Codex: `~/.codex/skills/arxiv-daily-digest/SKILL.md`
- Claude Code personal skill: `~/.claude/skills/arxiv-daily-digest/SKILL.md`
- OpenClaw global skill: `~/.openclaw/skills/arxiv-daily-digest/SKILL.md`
- Hermes local skill: `~/.hermes/skills/arxiv-daily-digest/SKILL.md`

Use `scripts/install_portable.py` from the skill root to create symlinks for Claude Code, OpenClaw, and Hermes.

## Platform Behavior

Codex:

- Use the Codex automation tool for the daily recurring job when available.
- Use `destination=thread` only for thread follow-up. For this skill's long-running daily job, prefer a cron automation that runs the self-contained daily prompt.

Claude Code:

- Claude Code reads personal skills from `~/.claude/skills/<skill-name>/SKILL.md`.
- Direct invocation is normally `/arxiv-daily-digest`.
- If Claude Code has no scheduler in the active environment, configure `cron`, `launchd`, or an external scheduler to run a prompt/command daily.

OpenClaw:

- OpenClaw commonly reads global skills from `~/.openclaw/skills/`.
- Restart or refresh the gateway if the skill does not appear after installation.
- Use OpenClaw's own task/cron system if available.

Hermes:

- Hermes accepts `SKILL.md`-style skills and can load local skills from its configured skills directory.
- This machine has `~/.hermes/skills/`; use that as the local install target unless the user's Hermes config says otherwise.
- Use Hermes cron/task support if available; otherwise hand the user a scheduler command.

## Portability Rule

The skill is responsible for the workflow and quality bar. Scheduling, credentials, web search, and Feishu command execution depend on the host agent's available tools. If a host lacks a required tool, state the missing capability and provide the next concrete setup step.
