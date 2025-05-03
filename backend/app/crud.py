from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

# --- Anime CRUD --- 

def get_anime(db: Session, anime_id: int) -> Optional[models.Anime]:
    """Get a single anime by its ID."""
    return db.query(models.Anime).filter(models.Anime.id == anime_id).first()

def get_anime_by_titel(db: Session, titel: str) -> Optional[models.Anime]:
    """Get a single anime by its title."""
    return db.query(models.Anime).filter(models.Anime.titel == titel).first()

def get_animes(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Anime]:
    """Get a list of animes with pagination."""
    return db.query(models.Anime).offset(skip).limit(limit).all()

def create_anime(db: Session, anime: schemas.AnimeCreate) -> models.Anime:
    """Create a new anime in the database."""
    db_anime = models.Anime(
        titel=anime.titel,
        status=anime.status,
        beschreibung=anime.beschreibung,
        anime_loads_url=str(anime.anime_loads_url) if anime.anime_loads_url else None,
        cover_image_url=str(anime.cover_image_url) if anime.cover_image_url else None
    )
    db.add(db_anime)
    db.commit()
    db.refresh(db_anime)
    return db_anime

def update_anime(db: Session, anime_id: int, anime_update: schemas.AnimeUpdate) -> Optional[models.Anime]:
    """Update an existing anime."""
    db_anime = get_anime(db, anime_id=anime_id)
    if not db_anime:
        return None

    update_data = anime_update.model_dump(exclude_unset=True) # Use Pydantic V2 method

    for key, value in update_data.items():
        # Handle URL conversion if present
        if key in ['anime_loads_url', 'cover_image_url'] and value is not None:
            setattr(db_anime, key, str(value))
        else:
            setattr(db_anime, key, value)

    db.commit()
    db.refresh(db_anime)
    return db_anime

def delete_anime(db: Session, anime_id: int) -> Optional[models.Anime]:
    """Delete an anime from the database."""
    db_anime = get_anime(db, anime_id=anime_id)
    if db_anime:
        # Optional: Decide if you want to delete associated episodes too
        # for episode in db_anime.episoden:
        #     db.delete(episode)
        db.delete(db_anime)
        db.commit()
        return db_anime
    return None

# --- Episode CRUD --- 

def get_episode(db: Session, episode_id: int) -> Optional[models.Episode]:
    """Get a single episode by its ID."""
    return db.query(models.Episode).filter(models.Episode.id == episode_id).first()

def get_episode_by_anime_id_and_number(
    db: Session, anime_id: int, episoden_nummer: int
) -> Optional[models.Episode]:
    """Get a specific episode by anime ID and episode number."""
    return db.query(models.Episode).filter(
        models.Episode.anime_id == anime_id,
        models.Episode.episoden_nummer == episoden_nummer
    ).first()

def get_episodes_for_anime(db: Session, anime_id: int, skip: int = 0, limit: int = 1000) -> List[models.Episode]:
    """Get all episodes for a specific anime."""
    return db.query(models.Episode).filter(models.Episode.anime_id == anime_id).offset(skip).limit(limit).all()

def create_episode(db: Session, episode: schemas.EpisodeCreate, anime_id: int) -> models.Episode:
    """Create a new episode in the database."""
    db_episode = models.Episode(
        anime_id=anime_id,
        episoden_nummer=episode.episoden_nummer,
        titel=episode.titel,
        status=episode.status,
        air_date=episode.air_date,
        anime_loads_episode_url=str(episode.anime_loads_episode_url) if episode.anime_loads_episode_url else None
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode

def update_episode(
    db: Session, episode_id: int, episode_update: schemas.EpisodeUpdate
) -> Optional[models.Episode]:
    """Update an existing episode."""
    db_episode = get_episode(db, episode_id=episode_id)
    if not db_episode:
        return None

    update_data = episode_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        # Handle URL conversion if present
        if key == 'anime_loads_episode_url' and value is not None:
            setattr(db_episode, key, str(value))
        else:
            setattr(db_episode, key, value)

    db.commit()
    db.refresh(db_episode)
    return db_episode

def delete_episode(db: Session, episode_id: int) -> Optional[models.Episode]:
    """Delete an episode from the database."""
    db_episode = get_episode(db, episode_id=episode_id)
    if db_episode:
        db.delete(db_episode)
        db.commit()
        return db_episode
    return None
