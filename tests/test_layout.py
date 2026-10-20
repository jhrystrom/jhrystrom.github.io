"""Layout checks: render the built site in headless Chromium at several viewports.

Run with `just test-layout`. Full-page screenshots land in .layout-screenshots/ for a
once-over by eye; the assertions below are the part that decides pass/fail.
"""

from __future__ import annotations

import functools
import http.server
import re
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Page

import build

ROOT = Path(__file__).parent.parent
SCREENSHOTS = ROOT / ".layout-screenshots"

VIEWPORTS = {"phone": 375, "tablet": 768, "laptop": 1280, "desktop": 1920}
WIDE = ("laptop", "desktop")

# Pages that exercise the layout's distinct parts.
INDEX = "/"
PROSE = "/posts/2026/10/sovereignty-paradox/"
IMAGES = "/posts/2022/04/github-copilot-is-a-game-changer/"
NOTE = "/posts/2021/07/can-explainable-ai-be-automated/"

# Readable line length, in characters. Phones get a lower floor: the screen is the limit.
MIN_CHARS, MIN_CHARS_PHONE, MAX_CHARS = 45, 30, 85
# On a laptop or bigger, the text column should stop looking like a strip.
MIN_COLUMN = {"laptop": 640, "desktop": 740}
MIN_FONT = {"phone": 16, "tablet": 16, "laptop": 19, "desktop": 21}
MAX_FONT = 23
PHONE_GUTTER = (16, 24)
# Images may break out of the text column on wide screens, by at least this factor.
IMAGE_BREAKOUT = 1.2

# Width of the longest paragraph in main, and how many characters fit on one of its lines.
MEASURE_TEXT = """() => {
  const paragraphs = [...document.querySelectorAll('main p')];
  const p = paragraphs.reduce((a, b) => (b.textContent.length > a.textContent.length ? b : a));
  const probe = document.createElement('span');
  probe.style.font = getComputedStyle(p).font;
  probe.style.whiteSpace = 'nowrap';
  probe.textContent = p.textContent.slice(0, 500);
  document.body.append(probe);
  const charWidth = probe.getBoundingClientRect().width / probe.textContent.length;
  probe.remove();
  const rect = p.getBoundingClientRect();
  return {
    width: rect.width,
    left: rect.left,
    right: window.innerWidth - rect.right,
    chars: rect.width / charWidth,
  };
}"""


@pytest.fixture(scope="session")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("site")
    assert build.build(out, strict=False, future=False) == 0
    return out


@pytest.fixture(scope="session")
def site_url(site: Path) -> Iterator[str]:
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

    handler = functools.partial(QuietHandler, directory=site)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="session")
def all_paths(site: Path) -> list[str]:
    """Every HTML page in the sitemap, plus the talks list the sitemap leaves out."""
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    paths = [url.removeprefix(build.SITE_URL) for url in urls]
    return [p for p in paths if not p.endswith(".pdf")] + ["/talks/"]


@pytest.fixture(params=VIEWPORTS, ids=list(VIEWPORTS))
def viewport(request: pytest.FixtureRequest, page: Page) -> str:
    page.set_viewport_size({"width": VIEWPORTS[request.param], "height": 900})
    return request.param


def test_no_horizontal_scroll(
    page: Page, viewport: str, site_url: str, all_paths: list[str]
) -> None:
    overflowing = []
    for path in all_paths:
        page.goto(site_url + path)
        scroll = page.evaluate("document.documentElement.scrollWidth")
        if scroll > VIEWPORTS[viewport]:
            overflowing.append(f"{path} ({scroll}px)")
        name = path.strip("/").replace("/", "_") or "index"
        page.screenshot(path=SCREENSHOTS / viewport / f"{name}.png", full_page=True)
    assert not overflowing, f"pages wider than the {viewport} viewport: {overflowing}"


@pytest.mark.parametrize("path", [INDEX, PROSE, NOTE])
def test_line_length_is_readable(
    page: Page, viewport: str, site_url: str, path: str
) -> None:
    page.goto(site_url + path)
    chars = page.evaluate(MEASURE_TEXT)["chars"]
    floor = MIN_CHARS_PHONE if viewport == "phone" else MIN_CHARS
    assert floor <= chars <= MAX_CHARS, f"{chars:.0f} characters per line"


