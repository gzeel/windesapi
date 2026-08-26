import json

import pytest

from app.settings import load_settings


@pytest.mark.parametrize(
    "contents",
    [
        {"require_api_key": "false"},
        {"unknown_measure": True},
        ["not", "an", "object"],
    ],
)
def test_invalid_settings_fail_clearly(tmp_path, contents):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(contents), encoding="utf-8")

    with pytest.raises(ValueError):
        load_settings(path)
