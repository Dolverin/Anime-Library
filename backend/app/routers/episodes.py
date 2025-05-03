from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/api/episodes",
    tags=["episodes"],
    responses={404: {"description": "Not found"}},
)

@router.post("/{anime_id}", response_model=schemas.Episode, status_code=status.HTTP_201_CREATED)
def create_episode_for_anime(anime_id: int, episode: schemas.EpisodeCreate, db: Session = Depends(get_db)):
    """Erstelle eine neue Episode für einen bestimmten Anime."""
    db_anime = crud.get_anime(db, anime_id=anime_id)
    if db_anime is None:
        raise HTTPException(status_code=404, detail="Anime nicht gefunden")
    
    # Prüfen, ob eine Episode mit dieser Nummer bereits existiert
    existing_episode = crud.get_episode_by_anime_id_and_number(
        db, anime_id=anime_id, episoden_nummer=episode.episoden_nummer
    )
    if existing_episode:
        raise HTTPException(
            status_code=400, 
            detail=f"Episode {episode.episoden_nummer} existiert bereits für Anime mit ID {anime_id}"
        )
    
    return crud.create_episode(db=db, episode=episode, anime_id=anime_id)

@router.get("/{anime_id}", response_model=List[schemas.Episode])
def read_episodes(anime_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Hole alle Episoden für einen bestimmten Anime."""
    db_anime = crud.get_anime(db, anime_id=anime_id)
    if db_anime is None:
        raise HTTPException(status_code=404, detail="Anime nicht gefunden")
    
    episodes = crud.get_episodes_for_anime(db, anime_id=anime_id, skip=skip, limit=limit)
    return episodes

@router.get("/{anime_id}/{episode_id}", response_model=schemas.Episode)
def read_episode(anime_id: int, episode_id: int, db: Session = Depends(get_db)):
    """Hole eine bestimmte Episode nach ID."""
    db_anime = crud.get_anime(db, anime_id=anime_id)
    if db_anime is None:
        raise HTTPException(status_code=404, detail="Anime nicht gefunden")
    
    db_episode = crud.get_episode(db, episode_id=episode_id)
    if db_episode is None or db_episode.anime_id != anime_id:
        raise HTTPException(status_code=404, detail="Episode nicht gefunden")
    
    return db_episode

@router.put("/{episode_id}", response_model=schemas.Episode)
def update_episode(episode_id: int, episode: schemas.EpisodeUpdate, db: Session = Depends(get_db)):
    """Aktualisiere eine Episode anhand ihrer ID."""
    db_episode = crud.get_episode(db, episode_id=episode_id)
    if db_episode is None:
        raise HTTPException(status_code=404, detail="Episode nicht gefunden")
    
    updated_episode = crud.update_episode(db, episode_id=episode_id, episode_update=episode)
    return updated_episode

@router.delete("/{episode_id}", response_model=schemas.Episode)
def delete_episode(episode_id: int, db: Session = Depends(get_db)):
    """Lösche eine Episode anhand ihrer ID."""
    db_episode = crud.get_episode(db, episode_id=episode_id)
    if db_episode is None:
        raise HTTPException(status_code=404, detail="Episode nicht gefunden")
    
    deleted_episode = crud.delete_episode(db, episode_id=episode_id)
    return deleted_episode
