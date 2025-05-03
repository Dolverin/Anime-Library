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
    titel_de: str  # Deutscher Titel (Primärtitel)
    titel_jp: Optional[str] = None  # Japanischer Titel (Romanisiert)
    titel_org: Optional[str] = None  # Originaltitel (in originaler Schrift)
    titel_en: Optional[str] = None  # Englischer Titel
    synonyme: Optional[str] = None  # Sonstige alternative Titel
    
    status: AnimeStatus = AnimeStatus.plan_to_watch
    beschreibung: Optional[str] = None
    anime_loads_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    typ: Optional[str] = None
    jahr: Optional[int] = None
    episoden_anzahl: Optional[str] = None
    laufzeit: Optional[str] = None
    hauptgenre: Optional[str] = None
    nebengenres: Optional[str] = None
    tags: Optional[str] = None
    anisearch_url: Optional[str] = None

# Schema for creating a new Anime
class AnimeCreate(AnimeBase):
    pass

# Schema for updating an existing Anime (all fields optional)
class AnimeUpdate(BaseModel):
    titel_de: Optional[str] = None
    titel_jp: Optional[str] = None
    titel_org: Optional[str] = None
    titel_en: Optional[str] = None
    synonyme: Optional[str] = None
    
    status: Optional[AnimeStatus] = None
    beschreibung: Optional[str] = None
    anime_loads_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    typ: Optional[str] = None
    jahr: Optional[int] = None
    episoden_anzahl: Optional[str] = None
    laufzeit: Optional[str] = None
    hauptgenre: Optional[str] = None
    nebengenres: Optional[str] = None
    tags: Optional[str] = None
    anisearch_url: Optional[str] = None

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

# Schema für Anime-Relationen
class AnimeRelationBase(BaseModel):
    source_anime_id: int
    target_anime_id: int
    relation_type: str

# Schema for creating a new Anime relation
class AnimeRelationCreate(AnimeRelationBase):
    pass

# Schema for reading/returning Anime relation data (includes id)
class AnimeRelation(AnimeRelationBase):
    id: int

    class Config:
        orm_mode = True

# Schema for reading/returning Anime data including its relations
class AnimeWithRelations(Anime):
    source_relations: List[AnimeRelation] = []
    target_relations: List[AnimeRelation] = []
