#!/usr/bin/env python3
"""Haas AI Club event intake + approval-plan generator.

Python 3.9+ stdlib only. No network calls, no live mutations. The test suite
uses temp files for input; the script itself only reads --input and prints.

Usage: python3 event_intake.py --input event.json [--dry-run]

Output modes:
- Validation errors (exit 1): malformed date/time/timezone, unknown event type,
  bad duration/headcount, end not after start without explicit overnight.
- Intake incomplete (exit 2): blocking questions, optional questions with
  defaults, and agent research tasks.
- Complete (exit 0): the approval plan. --dry-run marks actions WOULD-DO.

Input fields: event_type, title, date (ISO), start_time/end_time (24h HH:MM),
end_date (ISO, only when the event crosses midnight), duration_minutes
(positive int, alternative to end_time), timezone (IANA), format, venue,
room_preference, room_confirmed, room_capacity, headcount (int), minors
(true/false or "yes"/"no"), pricing, rsvp_cap (int), speakers[], food,
email_blast.
"""
import argparse, json, re, sys
from datetime import date
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

EVENT_TYPES = ["lunch & learn", "panel", "fireside chat", "mixer",
               "hackathon", "workshop", "trek", "summit"]
SPEAKER_TYPES = {"lunch & learn", "panel", "fireside chat", "summit"}
FOOD_TYPICAL_TYPES = {"lunch & learn", "summit", "hackathon"}
TYPE_DEFAULT_FORMAT = {"mixer": "offsite", "trek": "offsite"}
FORMATS = {"in-person", "online", "hybrid", "offsite"}
TIME_RE = re.compile(r"^([01]?\d|2[0-3]):[0-5]\d$")

def norm_minors(v):
    """Strict: True/False or 'yes'/'no'. Anything else is not an answer."""
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("yes", "y"):
            return True
        if s in ("no", "n"):
            return False
    return None

def present(ev, key):
    return key in ev and ev[key] not in (None, "")

def minutes(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)

def validate(ev):
    errs = []
    et = ev.get("event_type")
    if et and et not in EVENT_TYPES:
        errs.append("unknown event_type %r (known: %s)" % (et, ", ".join(EVENT_TYPES)))
    d = ev.get("date")
    parsed_date = None
    if d:
        try:
            parsed_date = date.fromisoformat(d)
        except (ValueError, TypeError):
            errs.append("date %r is not ISO YYYY-MM-DD" % d)
    ed = ev.get("end_date")
    if ed:
        try:
            date.fromisoformat(ed)
        except (ValueError, TypeError):
            errs.append("end_date %r is not ISO YYYY-MM-DD" % ed)
    for k in ("start_time", "end_time"):
        t = ev.get(k)
        if t and not TIME_RE.match(str(t)):
            errs.append("%s %r is not 24h HH:MM" % (k, t))
    # end vs start: overnight only with an explicit later end_date
    st, en = ev.get("start_time"), ev.get("end_time")
    if st and en and TIME_RE.match(str(st)) and TIME_RE.match(str(en)):
        if minutes(str(en)) <= minutes(str(st)):
            overnight = False
            if ed and parsed_date:
                try:
                    overnight = date.fromisoformat(ed) > parsed_date
                except (ValueError, TypeError):
                    overnight = False
            if not overnight:
                errs.append("end_time %s is not after start_time %s - if the event crosses midnight, set end_date to the next day explicitly" % (en, st))
    if "duration_minutes" in ev and ev["duration_minutes"] is not None:
        dm = ev["duration_minutes"]
        if isinstance(dm, bool) or not isinstance(dm, int) or dm <= 0:
            errs.append("duration_minutes %r must be a positive integer" % (dm,))
    tz = ev.get("timezone")
    if tz and ZoneInfo is not None:
        try:
            ZoneInfo(str(tz))
        except Exception:
            errs.append("timezone %r is not a valid IANA name (e.g. America/Los_Angeles)" % tz)
    hc = ev.get("headcount")
    if hc is not None:
        if isinstance(hc, bool) or not isinstance(hc, int) or hc <= 0:
            errs.append("headcount %r must be a positive integer" % (hc,))
    fmt = ev.get("format")
    if fmt and fmt not in FORMATS:
        errs.append("format %r not one of %s" % (fmt, ", ".join(sorted(FORMATS))))
    cap = ev.get("rsvp_cap")
    if cap is not None and (isinstance(cap, bool) or not isinstance(cap, int) or cap <= 0):
        errs.append("rsvp_cap %r must be a positive integer" % (cap,))
    return errs

def event_format(ev):
    return ev.get("format") or TYPE_DEFAULT_FORMAT.get(ev.get("event_type"))

def needs_room(ev):
    return event_format(ev) in ("in-person", "hybrid")

