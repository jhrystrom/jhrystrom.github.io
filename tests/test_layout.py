"""Layout checks: render the built site in headless Chromium at several viewports.

Run with `just test-layout`. Only failing pages are captured in .layout-screenshots/;
pass --layout-screenshots to capture every page for a once-over by eye.
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import shutil
import threading
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from conftest import LockedSite
from playwright.sync_api import Error, Page, expect

pytestmark = pytest.mark.layout

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


@contextlib.contextmanager
def serve(directory: Path) -> Iterator[str]:
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

    handler = functools.partial(QuietHandler, directory=directory)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.fixture(scope="session")
def site_url(site: Path) -> Iterator[str]:
    with serve(site) as url:
        yield url


@pytest.fixture(scope="session")
def locked_url(locked_site: LockedSite) -> Iterator[str]:
    with serve(locked_site.out) as url:
        yield url + "/p/fixture/"


@pytest.fixture(scope="session")
def all_paths(site: Path) -> list[str]:
    """Include unlisted static pages as well as generated posts and lists."""
    paths = [
        "/" + path.relative_to(site).as_posix().removesuffix("index.html")
        for path in sorted(site.rglob("index.html"))
    ]
    # Renaming a representative page must not silently remove its geometry checks.
    assert {INDEX, PROSE, NOTE, IMAGES} <= set(paths)
    return paths


@pytest.fixture(scope="session")
def screenshot_dir() -> Path:
    # A passing run should not leave stale failure evidence from a previous run.
    if SCREENSHOTS.exists():
        shutil.rmtree(SCREENSHOTS)
    return SCREENSHOTS


@pytest.fixture(params=VIEWPORTS, ids=list(VIEWPORTS))
def viewport(request: pytest.FixtureRequest, page: Page) -> str:
    page.set_viewport_size({"width": VIEWPORTS[request.param], "height": 900})
    return request.param


def test_layout(
    page: Page,
    viewport: str,
    site_url: str,
    all_paths: list[str],
    screenshot_dir: Path,
    subtests: pytest.Subtests,
    request: pytest.FixtureRequest,
) -> None:
    """Visit each page once per width; subtests report failures without ending the sweep.

    Geometry needs a real rendering engine. Keep checks for the same page together
    instead of creating another context and reloading its images for every assertion.
    """
    for path in all_paths:
        with subtests.test(path=path):
            failed = False
            try:
                # The load event waits for images whose dimensions affect layout.
                response = page.goto(site_url + path, wait_until="load")
                assert response is not None and response.ok, f"could not load {path}"
                scroll = page.evaluate("document.documentElement.scrollWidth")
                assert scroll <= VIEWPORTS[viewport], f"page is {scroll}px wide"

                if path in (INDEX, PROSE, NOTE, IMAGES):
                    text = page.evaluate(MEASURE_TEXT)
                    if path in (INDEX, PROSE, NOTE):
                        assert_line_length_is_readable(text, viewport)
                    if path in (INDEX, PROSE) and viewport in WIDE:
                        assert text["width"] >= MIN_COLUMN[viewport], (
                            f"text column is {text['width']:.0f}px wide"
                        )
                    if path == PROSE:
                        assert_font_size_scales(page, viewport)
                        if viewport == "phone":
                            assert_phone_gutters(text)
                    if path == INDEX:
                        assert_post_list_keeps_dates_next_to_titles(page)
                    if path == IMAGES and viewport in WIDE:
                        assert_images_break_out_on_wide_screens(page, text["width"])
                    if path in (IMAGES, PROSE):
                        assert_images_and_captions_are_centred_on_the_text(page, text)
            except Exception:
                failed = True
                raise
            finally:
                if failed or request.config.getoption("--layout-screenshots"):
                    name = path.strip("/").replace("/", "_") or "index"
                    try:
                        page.screenshot(
                            path=screenshot_dir / viewport / f"{name}.png",
                            full_page=True,
                        )
                    except Error as exc:
                        # Preserve the original error if navigation or Chromium failed.
                        warnings.warn(f"Could not capture {path}: {exc}", stacklevel=1)


def assert_line_length_is_readable(text: dict, viewport: str) -> None:
    chars = text["chars"]
    floor = MIN_CHARS_PHONE if viewport == "phone" else MIN_CHARS
    assert floor <= chars <= MAX_CHARS, f"{chars:.0f} characters per line"


def assert_font_size_scales(page: Page, viewport: str) -> None:
    size = float(page.evaluate("parseFloat(getComputedStyle(document.body).fontSize)"))
    assert MIN_FONT[viewport] <= size <= MAX_FONT, f"body font is {size}px"


def assert_phone_gutters(text: dict) -> None:
    low, high = PHONE_GUTTER
    assert low <= text["left"] <= high, f"left gutter is {text['left']:.0f}px"
    assert low <= text["right"] <= high, f"right gutter is {text['right']:.0f}px"


def assert_images_break_out_on_wide_screens(page: Page, column: float) -> None:
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


def assert_post_list_keeps_dates_next_to_titles(page: Page) -> None:
    """A date sits beside its title, or directly above it on narrow screens."""
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


def assert_images_and_captions_are_centred_on_the_text(page: Page, text: dict) -> None:
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
    assert figures, f"{page.url} has no images to check"
    for figure in figures:
        assert abs(figure["centre"] - centre) <= 2, f"{figure['src']} is off-centre"
        if figure["caption"] is not None:
            assert figure["caption"] >= figure["bottom"] - 1, (
                f"caption of {figure['src']} sits beside the image, not below"
            )


def test_locked_page_opens_from_link_and_remembers(
    page: Page, locked_site: LockedSite, locked_url: str
) -> None:
    """Python encrypts and WebCrypto decrypts: this is what proves the formats agree."""
    page.goto(f"{locked_url}#pw={locked_site.password}")
    expect(page).to_have_title(locked_site.title)
    expect(page.locator("#marker")).to_have_text(locked_site.marker)
    assert page.evaluate("document.body.dataset.ran") == "yes", "FAQ scripts must run"
    assert page.evaluate("location.hash") == "", "password lingers in the address bar"

    page.reload()
    expect(page).to_have_title(locked_site.title)


def test_locked_page_falls_back_to_the_prompt(
    page: Page, locked_site: LockedSite, locked_url: str
) -> None:
    page.set_viewport_size({"width": VIEWPORTS["phone"], "height": 900})
    page.goto(f"{locked_url}#pw=out-of-date-password")
    alert = page.get_by_role("alert")
    expect(alert).to_contain_text("out of date")
    expect(page).to_have_title("Private page")
    scroll = page.evaluate("document.documentElement.scrollWidth")
    assert scroll <= VIEWPORTS["phone"], f"lock screen is {scroll}px wide"

    password = page.get_by_label("Password")
    password.fill("not-the-password")
    password.press("Enter")
    expect(alert).to_contain_text("Wrong password")

    password.fill("  Maple Otter Lantern Quilt ")
    page.get_by_role("button", name="Open").click()
    expect(page.locator("#marker")).to_have_text(locked_site.marker)


def test_typing_during_the_automatic_check_is_not_lost(
    page: Page, locked_site: LockedSite, locked_url: str
) -> None:
    """Guests may start typing before a stale link's password has finished failing.

    A phone takes far longer over the key derivation than desktop Chromium (which runs it
    off the main thread, out of reach of CPU throttling), so delay it until the check is
    sure to fail partway through the typing.
    """
    page.add_init_script("""
      const deriveKey = crypto.subtle.deriveKey.bind(crypto.subtle);
      crypto.subtle.deriveKey = (...args) =>
        new Promise((resolve) => setTimeout(resolve, 300)).then(() => deriveKey(...args));
    """)
    page.goto(f"{locked_url}#pw=out-of-date-password")
    page.get_by_label("Password").click()
    page.keyboard.type("Maple Otter Lantern Quilt", delay=40)
    page.keyboard.press("Enter")
    expect(page.locator("#marker")).to_have_text(locked_site.marker)
