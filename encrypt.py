"""Encrypt a standalone HTML page from private/ into content/locked/, or make its QR code.

    uv run encrypt.py party                  # private/party.html -> content/locked/party.json
    uv run encrypt.py party --new-password   # same, replacing the password it was locked with
    uv run encrypt.py party --qr             # private/party-qr.png, linking to /p/party/#pw=...

Re-encrypting keeps the existing password unless --new-password is given, so a typo can't
silently break the links and QR codes already sent out.

Runs locally only: CI never sees the plaintext or the password. The password comes from
$PAGE_PASSWORD or a prompt, never an argument, so it stays out of shell history.
templates/locked.html decrypts in the browser and must stay in step with this format.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import math
import os
import random
import re
import secrets
import sys
from pathlib import Path

import segno
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image, ImageDraw
from segno import consts

from build import LOCKED_DIR, MIN_ITERATIONS, ROOT, SITE_URL

PRIVATE_DIR = ROOT / "private"

# src/href attributes and CSS url()s, minus anything that doesn't touch this site.
REF_RE = re.compile(r"""(?:(?:src|href)=["']|url\(["']?)([^"')]+)""")
EXTERNAL_RE = re.compile(r"\A(?:[a-z][a-z0-9+.-]*:|//|#)", re.IGNORECASE)


class WrongPassword(Exception):
    pass


def normalize(password: str) -> str:
    """What a phone keyboard does to 'maple-otter' (capitals, spaces) shouldn't matter.

    templates/locked.html applies the same rule before deriving the key.
    """
    return re.sub(r"[\s-]+", "-", password.strip().lower())


def derive_key(password: str, salt: bytes, iterations: int) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations
    )
    return kdf.derive(normalize(password).encode())


def encrypt(plaintext: bytes, password: str) -> dict:
    salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    key = derive_key(password, salt, MIN_ITERATIONS)
    # AESGCM appends the 16-byte tag to the ciphertext, which is what WebCrypto expects.
    ciphertext = AESGCM(key).encrypt(iv, plaintext, None)
    return {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "iterations": MIN_ITERATIONS,
        "ciphertext": base64.b64encode(ciphertext).decode(),
    }


def decrypt(blob: dict, password: str) -> bytes:
    key = derive_key(password, base64.b64decode(blob["salt"]), blob["iterations"])
    try:
        return AESGCM(key).decrypt(
            base64.b64decode(blob["iv"]), base64.b64decode(blob["ciphertext"]), None
        )
    except InvalidTag:
        raise WrongPassword from None


def local_refs(html: str) -> list[str]:
    """Assets the page loads from this site: they'd 404, or be public if put in static/."""
    refs = (ref.strip() for ref in REF_RE.findall(html))
    return [ref for ref in refs if ref and not EXTERNAL_RE.match(ref)]


def lock(
    name: str, password: str, private: Path, locked: Path, new_password: bool = False
) -> list[str]:
    """Encrypt private/<name>.html. Returns any local asset references to warn about.

    Raises WrongPassword, leaving the page as it was, if it is already locked with a
    different password and new_password isn't set.
    """
    html = (private / f"{name}.html").read_bytes()
    existing = locked / f"{name}.json"
    if existing.exists() and not new_password:
        decrypt(json.loads(existing.read_text()), password)
    locked.mkdir(parents=True, exist_ok=True)
    blob = encrypt(html, password)
    (locked / f"{name}.json").write_text(json.dumps(blob, indent=2) + "\n")
    return local_refs(html.decode("utf-8", errors="replace"))


def share_link(name: str, password: str) -> str:
    return f"{SITE_URL}/p/{name}/#pw={normalize(password)}"


def qr(name: str, password: str, locked: Path, private: Path) -> Path:
    """Refuses a password that doesn't open the committed page, so a typo can't get printed."""
    blob = json.loads((locked / f"{name}.json").read_text())
    decrypt(blob, password)
    target = private / f"{name}-qr.png"
    render_rustic_qr(share_link(name, password), target)
    return target


# Black ink on a transparent background, so the code sits on whatever the invite is
# printed on. That background must be light: scanners need dark modules on light.
INK = (0, 0, 0, 255)
PAPER = (0, 0, 0, 0)
INK_WORN = (0, 0, 0, 165)  # worn spots: still well on the dark side over white


def _blob(cx, cy, radius, rng, squareness=2.0, wobble=0.05, points=72):
    """A hand-drawn-looking closed shape: a squircle (squareness 2 = circle) with a
    smooth, low-frequency wobble so the edge looks inked rather than plotted."""
    harmonics = [
        (k, rng.uniform(0, wobble / k), rng.uniform(0, 2 * math.pi)) for k in (2, 3, 5)
    ]
    shape = []
    for i in range(points):
        t = 2 * math.pi * i / points
        c, s = math.cos(t), math.sin(t)
        x = math.copysign(abs(c) ** (2 / squareness), c)
        y = math.copysign(abs(s) ** (2 / squareness), s)
        r = radius * (1 + sum(a * math.sin(k * t + p) for k, a, p in harmonics))
        shape.append((cx + r * x, cy + r * y))
    return shape


