"""Every translation file says the same things as the English one."""

from __future__ import annotations

import json
import pathlib

import pytest

DIR = pathlib.Path(__file__).resolve().parent.parent / "custom_components/drivepulse/translations"
FILES = sorted(DIR.glob("*.json"))


def _paths(node, prefix=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _paths(value, f"{prefix}.{key}" if prefix else key)
    else:
        yield prefix, node


EN = dict(_paths(json.loads((DIR / "en.json").read_text(encoding="utf-8"))))


def test_the_ten_languages_of_the_app_are_there() -> None:
    assert {f.stem for f in FILES} == {
        "en", "it", "de", "fr", "es", "pt", "cs", "hu", "pl", "ro"
    }


@pytest.mark.parametrize("file", FILES, ids=lambda f: f.stem)
def test_same_keys_no_empty_text_same_placeholders(file: pathlib.Path) -> None:
    text = dict(_paths(json.loads(file.read_text(encoding="utf-8"))))
    assert set(text) == set(EN)
    for path, value in text.items():
        assert value.strip(), path
        assert ("{webhook_url}" in value) == ("{webhook_url}" in EN[path]), path
        assert "—" not in value, f"long dash in {path}"
