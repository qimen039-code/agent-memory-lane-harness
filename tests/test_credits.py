from __future__ import annotations

import sys
from pathlib import Path

import pytest


if sys.version_info < (3, 11):
    pytest.skip("tomllib requires Python 3.11+", allow_module_level=True)

import tomllib  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


def test_credits_toml_is_machine_readable() -> None:
    payload = tomllib.loads((ROOT / "CREDITS.toml").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "credits/v1"
    assert payload["influence"]
    assert payload["pattern"]


@pytest.mark.parametrize("entry_type", ["influence", "pattern"])
def test_credit_entries_have_required_boundaries(entry_type: str) -> None:
    payload = tomllib.loads((ROOT / "CREDITS.toml").read_text(encoding="utf-8"))
    for entry in payload[entry_type]:
        assert entry["id"]
        assert entry["name"]
        assert entry["used_for"]
        assert entry["boundary"]


def test_public_influence_entries_have_urls_and_non_adoption_boundaries() -> None:
    payload = tomllib.loads((ROOT / "CREDITS.toml").read_text(encoding="utf-8"))
    for entry in payload["influence"]:
        assert entry["url"].startswith("https://github.com/")
        assert entry["source_type"] == "public_github"
        assert entry["not_adopted"]
        assert entry["docs_ref"] == "docs/influences-and-attribution.md"
