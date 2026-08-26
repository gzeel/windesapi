import sys
from pathlib import Path


START = "<!-- standalone-compose:start -->"
END = "<!-- standalone-compose:end -->"


def extract(document: Path) -> str:
    text = document.read_text(encoding="utf-8")
    section = text.split(START, 1)[1].split(END, 1)[0]
    fenced = section.split("```yaml", 1)[1].split("```", 1)[0]
    return fenced.strip() + "\n"


if __name__ == "__main__":
    source, destination = map(Path, sys.argv[1:3])
    destination.write_text(extract(source), encoding="utf-8")
