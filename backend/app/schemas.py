from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime, date
from .models import AnimeStatus, EpisodeStatus

# --- Episode Schemas ---

# Base schema for Episode data (common fields)
class EpisodeBase(BaseModel):
    episoden_nummer: int
    titel: Optional[str] = None
    status: EpisodeStatus = EpisodeStatus.missing
    air_date: Optional[date] = None
    anime_loads_episode_url: Optional[HttpUrl] = None

# Schema for creating a new Episode (requires anime_id)
class EpisodeCreate(EpisodeBase):
    anime_id: int

# Schema for updating an existing Episode (all fields optional)
class EpisodeUpdate(BaseModel):
    episoden_nummer: Optional[int] = None
    titel: Optional[str] = None
    status: Optional[EpisodeStatus] = None
    air_date: Optional[date] = None
    anime_loads_episode_url: Optional[HttpUrl] = None

# Schema for reading/returning Episode data (includes id and timestamps)
class Episode(EpisodeBase):
    id: int
    anime_id: int
    hinzugefuegt_am: datetime
    zuletzt_aktualisiert_am: datetime

    class Config:
        from_attributes = True # Use Pydantic V2 'from_attributes' instead of orm_mode

# --- Anime Schemas ---

# Base schema for Anime data (common fields)
class AnimeBase(BaseModel):
    titel: str
    status: AnimeStatus = AnimeStatus.plan_to_watch
    beschreibung: Optional[str] = None
    anime_loads_url: Optional[HttpUrl] = None
    cover_image_url: Optional[HttpUrl] = None

# Schema for creating a new Anime
class AnimeCreate(AnimeBase):
    pass

# Schema for updating an existing Anime (all fields optional)
class AnimeUpdate(BaseModel):
    titel: Optional[str] = None
    status: Optional[AnimeStatus] = None
    beschreibung: Optional[str] = None
    anime_loads_url: Optional[HttpUrl] = None
    cover_image_url: Optional[HttpUrl] = None

# Schema for reading/returning Anime data (includes id and timestamps)
# Excludes episodes list by default
class AnimeSimple(AnimeBase):
    id: int
    hinzugefuegt_am: datetime
    zuletzt_aktualisiert_am: datetime

    class Config:
        from_attributes = True

# Schema for reading/returning Anime data including its episodes
class Anime(AnimeSimple):
    episoden: List[Episode] = []

    class Config:
        from_attributes = True
