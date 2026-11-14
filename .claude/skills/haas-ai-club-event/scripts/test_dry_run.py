#!/usr/bin/env python3
"""Dry-run test suite for the haas-ai-club-event skill.

Scope (exactly): exercises the intake validation, gap detection, and
approval-plan generation in scripts/event_intake.py. It does NOT test skill
triggering inside an agent harness, and it touches NO live system (no
network, no bookings, no sends, no pushes). It writes only temporary input
files for the script under test.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
INTAKE = os.path.join(HERE, "event_intake.py")
SAMPLE = os.path.join(HERE, "..", "examples", "sample-event.json")
failures = []

def run_intake(ev):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(ev, f)
        path = f.name
    try:
        p = subprocess.run([sys.executable, INTAKE, "--input", path, "--dry-run"],
                           capture_output=True, text=True)
        return p.returncode, p.stdout
    finally:
        os.unlink(path)

def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL") + ": " + name + ((" - " + detail) if detail and not cond else ""))
    if not cond:
        failures.append(name)

with open(SAMPLE) as f:
    SAMPLE_EV = json.load(f)

# --- 1. Minimal intake: blocking vs optional vs research split
rc, out = run_intake({"event_type": "lunch & learn", "title": "AI for Testing"})
check("minimal intake exits 2", rc == 2)
for q in ("Date?", "Start time", "End time or duration", "Timezone", "headcount", "under 18", "Format"):
    check("blocking asks: %s" % q, q in out)
check("blocking section labeled", "MISSING - BLOCKING" in out)
check("optional section labeled", "OPTIONAL" in out)

# --- 2. minors boolean false must NOT re-ask; room_confirmed satisfies room question
ev = dict(SAMPLE_EV)
rc, out = run_intake(ev)
check("minors=false accepted (exit 0)", rc == 0, out[:300])
check("minors reported as no", "Minors under 18: no" in out)
ev2 = dict(SAMPLE_EV); ev2.pop("room_confirmed"); ev2.pop("room_capacity")
rc2, out2 = run_intake(ev2)
check("missing room asks when neither confirmed nor preferred", rc2 == 2 and "Room:" in out2)
ev3 = dict(SAMPLE_EV); ev3.pop("room_preference", None)
rc3, out3 = run_intake(ev3)
check("room_confirmed alone satisfies room intake", rc3 == 0)

# --- 3. Online format: no room question, no EMS step, has online-session step
ev = dict(SAMPLE_EV, format="online")
ev.pop("room_confirmed", None); ev.pop("room_capacity", None)
rc, out = run_intake(ev)
check("online intake complete without room", rc == 0, out[:300])
check("online plan has online-session step", "online session" in out)
check("online plan has no EMS request", "Haas EMS" not in out)

# --- 4. Validation errors
rc, out = run_intake(dict(SAMPLE_EV, event_type="rave"))
check("unknown event_type errors (exit 1)", rc == 1 and "unknown event_type" in out)
rc, out = run_intake(dict(SAMPLE_EV, date="next Tuesday"))
check("bad date errors", rc == 1 and "not ISO YYYY-MM-DD" in out)
rc, out = run_intake(dict(SAMPLE_EV, timezone="PST"))
check("non-IANA timezone errors", rc == 1 and "IANA" in out)
rc, out = run_intake(dict(SAMPLE_EV, start_time="noon"))
check("bad start_time errors", rc == 1 and "HH:MM" in out)
rc, out = run_intake(dict(SAMPLE_EV, headcount="lots"))
check("bad headcount errors", rc == 1 and "headcount" in out)

# --- 5. Full sample: plan contents
rc, out = run_intake(SAMPLE_EV)
check("complete intake exits 0", rc == 0)
check("plan is dry-run marked", "WOULD-DO" in out and "no actions taken" in out)
for work in ("EMS", "Poster", "CampusGroups", "Marketing", "Website", "Email blast", "Food", "reimbursement"):
    check("plan covers %s" % work, work.lower() in out.lower())
check("RSVP cap is 2x room capacity (76 -> 152)", "cap 152" in out)
check("cap labeled configurable heuristic, not occupancy permission", "never permission to exceed safe room occupancy" in out)
check("Upcoming is chronological earliest-first", "chronological, earliest first" in out)
check("IDs/receipts kept private", "recorded privately" in out)

# --- 6. Sequence: draft RSVP -> QR -> poster -> publish
i_draft = out.find("UNPUBLISHED draft")
i_qr = out.find("square QR from the draft's public RSVP URL")
i_publish = out.find("Publish the RSVP")
check("sequence: draft RSVP before QR before publish", -1 < i_draft < i_qr < i_publish)

# --- 7. Section routing and post-event category preservation
rc, out = run_intake(dict(SAMPLE_EV, event_type="workshop", email_blast=False, food=None))
check("workshop routes to Hackathons & Workshops", "Hackathons & Workshops" in out)
check("workshops not moved to regular Past", "stay in Hackathons & Workshops" in out)

# --- 8. Paid/restricted events never assert free/open
rc, out = run_intake(dict(SAMPLE_EV, pricing="paid $10"))
check("paid event omits free/open line", "Free RSVP, open to everyone" not in out)
check("paid event flags pricing copy", "do NOT use the free/open" in out)

# --- 9. Speaker research, not interrogation: name + link only
ev = dict(SAMPLE_EV)
ev["speakers"] = [{"name": "New Speaker", "links": ["https://www.linkedin.com/in/example"]}]
rc, out = run_intake(ev)
check("speaker with name+link is not blocking", rc == 2 and "MISSING - BLOCKING" not in out.split("AGENT RESEARCH")[0].replace("OPTIONAL", ""))
check("research task issued for company/title/bio", "AGENT RESEARCH" in out and "Research New Speaker" in out)
check("headshot is optional, not blocking", "Headshot for New Speaker? (optional" in out)

# --- 10. No-fabrication guard
ev = dict(SAMPLE_EV)
ev.pop("room_confirmed"); ev["room_preference"] = "tiered, ~76 seats"
ev["speakers"] = [{"name": "Un Bio", "company": "TestCo", "title": "CEO", "bio_unavailable": True}]
rc, out = run_intake(ev)
check("pending room labeled, not asserted", "PENDING EMS confirmation" in out)
check("missing bio listed as open item", "bio for Un Bio unavailable" in out)
check("unconfirmed title held from Speakers card", "title for Un Bio unconfirmed" in out)
check("open items section present", "OPEN ITEMS" in out)

# --- 11. Recurring speaker dedupe instruction present
check("plan dedupes recurring speakers", "reuse the existing card" in out)

# --- 12. Minors reflected when true (not hardcoded no)
rc, out = run_intake(dict(SAMPLE_EV, minors=True))
check("minors=true carried into plan", "Minors under 18: yes" in out)

# --- 13. Strict minors: unrecognized string is not an answer
rc, out = run_intake(dict(SAMPLE_EV, minors="maybe"))
check("minors 'maybe' is re-asked, not coerced", rc == 2 and "under 18 attend" in out)

# --- 14. Strict duration validation
rc, out = run_intake(dict(SAMPLE_EV, duration_minutes=0))
check("duration 0 rejected", rc == 1 and "positive integer" in out)
rc, out = run_intake(dict(SAMPLE_EV, duration_minutes=-30))
check("negative duration rejected", rc == 1)
rc, out = run_intake(dict(SAMPLE_EV, duration_minutes="90"))
check("string duration rejected", rc == 1 and "positive integer" in out)

# --- 15. Null end_time and null duration do not bypass the missing check
ev = dict(SAMPLE_EV); ev["end_time"] = None; ev["duration_minutes"] = None
rc, out = run_intake(ev)
check("null end+duration asks End time or duration", rc == 2 and "End time or duration" in out)

# --- 16. Bool headcount rejected
rc, out = run_intake(dict(SAMPLE_EV, headcount=True))
check("bool headcount rejected", rc == 1 and "headcount" in out)

# --- 17. End before start: rejected without explicit overnight end_date
rc, out = run_intake(dict(SAMPLE_EV, start_time="22:00", end_time="01:00"))
check("end<=start rejected without end_date", rc == 1 and "crosses midnight" in out)
rc, out = run_intake(dict(SAMPLE_EV, start_time="22:00", end_time="01:00", end_date="2026-11-11"))
check("overnight allowed with explicit end_date", rc == 0 and "ends 2026-11-11" in out)

# --- 18. Confirmed room: reuse/verify, never a duplicate request
rc, out = run_intake(SAMPLE_EV)
check("confirmed room verifies existing booking", "Use the confirmed booking Chou N300" in out and "do NOT submit a duplicate request" in out)
check("confirmed room plan has no new request step", "Request Chou N300 in Haas EMS" not in out)
ev = dict(SAMPLE_EV); ev.pop("room_confirmed"); ev["room_preference"] = "tiered"
rc, out = run_intake(ev)
check("unconfirmed room does request via EMS", "Request tiered in Haas EMS" in out)

# --- 19. Two-phase RSVP URL verification, no publish-just-to-test
rc, out = run_intake(SAMPLE_EV)
check("draft URL target confirmed while authenticated", "while authenticated as the organizer, confirm that URL targets this event" in out)
check("anonymous verification after authorized publish", "may not resolve anonymously before publication" in out and "never publish merely to test" in out)
check("post-publish anonymous re-verify step", "re-verify the public RSVP URL anonymously" in out)

print()
if failures:
    print("%d FAILURES: %s" % (len(failures), "; ".join(failures)))
    sys.exit(1)
print("ALL TESTS PASSED (%d checks)" % 0 if False else "ALL TESTS PASSED")
