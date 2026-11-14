# CampusGroups event

The club's CampusGroups page (group slug `haic`) is where RSVPs live. Creating
events requires the organizer's login (CalNet-backed) via the harness secret
store.

## Sequence (breaks the poster/QR/RSVP circular dependency)

1. Create the event as an **unpublished draft** with title, date/time, and
   details. Do not wait for a finished poster.
2. Obtain the draft's **public RSVP URL**. A draft's public URL may not
   resolve anonymously before publication, so verification is two-phase:
   (a) while authenticated as the organizer, open the URL and confirm it
   targets this event (right title/date - not some other event's link);
   (b) immediately AFTER the authorized publish, re-verify the URL anonymously
   (logged out) before the link circulates anywhere. Never publish merely to
   test a link.
3. Generate the poster's QR from that target-confirmed URL; finalize the
   poster; upload it to the draft as flyer/banner.
4. Publish only on the organizer's plan approval, then run phase (b). If the
   anonymous check fails, pull the link from all queued copy and fix before
   anything circulates.

## Event copy pattern (club preference)

- Title = event title.
- Speaker (class year if a student), company, one line on the topic.
- If the event is free and open: close with "Free RSVP, open to everyone."
  If it is paid or restricted, say exactly that instead - never default to
  free/open.
- Date/time/location exactly as confirmed. Room pending? Publish without it
  (organizer's call to gather RSVPs early) and add it when EMS confirms.
  Never print an unconfirmed room.
- RSVP cap: the club heuristic is ~2x room capacity (observed ~50% show rate).
  It is configurable, it caps the RSVP list only - never safe occupancy - and
  any host or platform cap wins. Raise on the organizer's request.

## Links

- Always share the **public RSVP link** (the rsvp_boot URL), never the
  event_form edit link. Marketing, poster QR, website "Go to Event" and the
  email blast all use the public link.
- Verify the link opens the right event before circulating it. Keep the admin/
  edit link private.

## Keep in sync

Any change to title, time, venue or poster propagates to CampusGroups (title,
location, description, flyer/banner) and every other surface in the same pass.
The organizer expects this without being asked.

## Series rule: AI Risk Speaker Series

Co-hosted AI Risk Speaker Series events use RSVP cap 50 max (organizer's
instruction 2026-11-09), overriding the ~2x-room-capacity heuristic.
