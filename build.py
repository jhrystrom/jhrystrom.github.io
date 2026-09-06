"""Build jhrystrom.github.io.

Reads markdown from content/, renders it through templates/, writes a static site.
Also validates the content: run with --strict to turn warnings into failures.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).parent
SITE_URL = "https://jhrystrom.github.io"
SITE_TITLE = "Jonathan Rystrøm"
SITE_DESCRIPTION = "Research on evaluating AI agents for the public sector."
AUTHOR = "Jonathan Rystrøm"

LANG_NAMES = {"da": "Danish", "en": "English"}
DEFAULT_LANG = "en"

# Any front-matter key outside this set is an error. This is what catches `titel:`.
ALLOWED_KEYS = {
    "title",
    "date",
    "permalink",
    "lang",
    "translation_key",
    "original",
    "venue",
    "summary",
    "draft",
}
REQUIRED_KEYS = {"title", "date"}

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)
DATED_FILENAME_RE = re.compile(r"\A(\d{4})-(\d{2})-(\d{2})-(?P<slug>.+)\Z")
LOCAL_REF_RE = re.compile(r"""(?:href|src)=["'](/[^"'#?]*)""")


class Problems:
    """Collects file-anchored problems so the build can report all of them at once."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path: Path, message: str, line: int | None = None) -> None:
        self.errors.append(self._format(path, message, line))

    def warn(self, path: Path, message: str, line: int | None = None) -> None:
        self.warnings.append(self._format(path, message, line))

    @staticmethod
    def _format(path: Path, message: str, line: int | None) -> str:
        try:
            where = path.relative_to(ROOT)
        except ValueError:
            where = path
        return f"{where}:{line}: {message}" if line else f"{where}: {message}"


@dataclass
class Page:
    source: Path
    meta: dict
    body: str
    url: str
    kind: str  # "post" | "talk" | "index"
    html: str = ""
    translations: list[Page] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.meta["title"]

    @property
    def date(self) -> dt.date | None:
        return self.meta.get("date")

    @property
    def lang(self) -> str:
        return self.meta.get("lang", DEFAULT_LANG)

    @property
    def is_original(self) -> bool:
        """Listed in the feed unless the file explicitly opts out."""
        return self.meta.get("original") is not False

    @property
    def abs_url(self) -> str:
        return SITE_URL + self.url


def key_line(raw: str, key: str) -> int | None:
    """Line number of `key:` inside a file, for editor-jumpable error messages."""
    for number, line in enumerate(raw.splitlines(), start=1):
        if re.match(rf"\s*{re.escape(key)}\s*:", line):
            return number
    return None


def parse(path: Path, kind: str, problems: Problems) -> Page | None:
    raw = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(raw)
    if not match:
        problems.error(
            path, "no YAML front matter (file must start with a --- block)", 1
        )
        return None

    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        problems.error(path, f"front matter is not valid YAML: {exc}", 1)
        return None
    if not isinstance(meta, dict):
        problems.error(path, "front matter must be a mapping of key: value", 1)
        return None

    for key in sorted(set(meta) - ALLOWED_KEYS):
        allowed = ", ".join(sorted(ALLOWED_KEYS))
        problems.error(
            path,
            f"unknown front-matter key {key!r} (allowed: {allowed})",
            key_line(raw, key),
        )
    for key in sorted(REQUIRED_KEYS - set(meta)):
        problems.error(path, f"missing required front-matter key {key!r}", 1)

    if "date" in meta and not isinstance(meta["date"], dt.date):
        problems.error(
            path,
            f"date must be a plain YYYY-MM-DD date, got {meta['date']!r}",
            key_line(raw, "date"),
        )
    if isinstance(meta.get("date"), dt.datetime):
        meta["date"] = meta["date"].date()

    if "lang" in meta and meta["lang"] not in LANG_NAMES:
        known = ", ".join(sorted(LANG_NAMES))
        problems.error(
            path,
            f"unknown lang {meta['lang']!r} (known: {known})",
            key_line(raw, "lang"),
        )
    if "original" in meta and not isinstance(meta["original"], bool):
        problems.error(
            path, "original must be true or false", key_line(raw, "original")
        )
    if "translation_key" in meta and "lang" not in meta:
        problems.error(
            path, "translation_key requires lang", key_line(raw, "translation_key")
        )

    url = resolve_url(path, meta, kind, raw, problems)
    return Page(source=path, meta=meta, body=match.group(2), url=url, kind=kind)


def resolve_url(path: Path, meta: dict, kind: str, raw: str, problems: Problems) -> str:
    if kind == "index":
        return "/"

    if permalink := meta.get("permalink"):
        line = key_line(raw, "permalink")
        if not permalink.startswith("/"):
            problems.error(path, f"permalink must start with '/': {permalink!r}", line)
        if permalink != permalink.lower():
            problems.error(path, f"permalink must be lowercase: {permalink!r}", line)
        return permalink if permalink.endswith("/") else permalink + "/"

    stem = path.stem
    if kind == "post":
        if not (match := DATED_FILENAME_RE.match(stem)):
            problems.error(path, "post filename must be YYYY-MM-DD-slug.md", 1)
            return f"/posts/{stem}/"
        year, month, _, slug = match.groups()
        return f"/posts/{year}/{month}/{slug}/"

    slug = match.group("slug") if (match := DATED_FILENAME_RE.match(stem)) else stem
    return f"/talks/{slug}/"


def link_translations(pages: list[Page], problems: Problems) -> None:
    groups: dict[str, list[Page]] = {}
    for page in pages:
        if key := page.meta.get("translation_key"):
            groups.setdefault(key, []).append(page)

    for key, group in groups.items():
        first = group[0].source
        if len(group) < 2:
            problems.error(first, f"translation_key {key!r} has only one file")
            continue

        originals = [p for p in group if p.meta.get("original") is True]
        if len(originals) != 1:
            names = ", ".join(sorted(p.source.name for p in group))
            problems.error(
                first,
                f"translation_key {key!r} needs exactly one file with original: true, "
                f"found {len(originals)} across {names}",
            )

        by_lang: dict[str, Page] = {}
        for page in group:
            if clash := by_lang.get(page.lang):
                problems.error(
                    page.source,
                    f"translation_key {key!r} has two files with lang {page.lang!r} "
                    f"({clash.source.name} and {page.source.name})",
                )
            by_lang[page.lang] = page

        for page in group:
            page.translations = [other for other in group if other is not page]


def check_unique_urls(pages: list[Page], problems: Problems) -> None:
    seen: dict[str, Page] = {}
    for page in pages:
        if clash := seen.get(page.url):
            problems.error(
                page.source, f"URL {page.url} is already used by {clash.source.name}"
            )
        seen[page.url] = page


def check_internal_links(
    pages: list[Page], static_files: set[str], problems: Problems
) -> None:
    known = {page.url for page in pages} | static_files | {"/feed.xml", "/sitemap.xml"}
    for page in pages:
        for ref in sorted(set(LOCAL_REF_RE.findall(page.html))):
            candidates = {ref, ref.rstrip("/") + "/"}
            if not candidates & known:
                problems.error(page.source, f"internal link {ref} does not resolve")


def check_unused_images(
    static_dir: Path, pages: list[Page], templates: Path, problems: Problems
) -> None:
    """Flag images nothing links to. Templates count as references, not just content."""
    referenced = {ref for page in pages for ref in LOCAL_REF_RE.findall(page.html)}
    for template in sorted(templates.rglob("*")):
        if template.is_file():
            referenced |= set(
                LOCAL_REF_RE.findall(template.read_text(encoding="utf-8"))
            )
    for image in sorted((static_dir / "images").glob("*")):
        url = "/" + str(image.relative_to(static_dir))
        if url not in referenced:
            problems.warn(image, "image is not referenced by any page")


def date_filter(value: dt.date | None, fmt: str = "%b %-d, %Y") -> str:
    return value.strftime(fmt) if value else ""


def rfc3339(value: dt.date | None) -> str:
    if not value:
        return ""
    return dt.datetime.combine(value, dt.time(12, 0), tzinfo=dt.UTC).isoformat()


def report(problems: Problems, strict: bool) -> int | None:
    """Print collected problems. Returns 1 if the build should stop, else None."""
    if problems.errors or (strict and problems.warnings):
        for line in problems.errors + problems.warnings:
            print(line, file=sys.stderr)
        count = len(problems.errors) + (len(problems.warnings) if strict else 0)
        print(f"\n{count} problem(s); site not written.", file=sys.stderr)
        return 1
    for line in problems.warnings:
        print(f"warning: {line}", file=sys.stderr)
    return None


def build(out: Path, strict: bool) -> int:
    problems = Problems()
    content = ROOT / "content"
    static_dir = ROOT / "static"

    index = parse(content / "index.md", "index", problems)
    posts = [parse(p, "post", problems) for p in sorted(content.glob("posts/*.md"))]
    talks = [parse(p, "talk", problems) for p in sorted(content.glob("talks/*.md"))]

    def keep(candidates: list[Page | None]) -> list[Page]:
        return [p for p in candidates if p is not None and not p.meta.get("draft")]

    posts, talks = keep(posts), keep(talks)
    pages = keep([index]) + posts + talks

    link_translations(pages, problems)
    check_unique_urls(pages, problems)
    if (failed := report(problems, strict)) is not None:
        return failed

    md = markdown.Markdown(extensions=["extra", "smarty", "sane_lists"])
    for page in pages:
        md.reset()
        page.html = md.convert(page.body)

    posts.sort(key=lambda p: p.date or dt.date.min, reverse=True)
    talks.sort(key=lambda p: p.date or dt.date.min, reverse=True)
    listed = [p for p in posts if p.is_original]

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["date"] = date_filter
    env.filters["rfc3339"] = rfc3339

    static_files = {
        "/" + str(p.relative_to(static_dir))
        for p in static_dir.rglob("*")
        if p.is_file()
    }
    check_internal_links(pages, static_files, problems)
    check_unused_images(static_dir, pages, ROOT / "templates", problems)

    if (failed := report(problems, strict)) is not None:
        return failed

    shared = {
        "site_url": SITE_URL,
        "site_title": SITE_TITLE,
        "site_description": SITE_DESCRIPTION,
        "author": AUTHOR,
        "lang_names": LANG_NAMES,
        "default_lang": DEFAULT_LANG,
        "updated": max(
            (p.date for p in listed if p.date),
            default=dt.datetime.now(tz=dt.UTC).date(),
        ),
    }

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(static_dir, out)

    def write(url: str, text: str) -> None:
        target = (
            out / url.strip("/") / "index.html" if url != "/" else out / "index.html"
        )
        if url.endswith(".xml"):
            target = out / url.strip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    assert index is not None
    write(
        "/", env.get_template("index.html").render(page=index, posts=listed, **shared)
    )
    write("/talks/", env.get_template("list.html").render(pages=talks, **shared))
    for page in [*posts, *talks]:
        write(page.url, env.get_template("page.html").render(page=page, **shared))
    write("/feed.xml", env.get_template("feed.xml").render(posts=listed, **shared))
    write("/sitemap.xml", env.get_template("sitemap.xml").render(pages=pages, **shared))

    print(f"built {len(pages) + 1} pages into {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=ROOT / "_site", help="output directory"
    )
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )
    args = parser.parse_args()
    return build(args.out, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
