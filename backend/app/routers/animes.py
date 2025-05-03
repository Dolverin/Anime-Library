from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from .. import crud, models, schemas
from ..database import get_db
from ..scraper.scraper import search_anime, scrape_anime, scrape_episode_list

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

@router.get("/search-external", response_model=List[Dict])
def search_external_anime(query: str):
    """
    Sucht nach Animes auf anime-loads.org anhand eines Suchbegriffs.
    
    Args:
        query: Der Suchbegriff
        
    Returns:
        Liste von Anime-Ergebnissen mit Titel, URL und Bild
    """
    results = search_anime(query)
    return results or []

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

# Add routes for episodes later (e.g., POST /{anime_id}/episodes/)
