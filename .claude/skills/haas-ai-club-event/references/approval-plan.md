# The approval plan

After intake, present one consolidated plan and wait for explicit approval
before touching any live system. Re-present the plan if material facts change
(room, time, speaker lineup, pricing). The generator
(`../scripts/event_intake.py`) produces this plan; the rules below govern it.

## Execution sequence (dependency order)

1. **Space first.** EMS room request (in-person/hybrid), venue logistics
   (offsite), or online-session setup (online). EMS submissions are requests -
   the room is pending until the confirmation email lands.
2. **Draft the RSVP to get the link.** Create the CampusGroups event as an
   UNPUBLISHED draft, obtain its public RSVP URL, and confirm the target
   while authenticated (a draft URL may not resolve anonymously - anonymous
   verification happens right after the authorized publish, never publish
   just to test).
3. **QR, then poster.** Generate the square QR from the target-confirmed URL,
   finalize the poster with it, attach the poster to the draft event. Do not block the
   RSVP on a finished poster - the draft exists precisely to break that
   circular dependency.
4. **Publish on approval.** Publish the RSVP only with poster attached and
   room/venue shown exactly as confirmed (omitted while pending). Immediately
   re-verify the public URL anonymously before it circulates.
5. **Marketing message, website update, optional email blast** - all need the
   verified public RSVP link, so they follow it.
6. **After the event** - website moves to Past (category-preserving), turnout
   recorded, reimbursement if the organizer paid.

## Template

    Plan for: <event title>
    Type / format / date / time+timezone / headcount / minors: <actual values>

    1. Room: <if a booking exists: "Use confirmed booking <room> - first verify
       the existing EMS reservation covers this room/date/time; no duplicate
       request"> <otherwise: "Request <room candidate(s)> in Haas EMS for <time
       window incl. setup>">, headcount <n>, club Haas AI Club, minors under 18:
       <yes/no as answered>. EMS confirms by email; a submission is not a
       booking.
    2. RSVP: create the CampusGroups event as an unpublished draft, get and
       verify the public RSVP link. Pricing line: <"Free RSVP, open to
       everyone." if free/open; otherwise the actual pricing/audience>.
       RSVP cap <n> <heuristic or organizer-set>.
    3. Poster: two options in the club design language; QR from the verified
       link; you pick one; attached to the draft event.
    4. Publish the RSVP on your approval.
    5. Marketing message for WhatsApp/Slack (emoji style, title/time/venue on
       top) drafted for you to send.
    6. Website: Events entry <section><, Speakers card for <name> (reuses an
       existing card if they already have one)>.
    7. Optional email blast with poster attached: <yes/no>.
    8. Food: <plan or none - spend only on your explicit yes with the amount>.
    9. After the event: category-preserving website moves, turnout recorded,
       reimbursement filed if you paid personally.

    Open items I cannot verify yet: <list>.
    Approve, or tell me what to change.

## Rules

- The plan states what will be done, where, and in whose name. No silent
  additions afterwards. Approval of the plan is not approval to spend money -
  any spend needs its own explicit yes with the amount.
- If a step is blocked on a credential or a Duo approval, say so in the plan.
  Don't promise a Duo-gated action until a login has actually worked.
- Confirmation IDs, request numbers, RSVP/admin links and receipts are
  recorded privately with the organizer - never in the public repo, posters,
  or shared artifacts. Only the public RSVP URL circulates.
- Idempotency: before creating anything, check it does not already exist (an
  RSVP for this date/title, a website entry, a speaker card). If a run is
  interrupted, resume from the checklist state (see completion-checklist.md)
  instead of re-creating - duplicate RSVPs and duplicate website entries are
  the common failure.
- Keep all surfaces in sync: a change to title, time, venue, or poster
  propagates to CampusGroups, poster, website, marketing copy, and any queued
  email in the same pass.
