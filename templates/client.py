import os
import sys

import requests


BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.getenv("API_KEY")


def main() -> int:
    # TODO: voer een GET-request uit naar /api/v1/projects met timeout=5.
    # TODO: stuur API_KEY via X-API-Key als de API authenticatie vereist.
    # TODO: controleer de statuscode en verwerk JSON zonder op ontbrekende velden te crashen.
    # TODO: toon per project id, titel en status en handel request- en JSON-fouten af.
    raise NotImplementedError("Werk de TODO's uit volgens de studentopdracht.")


if __name__ == "__main__":
    sys.exit(main())
