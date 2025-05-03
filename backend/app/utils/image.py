import os
import hashlib
import logging
import requests
import base64
from app.scraper.scraper import download_image

logger = logging.getLogger(__name__)
FLARESOLVERR_URL = "http://localhost:8191/v1"


def hash_url(url: str) -> str:
    """Erzeugt einen gekürzten SHA256-Hash für eine URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:32]


def download_or_proxy(url: str) -> bytes | None:
    """Versucht das Bild über verschiedene Methoden herunterzuladen."""
    # Direktversuch
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and r.content:
            return r.content
    except Exception:
        pass
    # FlareSolverr
    try:
        payload = {"cmd": "request.get", "url": url, "maxTimeout": 60000, "responseType": "binary"}
        r = requests.post(FLARESOLVERR_URL, json=payload, timeout=60)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "ok":
                return base64.b64decode(data["solution"]["response"])
    except Exception:
        pass
    # Fallback
    try:
        return download_image(url)
    except Exception as e:
        logger.error(f"download_image fehlgeschlagen: {e}")
    return None
