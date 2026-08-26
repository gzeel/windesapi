from pathlib import Path

from tests.extract_compose import extract


ROOT = Path(__file__).resolve().parent.parent


def test_student_compose_block_is_canonical():
    documented = extract(ROOT / "docs" / "STUDENTOPDRACHT.md")
    canonical = (ROOT / "compose.yaml").read_text(encoding="utf-8")

    assert documented == canonical


def test_student_document_has_no_repository_dependency():
    document = (ROOT / "docs" / "STUDENTOPDRACHT.md").read_text(encoding="utf-8")

    assert "cd labs/" not in document
    assert "zie de README" not in document.lower()
    assert "docker compose config --quiet" in document
    assert '127.0.0.1:${LAB_PORT:-8000}:8000' in document
