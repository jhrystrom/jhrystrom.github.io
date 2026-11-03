"""Encrypt a standalone HTML page from private/ into content/locked/, or make its QR code.

    uv run encrypt.py party        # private/party.html -> content/locked/party.json
    uv run encrypt.py party --qr   # private/party-qr.png, linking to /p/party/#pw=...

Runs locally only: CI never sees the plaintext or the password. The password comes from
$PAGE_PASSWORD or a prompt, never an argument, so it stays out of shell history.
templates/locked.html decrypts in the browser and must stay in step with this format.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
import re
import secrets
import sys
from pathlib import Path

import segno
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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


def lock(name: str, password: str, private: Path, locked: Path) -> list[str]:
    """Encrypt private/<name>.html. Returns any local asset references to warn about."""
    html = (private / f"{name}.html").read_bytes()
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
    segno.make(share_link(name, password), error="m").save(target, scale=10, border=4)
    return target


def read_password(confirm: bool) -> str:
    if password := os.environ.get("PAGE_PASSWORD"):
        return password
    password = getpass.getpass("Password: ")
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
    for ref in lock(args.name, read_password(confirm=True), PRIVATE_DIR, LOCKED_DIR):
        print(f"warning: {ref} is not inside the page; inline it", file=sys.stderr)
    print(f"wrote content/locked/{args.name}.json -> /p/{args.name}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