def intake_gaps(ev):
    blocking, optional, research = [], [], []
    def need(key, q):
        if not present(ev, key):
            blocking.append(q)
    need("event_type", "What type of event? (%s)" % " / ".join(EVENT_TYPES))
    need("title", "Event title?")
    need("date", "Date? (YYYY-MM-DD)")
    need("start_time", "Start time? (24h HH:MM)")
    if not present(ev, "end_time") and not present(ev, "duration_minutes"):
        blocking.append("End time or duration?")
    need("timezone", "Timezone? (America/Los_Angeles for on-campus)")
    need("headcount", "Expected headcount?")
    if norm_minors(ev.get("minors")) is None:
        blocking.append("Will anyone under 18 attend? (yes/no - EMS requires it)")
    if not event_format(ev):
        blocking.append("Format: in-person, online, hybrid, or offsite?")
    fmt = event_format(ev)
    if fmt == "offsite" and not ev.get("venue"):
        blocking.append("Venue / host for the %s?" % ev.get("event_type", "event"))
    if needs_room(ev) and not ev.get("room_confirmed") and not ev.get("room_preference"):
        blocking.append("Room: confirmed room, or what kind should we request? (tiered vs flat, capacity target, building - Chou Hall is the club default)")
    if ev.get("event_type") in SPEAKER_TYPES:
        speakers = ev.get("speakers", [])
        if not speakers and not ev.get("no_speakers"):
            blocking.append("Speakers? Names at minimum; links (LinkedIn/company pages) help me research the rest.")
        for s in speakers:
            if not s.get("name"):
                blocking.append("A speaker entry is missing a name.")
                continue
            missing_facts = [f for f in ("company", "title") if not s.get(f)]
            if missing_facts or (not s.get("bio") and not s.get("bio_unavailable")):
                what = ", ".join(missing_facts + ([] if s.get("bio") or s.get("bio_unavailable") else ["bio"]))
                research.append("Research %s%s from public sources for: %s. Confirm findings with the organizer before publishing; only ask them directly if research fails." % (
                    s["name"],
                    " (%s)" % ", ".join(s["links"]) if s.get("links") else "",
                    what))
            if not s.get("headshot"):
                optional.append("Headshot for %s? (optional asset - website cards and posters need one supplied, never fabricated)" % s["name"])
            if not s.get("class_year"):
                optional.append("Class year for %s if a student (e.g. FTMBA 27)? (optional)" % s["name"])
    if "pricing" not in ev:
        optional.append("Free and open to everyone, or paid/restricted? (default: free, open to everyone)")
    if ev.get("event_type") in FOOD_TYPICAL_TYPES and "food" not in ev:
        optional.append("Food? (yes/no, rough budget, dietary/allergen notes - default: no food unless you say so)")
    if "email_blast" not in ev:
        optional.append("Also send an email blast to all club members with the poster attached? (default: no)")
    return blocking, optional, research

def rsvp_cap(ev):
    if isinstance(ev.get("rsvp_cap"), int) and not isinstance(ev.get("rsvp_cap"), bool) and ev["rsvp_cap"] > 0:
        return ev["rsvp_cap"], "organizer-set"
    cap = ev.get("room_capacity")
    if isinstance(cap, int) and not isinstance(cap, bool) and cap > 0:
        return 2 * cap, "club heuristic ~2x room capacity (based on ~50% show rate; configurable - this is an RSVP-list cap, never permission to exceed safe room occupancy, and host or platform policy caps win)"
    return None, "set with the organizer once room capacity is known (club heuristic ~2x capacity, ~50% show rate)"

def pricing_line(ev):
    p = (ev.get("pricing") or "free").lower()
    if p == "free":
        return '"Free RSVP, open to everyone."'
    return "pricing/audience as supplied (%s) - do NOT use the free/open-to-everyone line" % ev["pricing"]

def when_str(ev):
    end = ev.get("end_time") or "+%smin" % ev.get("duration_minutes")
    end_date = " (ends %s)" % ev["end_date"] if ev.get("end_date") else ""
    return "%s %s-%s %s%s" % (ev["date"], ev["start_time"], end, ev["timezone"], end_date)

