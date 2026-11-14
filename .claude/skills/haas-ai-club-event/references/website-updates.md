# Updating haasaiclub.com

Public static site at https://haasaiclub.com, source in the public GitHub repo
`shahdevansh/haas-ai-club`. Owner pushes to `main` auto-deploy. The repo is
public: no secrets, credentials, request IDs, or internal documents ever go
into it.

Pages: Home (index.html), Events (events.html), Speakers (speakers.html),
Team (team.html), Engage (engage.html - has its own backend; leave it and its
`api/` alone).

## Adding an event (events.html)

Sections in order: Upcoming Events, Past Events, Hackathons & Workshops,
Treks. Pick the section by event type: talks/panels/firesides/mixers/summits
go to Upcoming; hackathons and workshops go to Hackathons & Workshops; treks
go to Treks.

**Ordering is fixed:** Upcoming is chronological, earliest first. Past is most
recent first. Hackathons & Workshops and Treks keep their existing order.

Entry markup (copy an existing entry exactly):

    <div class="ev">
      <div class="evd">Nov 24, 2026</div>
      <div class="evm"><div class="evt">Event Title</div></div>
      <a class="evgo" href="<public RSVP URL>" target="_blank" rel="noopener">Go to Event &rarr;</a>
    </div>

- Date format `Mon D, YYYY`; ranges as `Nov 14-15, 2025`. No times, venues, or
  descriptive subtext - date, title, link only. Omit the `<a>` if there is no
  public link.
- **After the event:** a regular event's entry moves from Upcoming to Past.
  Hackathons/workshops and treks stay in their own sections - do NOT move them
  into Past Events. Add new ones to their section directly.
- Before adding, check the event is not already listed (idempotency).

## Adding a speaker (speakers.html)

Upcoming holds confirmed guests whose sessions are ahead; Past holds everyone
who has taken the stage.

- **Dedupe first:** if the speaker already has a card, do not add another.
  Reuse it. Move a card Upcoming -> Past only when the speaker has no future
  appearance remaining; if they are booked again later, the card stays in (or
  returns to) Upcoming.
- Card markup:

      <div class="spkcard"><img class="face" src="assets/speakers/<slug>.jpg" alt="<Name>"><div class="nm"><Name></div><img class="lg" src="assets/logos/<company>.svg" alt="<Company>"><div class="cn"><Company></div><div class="ti"><Title></div></div>

- Photo: circular crop, face centered and filling ~70% of the circle, no black
  surround. Never fabricate a photo - coordinate with the organizer instead.
- Company logo: reuse an existing asset in `assets/logos/` when the company
  already appears; otherwise obtain a legitimate logo. When no logo asset is
  right, use the text fallback `<div class="lgtxt">Company</div>` (and drop the
  `.cn` line), matching existing cards.
- Title is the speaker's confirmed current role - never a guess. Unconfirmed:
  hold the card out of the deploy.
- Grid: six-across desktop, two-across mobile. Preserve spacing; do not re-add
  any caption line below section headings.

## Deploy safety

- Commit only the files the change needs; plain commit message.
- Only the repo owner's pushes deploy. Pushing as a collaborator does not
  update the site - say so and hand the owner the push/merge.
- After deploy, verify live: fetch the page, confirm the new entry renders and
  every asset URL returns 200; check desktop and mobile widths if structure
  changed. Do not report done on an unverified deploy.
