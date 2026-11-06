# Plan: password-protected pages (party FAQ)

Status: implemented. `encrypt.py`, `templates/locked.html`, `load_locked()` in `build.py`;
tests in `tests/test_private.py` and the two `test_locked_page_*` layout tests.

The problem: GitHub Pages serves every file to anyone, and the repo is public. There is no
server to check a password, so "private" has to mean *encrypted*: the page ships as
ciphertext plus a small script, and the guest's browser decrypts it with the password.
Without the password, the deployed page and the repo hold nothing readable.

The FAQ is a standalone HTML file (its own styles, not the site's templates), so the whole
document is encrypted as-is and swapped in after decryption.

## The threat model, stated plainly

- **Keeps out:** search engines, people browsing the repo or the site, anyone who finds the
  URL without the password.
- **Doesn't keep out:** a guest who forwards the password. There is no revoking it; rotating
  the password only protects future versions (old ciphertext stays in git history and the
  Wayback Machine, decryptable with the old password).
- **Offline guessing:** the ciphertext is public, so the password is the only thing standing
  between it and a brute-force attempt. Use a random 4–5 word passphrase, not `party2026`.
  The key derivation is deliberately slow (PBKDF2-SHA256, 600,000 iterations) to make
  guessing expensive.
- Good enough for a party FAQ (address, timings, dress code). Not for anything you'd mind
  leaking.

## Why not GitHub Secrets

The two "privacy risks" are really one: the plaintext must never be committed. GitHub Secrets
would let CI do the encryption, but it buys nothing here:

- The deployed page has to contain the ciphertext anyway, so committing that same ciphertext
  reveals nothing new.
- Secrets are write-only and capped at 48 KB: every FAQ edit becomes "paste the whole file
  into the GitHub UI", with no diff and no local preview. A self-contained HTML file with
  inline CSS (and maybe images) can easily pass 48 KB.
- The password would sit in one more place.

So: **encrypt locally, commit only the ciphertext.** CI needs no secrets and no new
dependencies; the password lives only in your head / password manager and with your guests.

## 1. Source and ciphertext layout

```
private/                  # gitignored — plaintext never leaves your machine
  party.html              # the standalone FAQ, exactly as you'd open it in a browser
content/locked/
  party.json              # committed: {salt, iv, iterations, ciphertext}
```

- Add `private/` to `.gitignore`. Back `private/party.html` up somewhere (password manager
  note, a private repo, iCloud) — it is the only copy of the plaintext.
- The FAQ must be **fully self-contained**: inline `<style>`, inline `<script>`, images as
  `data:` URIs. Anything it loads from `static/` or a relative path is public. Google Fonts or
  a CDN are fine (they reveal nothing about the content).
- The public shell gets a generic `<title>` ("Private page") so the tab and link previews
  don't leak anything; the real title is inside the ciphertext and appears after unlock.

## 2. `just encrypt <name>` (local only)

A small script, `encrypt.py`:

1. Read `private/<name>.html` as bytes. No parsing or rendering.
2. Read the password from `$PAGE_PASSWORD` or prompt with `getpass` (never a CLI argument —
   that lands in shell history). Prompt twice to catch typos.
3. Encrypt with AES-256-GCM, key = PBKDF2-SHA256(password, random 16-byte salt, 600k),
   random 12-byte IV. Write base64 fields to `content/locked/<name>.json`.
4. Warn if the HTML references a relative or root-relative `src`/`href` (`/…`, `./…`) —
   that asset would either 404 or be public.

Uses the `cryptography` package, added to the **dev** dependency group only — CI never
encrypts, so the build itself stays at three libraries.

## 3. Build: render the locked shell

In `build.py`, for each `content/locked/*.json`:

- Write `/p/<name>/index.html` from a new `templates/locked.html`. It is a minimal page of its
  own, not an extension of `base.html`: a password field, the embedded JSON, and ~40 lines of
  inline JS. Styled with a few lines of the site's CSS so the lock screen doesn't look broken.
- Unlock: WebCrypto `PBKDF2` → `AES-GCM` decrypt → replace the whole document with the
  decrypted HTML (`document.open(); document.write(html); document.close()`), so the FAQ's
  own `<head>`, styles and scripts take over exactly as if the file were opened directly.
  A wrong password fails GCM authentication, which gives a clean "wrong password" message
  for free.
- `<meta name="robots" content="noindex, nofollow">` in the shell.
- Excluded from the index, lists, `feed.xml` and `sitemap.xml`.
- **Two ways in, same page:** the password prompt is always there, and the URL fragment
  (`/p/party/#pw=correct-horse-battery`) fills it in automatically. If a `#pw=` is wrong
  (password since changed, mangled link), fall back to the prompt with "This link's password
  is out of date — enter the one from your invite", not a dead end. Fragments are never sent
  to the server. Clear it with `history.replaceState` before swapping the document so it
  doesn't linger in the address bar.
- Make the prompt phone-friendly: `autocapitalize="none"`, `autocorrect="off"`,
  `spellcheck="false"`, and trim + lowercase input before deriving the key (the passphrase
  is generated lowercase), so "Correct-horse " on an iPhone keyboard still works.
- Remember the password in `localStorage` after a successful unlock, so guests who scan once
  can reopen the page from their history on the day without the invite to hand. If the
  stored one fails (rotated), drop it and show the prompt.

`--strict` additions: each locked JSON has exactly the expected fields with valid base64;
iterations ≥ 600,000.

## 4. Guard rails

- Test: `private/` is matched by `.gitignore` (`git check-ignore private/x.html`).
- Test: no file under `private/` is tracked (`git ls-files private/` is empty).
- Pre-commit already runs `just check`, so those block an accidental `git add -f`.
- Test: build with a fixture page containing a marker string, and assert the marker appears
  nowhere in `_site/`.

## 5. Tests

- Unit (`just test`): encrypt → decrypt round-trip in Python; wrong password raises.
- Layout (`just test-layout`): the lock screen gets visited at all four widths like any other
  page. Add one test that encrypts a fixture HTML file with a known password, loads
  `/p/fixture/#pw=…` in Chromium, and asserts the fixture's `<title>` and a marker element
  rendered. This is what proves the Python and WebCrypto halves agree on the format.
- The site's layout rules (column width, font scaling) don't apply to the unlocked FAQ: it
  has its own design. Check it on a phone by hand.

## 6. Workflow once built

```
$EDITOR private/party.html   # or open it directly in a browser to preview
just encrypt party           # prompts for the passphrase
just dev                     # check /p/party/ unlocks locally
git add content/locked/party.json && git commit && git push
```

## 7. Sharing via QR code on the invite

Recommended: **QR code with `#pw=` baked in, and the passphrase also printed in words
underneath** ("Can't scan? Go to jhrystrom.github.io/p/party and enter `maple-otter-lantern`").

- Putting the password in the QR code doesn't make it less secure than printing it: either
  way, whoever holds the invite gets in, and the invite *is* the access token. Leaving the
  password out of the QR code only helps if you send it through a different channel (e.g. a
  group chat), and then every guest has to type it on a phone.
- It isn't fragile either, because of the prompt fallback in section 3. If you rotate the
  password, old QR codes open the prompt instead of breaking. The printed words cover
  scanners or in-app browsers that drop the fragment.
- The one way it's genuinely fragile is rotating the password after the invites go out. Pick
  the passphrase once, before printing, and treat it as fixed.
- Keep the QR code short and easy to scan: the short `/p/party/` URL plus a 4-word
  lowercase passphrase (about 51 bits from the EFF word list, enough given the slow key
  derivation). `just qr party` can generate the PNG locally (`segno` for the matrix, drawn in a rustic style with Pillow;
  dev group); it reads the password the same way `just encrypt` does, and the PNG goes to
  `private/` so it isn't committed.

## If this ever needs real access control

Per-guest access or revocation needs a server. Cloudflare Pages + Cloudflare Access (email
one-time codes, free tier) in front of the site would do it, but it means moving hosting off
GitHub Pages. Not worth it for one FAQ.