def build_plan(ev, dry_run):
    tag = "WOULD-DO" if dry_run else "TO-DO (after your approval)"
    minors = "yes" if norm_minors(ev.get("minors")) else "no"
    fmt = event_format(ev)
    when = when_str(ev)
    lines = ["PLAN FOR: %s" % ev["title"],
             "Type: %s | Format: %s | When: %s | Headcount: %s | Minors under 18: %s" % (
                 ev["event_type"], fmt, when, ev["headcount"], minors), ""]
    n = 0
    def step(text):
        nonlocal n; n += 1
        lines.append("%d. [%s] %s" % (n, tag, text))
    # 1. Space
    if fmt == "online":
        step("Set up the online session (e.g. Zoom link under the organizer's account); link goes on the RSVP, not the public website.")
    elif fmt == "offsite":
        step("Venue/logistics for the %s at %s; budget options presented before any spend." % (ev["event_type"], ev.get("venue")))
    else:
        if ev.get("room_confirmed"):
            step("Use the confirmed booking %s for %s: first verify the existing EMS reservation actually covers this room, date and time (confirmation email or EMS record) - do NOT submit a duplicate request. If it does not match, say so and request instead." % (
                ev["room_confirmed"], when))
        else:
            room = ev.get("room_preference") or "best-fit Chou Hall room for %d" % ev["headcount"]
            step("Request %s in Haas EMS for %s, headcount %s, club Haas AI Club, minors under 18: %s (PENDING EMS confirmation - will not appear on any public copy until confirmed). EMS confirms by email; a submission is not a booking. Record the request ID privately." % (
                room, when, ev["headcount"], minors))
        if fmt == "hybrid":
            step("Set up the online session too (hybrid); link goes on the RSVP only.")
    # 2. Draft RSVP -> URL whose TARGET is verified while authenticated
    cap, cap_note = rsvp_cap(ev)
    cap_txt = ("RSVP cap %d (%s)" % (cap, cap_note)) if cap else ("RSVP cap: " + cap_note)
    step("Create the CampusGroups event as an UNPUBLISHED draft: title, date/time (%s), speaker line (class year, company, one line on topic), %s, %s. Obtain the draft's public RSVP URL; while authenticated as the organizer, confirm that URL targets this event. Note: a draft's public URL may not resolve anonymously before publication - anonymous verification happens right after authorized publish (step 4), never publish merely to test the link." % (
        when, cap_txt, pricing_line(ev)))
    # 3. QR + poster -> attach
    step("Generate the square QR from the draft's public RSVP URL (target confirmed in step 2), then finalize the poster (two options in the club design language; organizer picks one) with that QR. Attach the final poster to the draft event.")
    # 4. Publish -> anonymous verification
    step("Publish the RSVP on approval (poster attached; room/venue shown exactly as confirmed - omitted while pending). Immediately re-verify the public RSVP URL anonymously (logged-out) to confirm it resolves to this event before the link circulates anywhere.")
    # 5. Marketing
    step("Marketing message for WhatsApp/Slack: title on top, emoji-labeled time and venue lines, 2-3 lines on why it matters, the now-anonymously-verified RSVP link. Drafted for the organizer to send; venue line appears only once confirmed.")
    # 6. Website
    site_sections = {"hackathon": "Hackathons & Workshops", "workshop": "Hackathons & Workshops", "trek": "Treks"}
    if ev["event_type"] in site_sections:
        step("Website: add \"%s\" to Events > %s with the public RSVP link (date + title + Go to Event only)." % (ev["title"], site_sections[ev["event_type"]]))
    else:
        step("Website: add \"%s\" to Events > Upcoming (chronological, earliest first) with the public RSVP link (date + title + Go to Event only)." % (ev["title"],))
    for s in ev.get("speakers", []):
        step("Website: Speakers card for %s (%s, %s) - reuse the existing card if they already have one; circular photo face-centered ~70%%, company logo, confirmed title only." % (
            s["name"], s.get("company", "?"), s.get("title", "?")))
    if ev.get("email_blast"):
        step("Email blast to all members: short note + poster attached, drafted for approval before sending; member list from the club roster, BCC or platform-individual sends.")
    if ev.get("food"):
        step("Food: %s. Spend only after an explicit yes with the amount; keep the itemized receipt; verify allergen labeling and current campus food/vendor rules before ordering (see references/food-and-budget.md)." % ev["food"])
    step("After the event: move the Events entry to Past (regular events only - workshops/hackathons stay in Hackathons & Workshops, treks in Treks), move speaker cards Upcoming->Past only when no future appearance remains, record actual turnout privately, file the CalLink reimbursement if the organizer paid personally.")
    open_items = []
    if needs_room(ev) and not ev.get("room_confirmed"):
        open_items.append("room availability unknown until EMS responds - nothing public will name a room")
    for s in ev.get("speakers", []):
        if not s.get("bio") and s.get("bio_unavailable"):
            open_items.append("bio for %s unavailable - public copy will not assert one" % s["name"])
        if s.get("title") and not s.get("title_confirmed"):
            open_items.append("title for %s unconfirmed - Speakers card held until confirmed" % s["name"])
    if open_items:
        lines += ["", "OPEN ITEMS (never published as fact):"] + ["- " + o for o in open_items]
    lines += ["", "All confirmation IDs, request numbers, and receipts are recorded privately with the organizer, never in the public repo or shared artifacts.",
              "DRY RUN - no actions taken. Present to the organizer for approval before any execution." if dry_run else
              "Approve, or say what to change."]
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    with open(a.input) as f:
        ev = json.load(f)
    errs = validate(ev)
    if errs:
        print("INPUT ERRORS:")
        for e in errs:
            print("- " + e)
        sys.exit(1)
    blocking, optional, research = intake_gaps(ev)
    if blocking or research:
        if blocking:
            print("MISSING - BLOCKING (must come from the organizer):")
            for q in blocking: print("- " + q)
        if optional:
            print("\nMISSING - OPTIONAL (defaults in parentheses; skip is fine):")
            for q in optional: print("- " + q)
        if research:
            print("\nAGENT RESEARCH (agent does this from public sources; organizer only confirms):")
            for r in research: print("- " + r)
        sys.exit(2)
    if optional:
        print("OPTIONAL DEFAULTS APPLIED (organizer can override):")
        for q in optional: print("- " + q)
        print()
    print(build_plan(ev, a.dry_run))

if __name__ == "__main__":
    main()
