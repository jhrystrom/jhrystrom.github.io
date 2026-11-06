"""Password-protected pages: encryption, the locked shell, and keeping plaintext out of git."""

import base64
import json
import shutil
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


@pytest.fixture
def folders(tmp_path: Path) -> tuple[Path, Path]:
    """private/ and content/locked/, with party.html already encrypted once."""
    private, locked = tmp_path / "private", tmp_path / "locked"
    private.mkdir()
    (private / "party.html").write_text("<p>Old</p>")
    encrypt.lock("party", PASSWORD, private, locked)
    (private / "party.html").write_text("<p>New</p>")
    return private, locked


def test_re_encrypting_with_the_same_password_updates_the_page(folders) -> None:
    private, locked = folders

    encrypt.lock("party", "Maple Otter Lantern Quilt", private, locked)

    saved = json.loads((locked / "party.json").read_text())
    assert encrypt.decrypt(saved, PASSWORD) == b"<p>New</p>"


def test_re_encrypting_refuses_a_different_password(folders) -> None:
    """A typo, made twice, would otherwise break every printed QR code."""
    private, locked = folders
    before = (locked / "party.json").read_text()

    with pytest.raises(encrypt.WrongPassword):
        encrypt.lock("party", "maple-otter-lantern-quilts", private, locked)

    assert (locked / "party.json").read_text() == before


def test_new_password_replaces_the_old_one(folders) -> None:
    private, locked = folders

    encrypt.lock("party", "brand-new-pass-phrase", private, locked, new_password=True)

    saved = json.loads((locked / "party.json").read_text())
    assert encrypt.decrypt(saved, "brand-new-pass-phrase") == b"<p>New</p>"


@pytest.mark.parametrize(
    ("existing", "flags", "typed", "code", "prompts"),
    [
        # First time: no old password to check against, so confirm the new one.
        (False, [], [PASSWORD, PASSWORD], 0, ["Password: ", "Again: "]),
        (False, [], [PASSWORD, "typo"], "passwords don't match", 2),
        # Re-encrypting: the existing page is the check, so ask once.
        (True, [], [PASSWORD], 0, ["Password: "]),
        (True, [], ["wrong"], 1, ["Password: "]),
        (
            True,
            ["--new-password"],
            ["fresh", "fresh"],
            0,
            ["New password: ", "Again: "],
        ),
    ],
)
def test_cli_prompts(
    folders,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    existing: bool,
    flags: list[str],
    typed: list[str],
    code: int | str,
    prompts: list[str] | int,
) -> None:
    private, locked = folders
    if not existing:
        (locked / "party.json").unlink()
    asked: list[str] = []
    answers = iter(typed)

    def getpass(prompt: str) -> str:
        asked.append(prompt)
        return next(answers)

    monkeypatch.setattr(encrypt, "PRIVATE_DIR", private)
    monkeypatch.setattr(encrypt, "LOCKED_DIR", locked)
    monkeypatch.setattr(encrypt.getpass, "getpass", getpass)
    monkeypatch.delenv("PAGE_PASSWORD", raising=False)
    monkeypatch.setattr("sys.argv", ["encrypt.py", "party", *flags])

    if isinstance(code, str):
        with pytest.raises(SystemExit, match=code):
            encrypt.main()
    else:
        assert encrypt.main() == code
    assert asked == prompts if isinstance(prompts, list) else len(asked) == prompts
    if code == 1:
        assert "--new-password" in capsys.readouterr().err


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


@pytest.mark.skipif(
    shutil.which("zbarimg") is None, reason="needs zbar (brew install zbar)"
)
@pytest.mark.parametrize("width", [300, 600, 1200, None])
def test_rustic_qr_still_scans(tmp_path: Path, width: int | None) -> None:
    """The styling must never cost a guest a working link, at any print or photo size."""
    from PIL import Image

    link = encrypt.share_link("party", PASSWORD)
    target = tmp_path / "qr.png"
    encrypt.render_rustic_qr(link, target)
    qr = Image.open(target)
    assert qr.mode == "RGBA" and qr.getpixel((0, 0))[3] == 0  # transparent background
    # Printed on a light invite, as it will be; zbar may read transparent as black.
    page = Image.new("RGB", qr.size, "white")
    page.paste(qr, mask=qr)
    if width:
        page = page.resize((width, width), Image.Resampling.LANCZOS)
    page.save(target)

    decoded = subprocess.run(
        ["zbarimg", "-q", "--raw", str(target)],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    assert decoded == link


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
