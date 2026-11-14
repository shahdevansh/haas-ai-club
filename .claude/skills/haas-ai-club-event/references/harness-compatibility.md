# Harness compatibility

This skill is harness-agnostic by design: Markdown playbook + Python 3 stdlib
scripts. It makes **no assumptions about built-in integrations**. Before
executing, map each capability to what your harness actually provides, and
degrade to "produce the artifact + hand-off instructions" when a capability
is missing.

## Capability map

| Capability the playbook uses | If the harness has it | If it does not |
|---|---|---|
| Web browser automation | Drive EMS, CampusGroups, CalLink, and live-site verification directly | Produce filled-in checklists and exact click paths for the human; they execute, you verify results from what they paste back |
| Secret store | Pull CalNet/GitHub/email credentials from it | Never substitute chat-transmitted passwords; the human logs in themselves |
| Git / GitHub push | Commit and push the website update | Produce the patch or edited files for the human to commit |
| Image generation/editing | Render poster options and circular crops | Provide exact poster specs for a designer or design tool; Figma holds the official assets |
| Email sending | Draft, then send on approval | Draft only; the human sends |
| QR generation | Generate locally once the RSVP link exists | Use any QR tool; the requirement is a square QR aligned with the set |

## Bounded claims

- "Works in any harness" means: the playbook reads as plain instructions and
  the scripts run on Python 3.9+ with no dependencies. It does **not** mean
  every harness can click through CalNet - say which mode you are in.
- The dry-run suite (scripts/test_dry_run.py) exercises intake and planning
  with zero external calls, so it validates identically everywhere.

## Importing

- Claude Code / Claude Agent skills: place this directory in the skills folder;
  SKILL.md frontmatter is the manifest.
- Other harnesses: treat SKILL.md as the entry prompt and the references/
  directory as loadable context; scripts run as ordinary shell commands.