@pytest.mark.parametrize("path", [INDEX, PROSE])
def test_text_column_uses_wide_screens(
    page: Page, viewport: str, site_url: str, path: str
) -> None:
    if viewport not in WIDE:
        pytest.skip("only wide screens have room to spare")
    page.goto(site_url + path)
    width = page.evaluate(MEASURE_TEXT)["width"]
    assert width >= MIN_COLUMN[viewport], f"text column is {width:.0f}px wide"


def test_font_size_scales(page: Page, viewport: str, site_url: str) -> None:
    page.goto(site_url + PROSE)
    size = float(page.evaluate("parseFloat(getComputedStyle(document.body).fontSize)"))
    assert MIN_FONT[viewport] <= size <= MAX_FONT, f"body font is {size}px"


def test_phone_gutters(page: Page, viewport: str, site_url: str) -> None:
    if viewport != "phone":
        pytest.skip("gutters only matter on phones")
    page.goto(site_url + PROSE)
    text = page.evaluate(MEASURE_TEXT)
    low, high = PHONE_GUTTER
    assert low <= text["left"] <= high, f"left gutter is {text['left']:.0f}px"
    assert low <= text["right"] <= high, f"right gutter is {text['right']:.0f}px"


def test_images_break_out_on_wide_screens(
    page: Page, viewport: str, site_url: str
) -> None:
    if viewport not in WIDE:
        pytest.skip("narrow screens have no room for images to break out")
    page.goto(site_url + IMAGES)
    column = page.evaluate(MEASURE_TEXT)["width"]
    images = page.evaluate(
        "[...document.querySelectorAll('main img')]"
        ".map(i => ({src: i.src, width: i.getBoundingClientRect().width, natural: i.naturalWidth}))"
    )
    assert images, f"{IMAGES} has no images to check"
    for image in images:
        target = min(image["natural"], column * IMAGE_BREAKOUT)
        assert image["width"] >= target - 1, (
            f"{image['src']} is {image['width']:.0f}px, text column {column:.0f}px"
        )


def test_post_list_keeps_dates_next_to_titles(
    page: Page, viewport: str, site_url: str
) -> None:
    """A date sits beside its title, or directly above it on narrow screens."""
    page.goto(site_url + INDEX)
    gaps = page.evaluate(
        "[...document.querySelectorAll('ul.posts li')].map(li => {"
        "  const range = document.createRange();"
        "  range.selectNodeContents(li.querySelector('time'));"
        "  const date = range.getBoundingClientRect();"
        "  const title = li.querySelector('a').getBoundingClientRect();"
        "  return Math.max(0, title.top - date.bottom) / date.height;"
        "})"
    )
    assert max(gaps) < 1, f"title sits {max(gaps):.1f} date-heights below its date"


@pytest.mark.parametrize("path", [IMAGES, PROSE])
def test_images_and_captions_are_centred_on_the_text(
    page: Page, viewport: str, site_url: str, path: str
) -> None:
    page.goto(site_url + path)
    text = page.evaluate(MEASURE_TEXT)
    centre = text["left"] + text["width"] / 2
    figures = page.evaluate(
        "[...document.querySelectorAll('main p > img:first-child')].map(img => {"
        "  const box = img.getBoundingClientRect();"
        "  const caption = img.parentElement.querySelector('em');"
        "  return {"
        "    src: img.src, centre: box.left + box.width / 2, bottom: box.bottom,"
        "    caption: caption && caption.getBoundingClientRect().top,"
        "  };"
        "})"
    )
    assert figures, f"{path} has no images to check"
    for figure in figures:
        assert abs(figure["centre"] - centre) <= 2, f"{figure['src']} is off-centre"
        if figure["caption"] is not None:
            assert figure["caption"] >= figure["bottom"] - 1, (
                f"caption of {figure['src']} sits beside the image, not below"
            )
