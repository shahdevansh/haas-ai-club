# Dry-run testing - exact scope

## What the test suite covers

`scripts/test_dry_run.py` (~50 checks) exercises ONLY the intake and
plan-generation core: input validation (dates, times, timezones, event types),
the blocking/optional/research gap split, plan contents, execution sequencing
(draft RSVP before QR before publish), pricing and minors correctness, and the
no-fabrication guards (pending room, missing bio, unconfirmed title). It makes
no network calls and performs no live mutations; it writes only temporary
input files for the script under test.

## What it does NOT cover

- Skill triggering inside any particular agent harness.
- Any live integration (EMS, CampusGroups, CalLink, GitHub, email, Figma).
- Agent judgment calls - those are covered by references/eval-scenarios.md,
  which you run as prompted evaluations, not unit tests.

Live flows are only exercised on a real event with the organizer's approval.
Never create fake events, bookings, or sends just to test.

## Run

    python3 scripts/test_dry_run.py

Exit code 0 and "ALL TESTS PASSED" means the intake/planning core is behaving.
