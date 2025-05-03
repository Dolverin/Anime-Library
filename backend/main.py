from fastapi import FastAPI

# Import necessary components from our app
from backend.app import models
from backend.app.database import engine, Base
from backend.app.routers import animes, episodes

# Create database tables
# This should ideally be handled by migrations (e.g., Alembic) in production
# But for development, creating them here is convenient.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the anime router
app.include_router(animes.router)

# Include the episodes router
app.include_router(episodes.router)

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
                # Binäre Daten aus dem Base64-String extrahieren
                import base64
                image_data = base64.b64decode(data["solution"]["response"])
                
                # Content-Type aus den Headers extrahieren
                content_type = data["solution"]["headers"].get("content-type", "image/png")
                
                # Response mit dem Bild zurückgeben
                response.headers["Content-Type"] = content_type
                response.headers["Cache-Control"] = "max-age=86400"  # 1 Tag cachen
                return Response(content=image_data, media_type=content_type)
        
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
