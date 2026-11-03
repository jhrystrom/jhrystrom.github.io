"""Shared build and test options; no browser is started by these fixtures."""

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

import build
import encrypt


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--layout-screenshots",
        action="store_true",
        help="Save every layout screenshot (by default only failures are captured).",
    )


@pytest.fixture(scope="session")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("site")
    assert build.build(out, strict=True, future=False) == 0
    return out


@dataclass
class LockedSite:
    out: Path
    password: str
    title: str
    marker: str


@pytest.fixture(scope="session")
def locked_site(tmp_path_factory: pytest.TempPathFactory) -> LockedSite:
    """The real site plus one locked page, so its shell is built like any other."""
    title, marker = "Fixture FAQ", "plaintext-marker-5f2c"
    html = (
        f"<!doctype html><html><head><title>{title}</title></head><body>"
        f'<p id="marker">{marker}</p>'
        "<script>document.body.dataset.ran = 'yes'</script></body></html>"
    )
    password = "maple-otter-lantern-quilt"
    locked = tmp_path_factory.mktemp("locked")
    (locked / "fixture.json").write_text(
        json.dumps(encrypt.encrypt(html.encode(), password))
    )
    out = tmp_path_factory.mktemp("locked-site")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(build, "LOCKED_DIR", locked)
        assert build.build(out, strict=True, future=False) == 0
    return LockedSite(out, password, title, marker)
