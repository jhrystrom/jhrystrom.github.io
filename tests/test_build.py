"""Generator rules can be checked directly, without HTTP or a browser."""

import datetime as dt
from pathlib import Path

import pytest

import build


def test_parse_post(tmp_path: Path) -> None:
    path = tmp_path / "2026-10-20-example.md"
    path.write_text("---\ntitle: Example\ndate: 2026-10-20\n---\nBody.\n")
    problems = build.Problems()

    page = build.parse(path, "post", problems)

    assert not problems.errors
    assert page is not None
    assert page.title == "Example"
    assert page.date == dt.date(2026, 10, 20)
    assert page.url == "/posts/2026/10/example/"
    assert page.body == "Body.\n"


@pytest.mark.parametrize(
    ("front_matter", "error"),
    [
        ("not front matter", "no YAML front matter"),
        ("---\n[broken\n---", "not valid YAML"),
        ("---\n- title\n---", "must be a mapping"),
        ("---\ndate: 2026-10-20\n---", "missing required front-matter key 'title'"),
        ("---\ntitle: Example\n---", "missing required front-matter key 'date'"),
        (
            "---\ntitle: Example\ndate: 2026-10-20\ntitel: Typo\n---",
            "unknown front-matter key 'titel'",
        ),
        (
            "---\ntitle: Example\ndate: '2026-10-20'\n---",
            "date must be a plain YYYY-MM-DD date",
        ),
        (
            "---\ntitle: Example\ndate: 2026-10-20\nlang: xx\n---",
            "unknown lang 'xx'",
        ),
        (
            "---\ntitle: Example\ndate: 2026-10-20\noriginal: 'true'\n---",
            "original must be true or false",
        ),
        (
            "---\ntitle: Example\ndate: 2026-10-20\ntranslation_key: pair\n---",
            "translation_key requires lang",
        ),
    ],
)
def test_invalid_front_matter(tmp_path: Path, front_matter: str, error: str) -> None:
    path = tmp_path / "2026-10-20-example.md"
    path.write_text(front_matter)
    problems = build.Problems()

    build.parse(path, "post", problems)

    assert any(error in message for message in problems.errors), problems.errors


@pytest.mark.parametrize(
    ("kind", "filename", "meta", "url"),
    [
        ("index", "index.md", {}, "/"),
        ("post", "2026-10-20-example.md", {}, "/posts/2026/10/example/"),
        ("post", "2026-10-20-example.md", {"permalink": "/pinned"}, "/pinned/"),
        ("talk", "2026-10-20-example.md", {}, "/talks/example/"),
        ("talk", "example.md", {}, "/talks/example/"),
    ],
)
def test_resolve_url(kind: str, filename: str, meta: dict, url: str) -> None:
    problems = build.Problems()

    assert build.resolve_url(Path(filename), meta, kind, "", problems) == url
    assert not problems.errors


def test_internal_links_allow_assets_and_url_fragments() -> None:
    page = build.Page(
        Path("example.md"),
        {},
        "",
        "/example/",
        "post",
        html='<a href="/example#heading">Self</a><img src="/images/photo.png?v=1">',
    )
    problems = build.Problems()

    build.check_internal_links([page], {"/images/photo.png"}, problems)
    assert not problems.errors

    page.html += '<a href="/missing/">Missing</a>'
    build.check_internal_links([page], {"/images/photo.png"}, problems)
    assert len(problems.errors) == 1
    assert "internal link /missing/ does not resolve" in problems.errors[0]


def test_translations_link_both_ways_and_require_one_original() -> None:
    original = build.Page(
        Path("da.md"),
        {"lang": "da", "translation_key": "pair", "original": True},
        "",
        "/da/",
        "post",
    )
    translation = build.Page(
        Path("en.md"),
        {"lang": "en", "translation_key": "pair", "original": False},
        "",
        "/en/",
        "post",
    )
    problems = build.Problems()

    build.link_translations([original, translation], problems)
    assert not problems.errors
    assert original.translations == [translation]
    assert translation.translations == [original]
    assert original.is_original
    assert not translation.is_original

    translation.meta["original"] = True
    build.link_translations([original, translation], problems)
    assert len(problems.errors) == 1
    assert "needs exactly one file with original: true" in problems.errors[0]
