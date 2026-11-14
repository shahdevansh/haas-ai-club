# Food, budget, and event policy

Club history below is anecdote, not policy. **Verify current campus rules
before any order, venue booking, or alcohol-adjacent plan**, and say what you
verified vs what you assumed. The pointers below are discovery starting
points, not verified current links - find the live policy page, read it, and
record what you verified and when.

## Verify against current policy

- **Campus food/catering rules** - whether outside food vendors are allowed in
  the booked room, and any preferred-vendor or insurance requirements (Haas
  space management / the EMS booking terms for the room).
- **Allergen and food-safety handling** - label common allergens, collect
  dietary needs on the RSVP when a full meal is served, keep perishables safe
  for the serving window.
- **Alcohol** - any event with alcohol needs explicit verification of current
  campus alcohol policy and venue licensing before planning; do not rely on
  past events as precedent.
- **Vendor/payment rules** - whether the reimbursement path accepts how you
  plan to pay (see reimbursements.md).
- **Accessibility** - confirm the room/venue is accessible; include an
  accommodation contact line in event copy when the audience is campus-wide.

## What has worked (club history)

- Lunch & learns (50-70 headcount): pizza delivery (DoorDash/Uber Eats) paid
  personally, then reimbursed. Order for expected turnout, not RSVP count
  (~50% show rate is the organizer's working assumption).
- Mixers: the organizer chose venue + one drink per guest, no food, after a
  catered-food quote came to ~$20/head before tax, drinks and space fees -
  present that tradeoff when a mixer budget comes up.

## Budget hygiene

- Any spend needs the organizer's explicit yes with the amount, in advance.
- Keep the itemized paid receipt from the moment of purchase - reimbursement
  depends on it (see reimbursements.md).

## Ordering with the DoorDash CLI (dd-cli)

The club's default self-serve path for pizza/lunch delivery is the DoorDash
CLI (`dd-cli`), driven by the agent. It searches stores, builds the cart,
previews exact pricing, and submits - on the organizer's own DoorDash account
and saved card.

### Install and sign-in

- Install only from the official `doordash-oss/doordash-cli` GitHub releases;
  verify the published SHA256 checksum before running the binary (the README's
  security notice requires it). macOS Apple Silicon and Linux x86_64 builds
  are published.
- The CLI ships its own agent skill at `skills/dd-cli-usage/SKILL.md` in the
  release tarball - read it first; it owns command usage, `--intent`, exit
  codes, and card-handling rules.
- On a headless machine (no keychain/browser), sign in with the two-step
  flow: `dd-cli export-token --start`, the organizer opens the printed
  DoorDash URL and signs in, the browser lands on a "localhost refused to
  connect" error page (expected), they paste back the full address-bar URL,
  then `dd-cli export-token --finish '<url>'`. Set the printed token as
  `DD_CLI_ACCESS_TOKEN`. The pending sign-in is valid 10 minutes; the token
  lasts ~72 hours (`dd-cli auth status` shows expiry).
- The token is a credential: never print it, commit it, or send it in chat
  (see credentials-and-access.md). Store it only in the harness's secret
  store or a private env file.

### Ordering flow for an event

1. Confirm headcount (expected turnout, not RSVP count - ~50% show rate is
   the organizer's working assumption), delivery address and drop-off note
   (e.g. "Chou Hall, 2220 Piedmont Ave, ground floor"), arrival time, and the
   all-in budget ceiling.
2. `dd-cli address list` - the delivery address must be a saved DoorDash
   address; add it (`dd-cli address add`) if missing.
3. Search pizza/lunch stores near the venue, shortlist 2-3, and build carts
   sized to expected turnout (club baseline: ~10 XL pizzas for 60-70 people,
   a vegetarian/vegan share, plus sodas).
4. Use scheduled ("Schedule Ahead") delivery for a fixed arrival time; ASAP
   only for same-hour orders.
5. `dd-cli order preview` gives the exact all-in total (items, fees, tax,
   tip). Present 2-3 options with their exact totals and the card's display
   name. **The organizer approves one option and its exact total before
   submit** - the budget ceiling is hard, never exceed it.
6. Submit only after that approval. On a scheduled order, submit charges the
   account's default card - name it in the approval step.
7. After the order, keep the itemized receipt (`dd-cli order history`) - the
   reimbursement claim needs it (see reimbursements.md).
