# haas-ai-club-event

A portable agent skill for standing up Haas AI Club (UC Berkeley) events:
intake (blocking/optional/researched), approval-gated plan, EMS room requests,
poster design in the club's design language, CampusGroups RSVPs, WhatsApp/
Slack marketing copy, haasaiclub.com updates, optional member email blasts,
food and event policy, and reimbursements.

## Import

- **Claude Code / Claude agent skills:** copy this directory into your skills
  folder (e.g. `~/.claude/skills/` or the project's `.claude/skills/`). The
  SKILL.md frontmatter is the manifest; the skill triggers on requests to put
  up a new AI Club event.
- **Any other harness:** point the agent at SKILL.md as its entry prompt and
  let it read files under `references/` on demand. Scripts run with any
  Python 3.9+ (`python3 scripts/event_intake.py ...`). No dependencies.

## Test

    python3 scripts/test_dry_run.py

Expect "ALL TESTS PASSED". Scope: the suite covers the intake/plan core only -
no network, no live mutations, no harness triggering (it writes only temp
input files). Agent-judgment scenarios live in references/eval-scenarios.md;
details in references/dry-run-testing.md.

## Safety model

Intake before planning, plan before doing, approval before publishing.
Credentials only through the host's secret store, never chat; Duo retries
bounded and user-controlled. Club preferences and university policies are
labeled; policies are re-verified against official sources before reliance.
Nothing unconfirmed (room, bio, title) is ever published as fact. Receipts,
request IDs and admin links stay private.
