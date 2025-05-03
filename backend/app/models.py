from sqlalchemy import Column, Integer, String, Enum, Text, ForeignKey, TIMESTAMP, Date, Boolean, LargeBinary, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from .database import Base

# Enum definitions for status fields
class AnimeStatus(str, enum.Enum):
    watching = "watching"
    completed = "completed"
    on_hold = "on_hold"
    dropped = "dropped"
    plan_to_watch = "plan_to_watch"

class EpisodeStatus(str, enum.Enum):
    missing = "missing"
    owned = "owned"
    watched = "watched"

class Anime(Base):
    __tablename__ = "animes"

    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String(255), nullable=False)
    original_titel = Column(String(255))
    synonyme = Column(String(500))
    beschreibung = Column(Text)
    status = Column(Enum(AnimeStatus), default=AnimeStatus.plan_to_watch)
    typ = Column(String(50))  # Serie, Film, OVA, etc.
    jahr = Column(Integer)
    episoden_anzahl = Column(String(50))  # z.B. "12/24" für laufende Serien
    laufzeit = Column(String(50))
    hauptgenre = Column(String(100))
    nebengenres = Column(String(255))
    tags = Column(String(500))
    anime_loads_url = Column(String(255), unique=True)
    anime_loads_id = Column(String(255), unique=True)
    anisearch_url = Column(String(255), nullable=True)
    cover_image_url = Column(String(255), nullable=True)
    cover_image_data = Column(LargeBinary(16777215), nullable=True)  # MEDIUMBLOB für größere Bilder (bis zu 16MB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    episodes = relationship("Episode", back_populates="anime", cascade="all, delete-orphan")
    # Relationen, bei denen dieser Anime das Quell-Anime ist
    source_relations = relationship("AnimeRelation", 
                                   foreign_keys="AnimeRelation.source_anime_id",
                                   back_populates="source_anime",
                                   cascade="all, delete-orphan")
    # Relationen, bei denen dieser Anime das Ziel-Anime ist
    target_relations = relationship("AnimeRelation", 
                                   foreign_keys="AnimeRelation.target_anime_id",
                                   back_populates="target_anime",
                                   cascade="all, delete-orphan")


class AnimeRelation(Base):
    """Modell für Beziehungen zwischen Animes (Fortsetzungen, Prequels, Spin-offs, etc.)"""
    __tablename__ = "anime_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    source_anime_id = Column(Integer, ForeignKey("animes.id"), nullable=False)
    target_anime_id = Column(Integer, ForeignKey("animes.id"), nullable=False)
    relation_type = Column(String(50), nullable=False)  # "sequel", "prequel", "spin-off", etc.
    
    # Beziehungen zu Anime-Objekten
    source_anime = relationship("Anime", foreign_keys=[source_anime_id], back_populates="source_relations")
    target_anime = relationship("Anime", foreign_keys=[target_anime_id], back_populates="target_relations")


class Episode(Base):
    __tablename__ = "episoden"

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, ForeignKey("animes.id"), nullable=False)
    episoden_nummer = Column(Integer, nullable=False)
    titel = Column(String(255), nullable=True)
    status = Column(Enum(EpisodeStatus), nullable=False, default=EpisodeStatus.missing)
    air_date = Column(Date, nullable=True)
    anime_loads_episode_url = Column(String(512), nullable=True)
    hinzugefuegt_am = Column(TIMESTAMP, server_default=func.now())
    zuletzt_aktualisiert_am = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    anime = relationship("Anime", back_populates="episodes")
