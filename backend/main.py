from fastapi import FastAPI, Response, HTTPException, Depends
import logging
import requests
from urllib.parse import unquote
from app import models
from app.database import engine, Base, SessionLocal, get_db
from app.routers import animes, episodes
from app.scraper.scraper import download_image
import base64
from fastapi.responses import FileResponse
from app.utils.image import hash_url, download_or_proxy
import os
from app import crud
from fastapi.staticfiles import StaticFiles

# Logger konfigurieren (global)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create database tables
# This should ideally be handled by migrations (e.g., Alembic) in production
# But for development, creating them here is convenient.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the anime router
app.include_router(animes.router)

# Include the episodes router
app.include_router(episodes.router)

# Verzeichnis für gecachte Coverbilder
os.makedirs("static/covers", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Anime Library API"}

# Placeholder for future routes
# Example:
# from . import routes
# app.include_router(routes.router)

@app.get("/api/image-proxy")
async def image_proxy(url: str, response: Response):
    """
    Proxy für Bilder, die durch DDoS-Schutz geschützt sind.
    Verwendet FlareSolverr, um die Bilder zu holen.
    
    Args:
        url: Die URL des zu proxenden Bildes (URL-encoded)
    
    Returns:
        Das Bild als Binärdaten
    """
    try:
        # URL dekodieren
        decoded_url = unquote(url)
        logger.info(f"Proxying image from: {decoded_url}")
        
        # FlareSolverr verwenden, um das Bild zu holen
        flaresolverr_url = "http://localhost:8191/v1"
        payload = {
            "cmd": "request.get",
            "url": decoded_url,
            "maxTimeout": 60000,
            "responseType": "binary"
        }
        headers = {"Content-Type": "application/json"}
        
        flare_response = requests.post(flaresolverr_url, json=payload, headers=headers, timeout=60)
        
        if flare_response.status_code == 200:
            data = flare_response.json()
            if data.get("status") == "ok" and data.get("solution", {}).get("response"):
                try:
                    # Binäre Daten aus dem Base64-String extrahieren
                    base64_response = data["solution"]["response"]
                    image_data = base64.b64decode(base64_response)
                    
                    # Content-Type aus den Headers extrahieren
                    content_type = data["solution"]["headers"].get("content-type", "image/png")
                    
                    # Response mit dem Bild zurückgeben
                    response.headers["Content-Type"] = content_type
                    response.headers["Cache-Control"] = "max-age=86400"  # 1 Tag cachen
                    return Response(content=image_data, media_type=content_type)
                except (base64.binascii.Error, ValueError, TypeError) as e:
                    logger.error(f"Fehler beim Dekodieren der Base64-Antwort von FlareSolverr: {e}")
                    logger.debug(f"FlareSolverr response content type: {type(base64_response)}")
        
        # Fallback auf direkte Methode
        image_data = download_image(decoded_url)
        if image_data:
            # Content-Type aus dem Image bestimmen (vereinfacht)
            content_type = "image/png" if decoded_url.endswith(".png") else "image/jpeg"
            response.headers["Content-Type"] = content_type
            response.headers["Cache-Control"] = "max-age=86400"  # 1 Tag cachen
            return Response(content=image_data, media_type=content_type)
            
        # Wenn alles fehlschlägt, 404 zurückgeben
        raise HTTPException(status_code=404, detail="Bild konnte nicht gefunden werden")
    except Exception as e:
        logger.error(f"Fehler beim Proxen des Bildes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Interner Serverfehler: {str(e)}")

# Neue Route für Covers mit Caching
@app.get("/api/cover/{anime_id}")
def get_cover(anime_id: int, db=Depends(get_db)):
    anime = crud.get_anime(db, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime nicht gefunden")

    if not anime.cover_image_url:
        raise HTTPException(status_code=404, detail="Keine Cover-URL gespeichert")

    # Hash für Dateinamen
    filename_hash = hash_url(anime.cover_image_url)
    local_path = os.path.join("static", "covers", f"{filename_hash}.png")

    # Wenn Datei nicht existiert, herunterladen
    if not os.path.exists(local_path):
        data = download_or_proxy(anime.cover_image_url)
        if not data:
            raise HTTPException(status_code=502, detail="Cover konnte nicht geladen werden")
        with open(local_path, "wb") as f:
            f.write(data)
        # Pfad in DB speichern (optional)
        anime.cover_local_path = local_path
        db.commit()

    return FileResponse(local_path, media_type="image/png")
