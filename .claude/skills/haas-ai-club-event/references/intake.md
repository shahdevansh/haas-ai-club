# Intake: what to ask, what to research, what to default

Ask only for facts that are truly the organizer's to give. Batch all
outstanding questions into one short message - never drip-feed. The intake
script (`../scripts/event_intake.py`) splits gaps into three classes; mirror
that split in conversation:

1. **Blocking - must come from the organizer.** Event type, title, date,
   start time, end time or duration, timezone, headcount, minors (yes/no),
   format (in-person / online / hybrid / offsite), room or venue, and speaker
   names for speaker events.
2. **Optional - defaults exist; skipping is fine.** Pricing (default free and
   open to everyone), food (default none), email blast (default no), headshots
   and logos (optional assets), speaker class year.
3. **Agent research - do not interrogate the organizer for these.** Given a
   speaker's name plus any links (LinkedIn, company page), research company,
   title and bio from public sources yourself. Show the organizer what you
   found for confirmation; ask them directly only when research fails. Never
   publish a bio or title they haven't confirmed.

## The blocking question set

1. **Event type** - lunch & learn, panel, fireside chat, mixer, hackathon,
   workshop, trek, summit. Type drives routing: talks get the full pipeline;
   mixers/treks are offsite; hackathons/workshops/treks have their own website
   sections.
2. **Format** - in-person, online, hybrid, or offsite (mixers/treks default to
   offsite). Online events skip EMS and get an online-session link on the RSVP
   only. Hybrid needs both.
3. **Date, start time, end time or duration, timezone.** Validate the weekday
   against the date; confirm the timezone (America/Los_Angeles on campus). Ask
   about setup time: a room hold can start before the published start time -
   the public time stays the event's start even if the room is held earlier.
4. **Room or venue.** In-person/hybrid: a confirmed room, or the kind of room
   to request (tiered vs flat, capacity target, building - Chou Hall is the
   club default). Offsite: the venue. If no room fits the requested time,
   offer both a smaller room at the requested time and a later slot in a
   bigger room - the organizer picks.
5. **Headcount and minors.** Headcount drives room size and the RSVP-cap
   suggestion. EMS requires the under-18 answer; the club default for speaker
   events has been "no minors" - confirm, don't assume.
6. **Speakers** (speaker events): names at minimum. Everything else is
   research + confirmation (above) plus optional assets.

## Defaults the organizer has used before (club preferences, not policy)

- "All the usuals" = poster + CampusGroups event + room reservation.
- RSVP cap heuristic: ~2x room capacity on an observed ~50% show rate. This is
  a configurable club heuristic for the RSVP list only - never permission to
  exceed safe occupancy, and any host or platform cap wins.
- The organizer may publish the RSVP before the room is confirmed. Their call
  to offer, not yours to make silently: publish with the room omitted, add it
  when EMS confirms. Never print an unconfirmed room.

## Automate it

`../scripts/event_intake.py --input event.json [--dry-run]` validates inputs
(ISO date, 24h times, IANA timezone, known event type), then prints the
blocking/optional/research split or the full plan.
