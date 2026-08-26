import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LabSettings:
    require_api_key: bool = False
    enforce_project_ownership: bool = False
    minimal_responses: bool = False
    validate_queries: bool = False
    safe_errors_headers_cors: bool = False
    rate_limit_and_log: bool = False

    @property
    def hardened(self) -> bool:
        return all(self.__dict__.values())


def load_settings(path: Path | None = None) -> LabSettings:
    settings_path = path or Path(os.environ.get("LAB_SETTINGS_PATH", "lab-settings.json"))
    if not settings_path.exists():
        return LabSettings()
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("lab-settings.json moet een JSON-object bevatten.")
    known = set(LabSettings().__dict__)
    unknown = set(data) - known
    if unknown:
        raise ValueError(f"Onbekende labinstellingen: {', '.join(sorted(unknown))}")
    invalid = [key for key, value in data.items() if not isinstance(value, bool)]
    if invalid:
        raise ValueError(f"Deze labinstellingen moeten true of false zijn: {', '.join(sorted(invalid))}")
    return LabSettings(**{key: data.get(key, False) for key in known})
