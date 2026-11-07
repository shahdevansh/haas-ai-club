// Haas AI Club - Engage form endpoint (/api/engage)
// Validates the form POST and relays it to the club's private mail endpoint
// (ENGAGE_SCRIPT_URL env var, set in Vercel project settings - never in source).
// Fixed recipients live server-side only. No auto-reply is sent to the submitter.

const TOPICS = new Set([
  'propose-event',
  'propose-track',
  'request-to-speak',
  'propose-sponsorship'
]);

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function page(title, msg, ok) {
  return '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<title>' + title + ' - Haas AI Club</title>' +
    '<style>body{font-family:Roboto,Arial,sans-serif;background:#fff;color:#111;' +
    'display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}' +
    '.card{max-width:480px;padding:2rem;text-align:center}' +
    'h1{font-size:1.4rem;margin-bottom:.75rem}' +
    'a{color:#152f5e}</style></head><body><div class="card">' +
    '<h1>' + title + '</h1><p>' + msg + '</p>' +
    '<p><a href="/engage.html">' + (ok ? 'Back to Engage' : 'Go back and try again') + '</a></p>' +
    '</div></body></html>';
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).setHeader('Content-Type', 'text/html; charset=utf-8')
      .send(page('Not sent', 'This form needs to be submitted from the Engage page.', false));
    return;
  }

  const b = req.body || {};
  const name = String(b.name || '').trim();
  const email = String(b.email || '').trim();
  const topic = String(b.topic || '').trim();
  const message = String(b.message || '').trim();

  // Honeypot: hidden field only bots fill. Pretend success, send nothing.
  if (b.company) {
    res.status(200).setHeader('Content-Type', 'text/html; charset=utf-8')
      .send(page('Message sent', 'Thanks for reaching out - the club will get back to you.', true));
    return;
  }

  // Deployment self-check: dryrun=1 validates and round-trips the mail
  // endpoint without sending. Returns JSON instead of the HTML pages.
  const dryrun = String(b.dryrun || '') === '1';

  const valid = name.length > 0 && name.length <= 200 &&
    EMAIL_RE.test(email) && email.length <= 200 &&
    TOPICS.has(topic) &&
    message.length > 0 && message.length <= 5000;

  if (!valid) {
    res.status(400).setHeader('Content-Type', 'text/html; charset=utf-8')
      .send(page('Check your entries', 'Please fill every field with a valid email and pick one option.', false));
    return;
  }

  const upstream = process.env.ENGAGE_SCRIPT_URL;
  if (!upstream) {
    res.status(500).setHeader('Content-Type', 'text/html; charset=utf-8')
      .send(page('Not sent', 'The form is temporarily unavailable. Please try again later.', false));
    return;
  }

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 10000);
    const resp = await fetch(upstream, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(dryrun ? { name, email, topic, message, dryrun: '1' } : { name, email, topic, message }).toString(),
      redirect: 'follow',
      signal: controller.signal
    });
    clearTimeout(timer);
    const data = await resp.json().catch(() => ({}));

    if (resp.ok && data && data.ok === true) {
      if (dryrun) {
        res.status(200).setHeader('Content-Type', 'application/json; charset=utf-8')
          .send(JSON.stringify({ ok: true, dryrun: true, via: 'api/engage' }));
        return;
      }
      res.status(200).setHeader('Content-Type', 'text/html; charset=utf-8')
        .send(page('Message sent', 'Thanks for reaching out - the club will get back to you.', true));
    } else if (data && data.error === 'rate_limited') {
      res.status(429).setHeader('Content-Type', 'text/html; charset=utf-8')
        .send(page('Slow down', 'Too many messages right now. Please try again in a few minutes.', false));
    } else {
      res.status(502).setHeader('Content-Type', 'text/html; charset=utf-8')
        .send(page('Not sent', 'The form is temporarily unavailable. Please try again later.', false));
    }
  } catch (err) {
    res.status(502).setHeader('Content-Type', 'text/html; charset=utf-8')
      .send(page('Not sent', 'The form is temporarily unavailable. Please try again later.', false));
  }
};
