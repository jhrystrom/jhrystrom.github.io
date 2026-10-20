"""Shared build and test options; no browser is started by these fixtures."""

from pathlib import Path

import pytest

import build


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
