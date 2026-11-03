"""Password-protected pages: encryption, the locked shell, and keeping plaintext out of git."""

import base64
import json
import subprocess
from pathlib import Path

import pytest

import build
import encrypt

PASSWORD = "maple-otter-lantern-quilt"


@pytest.fixture(scope="module")
def blob() -> dict:
    return encrypt.encrypt(b"<p>Hello</p>", PASSWORD)


def test_round_trip(blob: dict) -> None:
    assert encrypt.decrypt(blob, PASSWORD) == b"<p>Hello</p>"


def test_wrong_password_raises(blob: dict) -> None:
    with pytest.raises(encrypt.WrongPassword):
        encrypt.decrypt(blob, "maple-otter-lantern-quilts")


def test_salt_and_iv_are_fresh_each_time(blob: dict) -> None:
    again = encrypt.encrypt(b"<p>Hello</p>", PASSWORD)
    for field in ("salt", "iv", "ciphertext"):
        assert again[field] != blob[field]


def test_blob_has_only_what_the_shell_reads(blob: dict) -> None:
    assert set(blob) == build.LOCKED_FIELDS
    assert blob["iterations"] == build.MIN_ITERATIONS
    assert len(base64.b64decode(blob["salt"])) == 16
    assert len(base64.b64decode(blob["iv"])) == 12


@pytest.mark.parametrize(
    "typed",
    [
        "Maple-Otter-Lantern-Quilt",
        "  maple otter lantern quilt ",
        "maple - otter  lantern-quilt",
    ],
)
def test_normalize_forgives_phone_keyboards(typed: str) -> None:
    assert encrypt.normalize(typed) == PASSWORD


def test_local_assets_are_flagged() -> None:
    html = (
        '<img src="/images/a.png"><img src="data:image/png;base64,AA">'
        '<a href="https://example.org">x</a><a href="#faq">f</a>'
        '<a href="mailto:me@example.org">m</a><link href="style.css">'
        "<div style=\"background: url('bg.jpg')\"></div>"
        '<link href="https://fonts.googleapis.com/css2?family=Inter">'
    )
    assert encrypt.local_refs(html) == ["/images/a.png", "style.css", "bg.jpg"]


def test_lock_writes_a_blob_that_opens_with_the_password(tmp_path: Path) -> None:
    private, locked = tmp_path / "private", tmp_path / "locked"
    private.mkdir()
    (private / "party.html").write_text('<img src="/a.png">')

    warnings = encrypt.lock("party", PASSWORD, private, locked)

    saved = json.loads((locked / "party.json").read_text())
    assert encrypt.decrypt(saved, PASSWORD) == b'<img src="/a.png">'
    assert warnings == ["/a.png"]


def test_share_link_carries_password_in_fragment() -> None:
    assert (
        encrypt.share_link("party", "Maple Otter Lantern Quilt")
        == "https://jhrystrom.github.io/p/party/#pw=maple-otter-lantern-quilt"
    )


def test_qr_refuses_a_password_that_does_not_open_the_page(
    tmp_path: Path, blob: dict
) -> None:
    (tmp_path / "party.json").write_text(json.dumps(blob))

    with pytest.raises(encrypt.WrongPassword):
        encrypt.qr("party", "wrong-password", tmp_path, tmp_path)
    assert not (tmp_path / "party-qr.png").exists()

    target = encrypt.qr("party", PASSWORD, tmp_path, tmp_path)
    assert target == tmp_path / "party-qr.png"
    assert target.read_bytes().startswith(b"\x89PNG")


def test_load_locked(tmp_path: Path, blob: dict) -> None:
    (tmp_path / "party.json").write_text(json.dumps(blob))
    problems = build.Problems()

    [page] = build.load_locked(tmp_path, problems)

    assert not problems.errors
    assert page.url == "/p/party/"
    assert page.blob == blob


def test_missing_locked_folder_is_fine(tmp_path: Path) -> None:
    problems = build.Problems()
    assert build.load_locked(tmp_path / "missing", problems) == []
    assert not problems.errors


@pytest.mark.parametrize(
    ("name", "change", "error"),
    [
        ("party", lambda b: b.pop("iv"), "fields must be exactly"),
        ("party", lambda b: b.update(title="Party"), "fields must be exactly"),
        ("party", lambda b: b.update(iterations=1000), "iterations must be at least"),
        (
            "party",
            lambda b: b.update(iterations="600000"),
            "iterations must be at least",
        ),
        ("party", lambda b: b.update(salt="not base64!"), "salt is not valid base64"),
        ("party", lambda b: b.update(iv="AAAA"), "iv must be 12 bytes"),
        ("Party", lambda b: None, "name must be lowercase letters, digits and -"),
    ],
)
def test_invalid_locked_blob(
    tmp_path: Path, blob: dict, name: str, change, error: str
) -> None:
    broken = dict(blob)
    change(broken)
    (tmp_path / f"{name}.json").write_text(json.dumps(broken))
    problems = build.Problems()

    build.load_locked(tmp_path, problems)

    assert any(error in message for message in problems.errors), problems.errors


def test_locked_file_that_is_not_json(tmp_path: Path) -> None:
    (tmp_path / "party.json").write_text("{nope")
    problems = build.Problems()

    assert build.load_locked(tmp_path, problems) == []
    assert any("not valid JSON" in message for message in problems.errors)


def test_locked_url_must_not_clash_with_a_page(tmp_path: Path, blob: dict) -> None:
    (tmp_path / "party.json").write_text(json.dumps(blob))
    problems = build.Problems()
    locked = build.load_locked(tmp_path, problems)
    page = build.Page(Path("pinned.md"), {}, "", "/p/party/", "post")

    build.check_unique_urls([page, *locked], problems)

    assert any("/p/party/ is already used" in message for message in problems.errors)


def test_shell_is_noindexed_and_unlisted(locked_site) -> None:
    shell = (locked_site.out / "p/fixture/index.html").read_text()

    assert '<meta name="robots" content="noindex, nofollow"' in shell
    assert "<title>Private page</title>" in shell
    for listing in ("index.html", "feed.xml", "sitemap.xml", "talks/index.html"):
        assert "/p/" not in (locked_site.out / listing).read_text(), listing


def test_plaintext_never_reaches_the_site(locked_site) -> None:
    for path in locked_site.out.rglob("*"):
        if path.is_file():
            data = path.read_bytes()
            assert locked_site.marker.encode() not in data, path
            assert locked_site.title.encode() not in data, path


def test_private_folder_is_gitignored() -> None:
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "private/party.html"],
        cwd=build.ROOT,
        check=False,
    )
    assert result.returncode == 0, "private/ must be in .gitignore"


def test_nothing_under_private_is_tracked() -> None:
    tracked = subprocess.run(
        ["git", "ls-files", "private/"],
        cwd=build.ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert tracked == "", f"plaintext is committed: {tracked}"
