from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import logging
import uuid

from .. import crud, models, schemas
from ..database import get_db
from ..scraper.scraper import search_anime, scrape_anime, scrape_episode_list

# Import der Scan-Funktionalität
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scan_local_files import scan_and_update

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/animes",
    tags=["animes"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.AnimeSimple, status_code=status.HTTP_201_CREATED)
def create_new_anime(anime: schemas.AnimeCreate, db: Session = Depends(get_db)):
    """Create a new anime entry."""
    db_anime = crud.get_anime_by_titel(db, titel=anime.titel)
    if db_anime:
        raise HTTPException(status_code=400, detail=f"Anime with title '{anime.titel}' already exists.")
    return crud.create_anime(db=db, anime=anime)

@router.get("/", response_model=List[schemas.AnimeSimple])
def read_all_animes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of all animes."""
    animes = crud.get_animes(db, skip=skip, limit=limit)
    return animes

@router.get("/search", response_model=List[schemas.AnimeSimple])
def search_animes(q: str, db: Session = Depends(get_db)):
    """
    Sucht nach Animes basierend auf einem Suchbegriff.
    
    Args:
        q: Der Suchbegriff
        
    Returns:
        Liste von Anime-Objekten, die dem Suchbegriff entsprechen
    """
    if not q:
        return []
    
    animes = crud.search_anime_by_any_titel(db, search_term=q)
    return animes

@router.get("/search-external", response_model=List[Dict])
def search_external_anime(query: str):
    """
    Sucht nach Animes auf anime-loads.org anhand eines Suchbegriffs.
    
    Args:
        query: Der Suchbegriff
        
    Returns:
        Liste von Anime-Ergebnissen mit Titel, URL und Bild
    """
    try:
        results = search_anime(query)
        # Konsolenausgabe für Debugging
        logger.info(f"Suchergebnisse für '{query}': {len(results)} gefunden")
        for result in results:
            # Stelle sicher, dass alle benötigten Felder vorhanden sind
            if 'id' not in result or not result['id']:
                # Generiere eine ID aus der URL, falls keine vorhanden
                url_parts = result.get('url', '').split('/')
                result['id'] = url_parts[-1] if len(url_parts) > 0 else str(uuid.uuid4())
            
            # Stelle sicher, dass title und url vorhanden sind
            if 'title' not in result or not result['title']:
                result['title'] = "Unbekannter Titel"
            
            if 'url' not in result or not result['url']:
                # Überspringe Ergebnisse ohne URL
                continue
                
        return results or []
    except Exception as e:
        logger.error(f"Fehler bei der externen Anime-Suche: {e}")
        return []

@router.get("/combined-search")
def combined_search(q: str, db: Session = Depends(get_db)):
    """
    Kombinierte Suche: Sucht zuerst in der Datenbank nach Animes und dann parallel auf anime-loads.org.
    
    Args:
        q: Der Suchbegriff
        
    Returns:
        Kombinierte Ergebnisse aus Datenbank und externer Suche mit Zeitstempelinformationen
    """
    if not q:
        return {"db_results": [], "external_results": []}
    
    # Zuerst in der eigenen Datenbank suchen
    db_animes = crud.search_anime_by_any_titel(db, search_term=q)
    
    # Ergebnisse mit Zeitstempelinformationen anreichern
    db_results = []
    for anime in db_animes:
        # Neuestes Update-Datum der Episoden ermitteln
        latest_episode_update = None
        if anime.episodes:
            latest_episode_update = max(episode.zuletzt_aktualisiert_am for episode in anime.episodes)
            
        db_results.append({
            "id": anime.id,
            "titel_de": anime.titel_de,
            "titel_jp": anime.titel_jp,
            "titel_en": anime.titel_en,
            "titel_org": anime.titel_org,
            "synonyme": anime.synonyme,
            "anime_loads_id": anime.anime_loads_id,
            "anime_loads_url": anime.anime_loads_url,
            "cover_image_url": anime.cover_image_url,
            "updated_at": anime.updated_at,
            "episodes_count": len(anime.episodes),
            "latest_episode_update": latest_episode_update
        })
    
    # Parallel auf anime-loads.org suchen
    external_results = search_anime(q) or []
    
    # Prüfen, welche externen Ergebnisse bereits in der Datenbank sind
    for ext_result in external_results:
        ext_id = ext_result.get("id")
        if ext_id:
            # Prüfen, ob dieser Anime bereits in der Datenbank existiert
            existing_anime = crud.get_anime_by_anime_loads_id(db, anime_loads_id=ext_id)
            if existing_anime:
                ext_result["in_database"] = True
                ext_result["db_id"] = existing_anime.id
                ext_result["updated_at"] = existing_anime.updated_at
            else:
                ext_result["in_database"] = False
    
    return {
        "db_results": db_results,
        "external_results": external_results
    }

@router.get("/scrape")
def scrape_anime_by_url(url: str):
    """
    Scrapt einen Anime von anime-loads.org anhand einer URL.
    
    Args:
        url: Die URL der Anime-Detailseite
        
    Returns:
        Anime-Informationen und Episodenliste
    """
    anime_data = scrape_anime(url)
    episodes_data = scrape_episode_list(url)
    
    if not anime_data:
        raise HTTPException(status_code=404, detail="Anime konnte nicht gefunden oder geparst werden.")
    
    return {
        "anime": anime_data,
        "episodes": episodes_data or []
    }

@router.post("/scan-local-files", response_model=Dict[str, int])
def scan_local_anime_files(media_dir: str = Body(...), db: Session = Depends(get_db)):
    """
    Scannt das angegebene Verzeichnis nach Anime-Dateien und aktualisiert die Datenbank.
    
    Args:
        media_dir: Das zu scannende Verzeichnis
        
    Returns:
        Dictionary mit Statistiken (gefundene Dateien, erkannte Animes, aktualisierte Episoden)
    """
    logger.info(f"Scan-Anfrage erhalten für Verzeichnis: {media_dir}")
    
    # Prüfen, ob das Verzeichnis existiert
    logger.info(f"Überprüfe ob Verzeichnis existiert: {media_dir}")
    if not os.path.exists(media_dir):
        err_msg = f"Verzeichnis '{media_dir}' existiert nicht."
        logger.error(err_msg)
        raise HTTPException(status_code=404, detail=err_msg)
    
    # Prüfen, ob es sich um ein Verzeichnis handelt
    logger.info(f"Überprüfe ob es sich um ein Verzeichnis handelt: {media_dir}")
    if not os.path.isdir(media_dir):
        err_msg = f"'{media_dir}' ist kein Verzeichnis."
        logger.error(err_msg)
        raise HTTPException(status_code=400, detail=err_msg)
    
    try:
        logger.info(f"Starte scan_and_update für Verzeichnis: {media_dir}")
        total_files, matched_animes, updated_episodes = scan_and_update(media_dir, db)
        logger.info(f"Scan abgeschlossen: {total_files} Dateien, {matched_animes} Animes, {updated_episodes} Episoden")
        return {
            "total_files": total_files,
            "matched_animes": matched_animes,
            "updated_episodes": updated_episodes
        }
    except Exception as e:
        logger.exception(f"Fehler beim Scannen von {media_dir}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Scannen: {str(e)}")

@router.post("/scan-and-create", response_model=Dict[str, int])
def scan_and_create_animes(media_dir_obj: Dict[str, str] = Body(...), db: Session = Depends(get_db)):
    """
    Scannt das angegebene Verzeichnis und erstellt neue Anime-Einträge für nicht zugeordnete Dateien.
    
    Args:
        media_dir_obj: Dictionary mit dem Schlüssel 'media_dir' und dem Pfad als Wert
        
    Returns:
        Dictionary mit Statistiken (gefundene Dateien, erstellte Animes, aktualisierte Episoden)
    """
    # Erhöhte Sichtbarkeit des vollständigen Request-Körpers
    logger.info(f"Empfangener Request-Body: {media_dir_obj}")
    
    # Extrahiere media_dir aus dem Dictionary
    if not isinstance(media_dir_obj, dict) or 'media_dir' not in media_dir_obj:
        logger.error(f"Fehlerhafter Request-Body: {media_dir_obj}")
        raise HTTPException(status_code=422, detail="'media_dir' wird im Request-Body erwartet")
    
    media_dir = media_dir_obj['media_dir']
    logger.info(f"Scan-and-Create-Anfrage für Verzeichnis: {media_dir}")
    
    # Prüfen, ob das Verzeichnis existiert
    logger.info(f"Überprüfe ob Verzeichnis existiert: {media_dir}")
    if not os.path.exists(media_dir):
        err_msg = f"Verzeichnis '{media_dir}' existiert nicht."
        logger.error(err_msg)
        raise HTTPException(status_code=404, detail=err_msg)
    
    # Prüfen, ob es sich um ein Verzeichnis handelt
    logger.info(f"Überprüfe ob es sich um ein Verzeichnis handelt: {media_dir}")
    if not os.path.isdir(media_dir):
        err_msg = f"'{media_dir}' ist kein Verzeichnis."
        logger.error(err_msg)
        raise HTTPException(status_code=400, detail=err_msg)
    
    try:
        # Aufruf der erweiterten Funktion mit create_missing=True
        logger.info(f"Führe scan_and_update mit create_missing=True für Verzeichnis aus: {media_dir}")
        
        # Detailliertes Debugging
        import traceback
        try:
            # Einfacher Test, ob wir überhaupt auf die Datenbank zugreifen können
            try:
                test_animes = db.query(models.Anime).limit(1).all()
                logger.info(f"Datenbankzugriff erfolgreich, gefundene Animes: {len(test_animes)}")
            except Exception as db_e:
                logger.error(f"Datenbankzugriff fehlgeschlagen: {str(db_e)}")
                raise HTTPException(status_code=500, detail=f"Datenbankzugriff fehlgeschlagen: {str(db_e)}")
                
            total_files, matched_animes, updated_episodes = scan_and_update(
                media_dir, db, create_missing=True
            )
            
            logger.info(f"Scan-and-Create abgeschlossen: {total_files} Dateien, {matched_animes} Animes, {updated_episodes} Episoden")
            
            # Zusätzliche Überprüfung, ob wir die Daten tatsächlich zurückgeben können
            result = {
                "total_files": total_files,
                "matched_animes": matched_animes, 
                "updated_episodes": updated_episodes
            }
            logger.info(f"Rückgabewerte: {result}")
            return result
            
        except Exception as inner_e:
            logger.error(f"Details der Exception: {str(inner_e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise inner_e
    except Exception as e:
        logger.exception(f"Fehler beim Scan-and-Create für {media_dir}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Scannen: {str(e)}")

@router.get("/{anime_id}", response_model=schemas.Anime)
def read_single_anime(anime_id: int, db: Session = Depends(get_db)):
    """Retrieve a single anime by its ID, including its episodes."""
    db_anime = crud.get_anime(db, anime_id=anime_id)
    if db_anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")
    # Note: This loads related episodes automatically due to the response_model and relationship
    return db_anime 

@router.put("/{anime_id}", response_model=schemas.AnimeSimple)
def update_existing_anime(anime_id: int, anime: schemas.AnimeUpdate, db: Session = Depends(get_db)):
    """Update an existing anime entry."""
    db_anime = crud.update_anime(db, anime_id=anime_id, anime_update=anime)
    if db_anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")
    return db_anime

@router.delete("/{anime_id}", response_model=schemas.AnimeSimple)
def delete_single_anime(anime_id: int, db: Session = Depends(get_db)):
    """Delete an anime entry."""
    db_anime = crud.delete_anime(db, anime_id=anime_id)
    if db_anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")
    return db_anime

# Add routes for episodes later (e.g., POST /{anime_id}/episodes/)