def render_rustic_qr(
    data: str,
    target: Path,
    module_px: int = 40,
    border: int = 4,
    joined: bool = True,
    grain: float = 0.5,
) -> None:
    """A QR code that looks stamped: black ink on transparent, wobbly rounded
    modules that run into their neighbours, soft squircle eyes and worn spots in the ink.

    Error correction is level H (30%), so the irregular look stays well inside what a
    scanner can recover from. The randomness is seeded by the data, so the same link
    always gives the same image.

    Tested against zbar and both OpenCV detectors at 250-2280px. Things that hurt
    scanning, so the defaults avoid them: separate dots (joined=False), flecks on the
    paper (detectors boost local contrast, so even faint flecks read as dark), heavy
    grain, and eyes rounder than squareness 10.
    """
    code = segno.make(data, error="h", boost_error=False)
    kinds = [list(row) for row in code.matrix_iter(scale=1, border=0, verbose=True)]
    n = len(kinds)
    rng = random.Random(data)
    ss = 3  # draw at 3x and downsample, for smooth edges
    m = module_px * ss
    size = (n + 2 * border) * m
    img = Image.new("RGBA", (size, size), PAPER)
    draw = ImageDraw.Draw(img)

    def centre(row, col):
        return (border + col + 0.5) * m, (border + row + 0.5) * m

    def eye(row, col, outer):
        """Concentric ink/paper/ink squircles centred on module (row, col)."""
        cx, cy = centre(row, col)
        for half, colour in (
            (outer / 2, INK),
            (outer / 2 - 1, PAPER),
            (outer / 2 - 2, INK),
        ):
            if half > 0:
                draw.polygon(_blob(cx, cy, half * m, rng, 10, 0.012), fill=colour)

    eyes = {(3, 3, 7), (3, n - 4, 7), (n - 4, 3, 7)}
    for row in range(1, n - 1):
        for col in range(1, n - 1):
            if (
                kinds[row][col] == consts.TYPE_ALIGNMENT_PATTERN_DARK
                and kinds[row - 1][col] == consts.TYPE_ALIGNMENT_PATTERN_LIGHT
                and kinds[row][col - 1] == consts.TYPE_ALIGNMENT_PATTERN_LIGHT
            ):
                eyes.add((row, col, 5))
    for row, col, outer in eyes:
        eye(row, col, outer)

    patterned = {consts.TYPE_FINDER_PATTERN_DARK, consts.TYPE_ALIGNMENT_PATTERN_DARK}

    def dark(row, col):
        # segno's dark module types are all >= 512, light ones < 256.
        return 0 <= row < n and 0 <= col < n and kinds[row][col] >= 256

    def data_dark(row, col):
        return dark(row, col) and kinds[row][col] not in patterned

    for row in range(n):
        for col in range(n):
            if not data_dark(row, col):
                continue
            cx, cy = centre(row, col)
            if joined:
                # Ink runs between touching modules, like a stamp pressed a bit hard.
                # Scanners see one dark run, as with a printed square QR code.
                h = rng.uniform(0.40, 0.45) * m
                if data_dark(row, col + 1):
                    draw.rectangle((cx, cy - h, cx + m, cy + h), fill=INK)
                if data_dark(row + 1, col):
                    draw.rectangle((cx - h, cy, cx + h, cy + m), fill=INK)
                if all(
                    data_dark(row + dr, col + dc) for dr, dc in ((0, 1), (1, 0), (1, 1))
                ):
                    draw.rectangle((cx, cy, cx + m, cy + m), fill=INK)
            else:
                cx += rng.uniform(-0.04, 0.04) * m
                cy += rng.uniform(-0.04, 0.04) * m
            radius = rng.uniform(0.40, 0.47) * m
            draw.polygon(_blob(cx, cy, radius, rng), fill=INK)

    # Grain: worn spots in the ink, so it reads as stamped rather than printed. They're
    # a muted ink, not paper, and only land on ink: a scanner looking closely at a print
    # must still see each dot as one dark module, not a dark module full of holes.
    for _ in range(int(grain * n * n * 2)):
        x, y = rng.uniform(0, size), rng.uniform(0, size)
        if img.getpixel((int(x), int(y))) != INK:
            continue
        r = rng.uniform(0.02, 0.06) * m
        draw.ellipse((x - r, y - r, x + r, y + r), fill=INK_WORN)

    final = img.resize((size // ss, size // ss), Image.Resampling.LANCZOS)
    final.save(target, dpi=(300, 300))


def read_password(confirm: bool, prompt: str = "Password: ") -> str:
    if password := os.environ.get("PAGE_PASSWORD"):
        return password
    password = getpass.getpass(prompt)
    if confirm and normalize(getpass.getpass("Again: ")) != normalize(password):
        sys.exit("passwords don't match")
    return password


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("name", help="private/<name>.html, served at /p/<name>/")
    parser.add_argument(
        "--qr", action="store_true", help="write private/<name>-qr.png instead"
    )
    parser.add_argument(
        "--new-password",
        action="store_true",
        help="replace the password; links and QR codes already sent out stop working",
    )
    args = parser.parse_args()

    if args.qr:
        try:
            target = qr(
                args.name, read_password(confirm=False), LOCKED_DIR, PRIVATE_DIR
            )
        except WrongPassword:
            print(f"that password doesn't open {args.name}", file=sys.stderr)
            return 1
        print(f"wrote {target.relative_to(ROOT)}")
        return 0

    source = PRIVATE_DIR / f"{args.name}.html"
    if not source.exists():
        print(f"{source.relative_to(ROOT)} not found", file=sys.stderr)
        return 1
    # An existing page checks the password itself; only a brand-new one needs typing twice.
    first_time = not (LOCKED_DIR / f"{args.name}.json").exists()
    if args.new_password:
        password = read_password(confirm=True, prompt="New password: ")
    else:
        password = read_password(confirm=first_time)
    try:
        refs = lock(args.name, password, PRIVATE_DIR, LOCKED_DIR, args.new_password)
    except WrongPassword:
        print(
            f"that isn't the password {args.name} is locked with; "
            "pass --new-password to change it (links and QR codes already sent out "
            "will stop working)",
            file=sys.stderr,
        )
        return 1
    for ref in refs:
        print(f"warning: {ref} is not inside the page; inline it", file=sys.stderr)
    print(f"wrote content/locked/{args.name}.json -> /p/{args.name}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
