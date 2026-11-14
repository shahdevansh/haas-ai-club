---
name: haas-ai-club-event
description: Stand up a new Haas AI Club (UC Berkeley) event end to end. Use whenever someone wants to put up, schedule, announce, or organize an AI Club event - lunch & learn, panel, fireside chat, mixer, hackathon, workshop, trek, or summit, in-person, online, hybrid, or offsite. Covers intake questions (with speaker research), an approval-gated plan, EMS room requests, poster design in the club's design language, CampusGroups RSVPs, WhatsApp/Slack marketing copy, haasaiclub.com updates, optional member email blasts, food and event policy, and expense reimbursements.
---

# Haas AI Club Event Setup

This skill codifies the club's operating playbook for putting up a new event.
It is portable: plain Markdown plus dependency-free Python 3 scripts, with no
assumption of a particular agent runtime - see
`references/harness-compatibility.md` for capability mapping and degradation.

## When this triggers

Any request to put up, schedule, announce, promote, or organize a Haas AI Club
event. Typical phrasing: "set up a lunch & learn with <speaker>", "put up an
event for <topic>", "the usuals for <event>".

## Core operating rules (read before anything else)

1. **Intake before planning, plan before doing, approval before publishing.**
   Never book a room, publish an RSVP, send a message, or push a website
   change until the organizer has approved a written plan.
2. **Ask only for organizer-owned facts; research the rest.** Speaker company,
   title and bio are researched from public sources and confirmed, not
   interrogated for. See `references/intake.md`.
3. **Never publish an unverified fact.** An unconfirmed room, a guessed bio, an
   assumed date, or a stale policy must never appear in public copy. Omit
   pending facts; label open items.
4. **Credentials come from the harness's secret store, never from chat.** Duo
   retries are bounded and user-controlled. See
   `references/credentials-and-access.md`.
5. **Distinguish club preference from university policy, and verify policy.**
   Policies (reimbursement, food, alcohol, vendors, accessibility) are checked
   against current official sources with the check date recorded - this skill's
   policy notes are Fall 2026 observations, not current law.
6. **Default to dry-run.** `scripts/event_intake.py --dry-run` produces the
   full plan with zero live actions.

## Workflow

### Step 1 - Intake

Gather what the request does not already state, batched in one message, split
into blocking / optional (defaults shown) / agent-research. Essentials: event
type; format (in-person, online, hybrid, offsite); date, start, end or
duration, timezone; room or venue; headcount; minors; speaker names (+links);
pricing; food; optional email blast. `scripts/event_intake.py` validates
inputs (ISO date, 24h times, IANA timezone, known event type) and prints the
gap split.

### Step 2 - Approval plan

Present the consolidated plan and wait for explicit approval. Execution
sequence (dependencies matter):

1. Space: EMS room request / venue / online-session setup
2. CampusGroups event as an UNPUBLISHED draft -> obtain and verify the public
   RSVP URL (this breaks the poster/QR/RSVP circular dependency)
3. QR from the verified URL -> poster finalized -> attached to the draft
4. Publish the RSVP on approval
5. Marketing message, website update, optional email blast
6. Post-event: category-preserving website moves, turnout, reimbursement

Full template and rules: `references/approval-plan.md`.

### Step 3 - Execute after approval

| Workstream | Reference |
|---|---|
| EMS room request | `references/room-booking-ems.md` |
| CampusGroups event | `references/campusgroups-event.md` |
| Poster design | `references/poster-design.md` |
| Marketing copy | `references/marketing-copy.md` |
| Website update | `references/website-updates.md` |
| Member email blast | `references/email-blast.md` |
| Food, budget, event policy | `references/food-and-budget.md` |
| Reimbursement | `references/reimbursements.md` |
| Completion / resume checklist | `references/completion-checklist.md` |

Track every item on the completion checklist; it doubles as resume state on
interruption (idempotency: check before re-creating). Receipts, request IDs
and admin links stay private.

### Step 4 - After the event

Regular events move Upcoming -> Past on the website (workshops/hackathons and
treks stay in their own sections); speaker cards move only when no future
appearance remains. Record actual turnout. File the reimbursement if the
organizer paid personally, verifying current rules first.

## Testing - exact scope

`scripts/test_dry_run.py` (~50 checks) covers ONLY intake validation, the
gap split, and plan generation - no network, no live mutations, no harness
triggering. Agent judgment is evaluated separately with the scenario prompts
and rubrics in `references/eval-scenarios.md`. Live flows are exercised only
on real approved events, never with fake bookings or sends. See
`references/dry-run-testing.md`.

## Files

- `SKILL.md` - this file
- `references/` - the playbook, one file per workstream
- `scripts/event_intake.py` - intake + plan generator (stdlib only)
- `scripts/test_dry_run.py` - intake/plan test suite (stdlib only)
- `examples/sample-event.json` - a filled-in sample event for testing
