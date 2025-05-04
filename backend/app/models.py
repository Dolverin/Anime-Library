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
    owned = "owned"  # Neu: Lokal vorhanden
    owned_incomplete = "owned_incomplete"  # Neu: Lokal vorhanden, aber unvollständig

class EpisodeStatus(str, enum.Enum):
    missing = "missing"
    owned = "owned"
    watched = "watched"

class EpisodeAvailabilityStatus(str, enum.Enum):
    NOT_AVAILABLE = "not_available"              # Episode ist nirgendwo verfügbar
    AVAILABLE_ONLINE = "available_online"        # Episode ist online verfügbar (aber nicht lokal)
    OWNED_LOCALLY = "owned_locally"              # Episode ist lokal vorhanden (aber nicht online)
    OWNED_AND_AVAILABLE_ONLINE = "owned_and_available_online"  # Episode ist sowohl online als auch lokal verfügbar

class Anime(Base):
    __tablename__ = "animes"

    id = Column(Integer, primary_key=True, index=True)
    # Neue, eindeutige Titelspalten
    titel_de = Column(String(255), nullable=False)  # Deutscher Titel (Primärtitel)
    titel_jp = Column(String(255))  # Japanischer Titel (Romanisiert)
    titel_org = Column(String(255))  # Originaltitel (in originaler Schrift)
    titel_en = Column(String(255))  # Englischer Titel
    synonyme = Column(String(500))  # Sonstige alternative Titel
    
    # Neue Felder für lokale Dateien und automatisches Update
    imported_from_local = Column(Boolean, default=False)  # Ob der Anime von lokalen Dateien importiert wurde
    local_path = Column(String(500), nullable=True)  # Pfad zum lokalen Verzeichnis des Animes
    auto_update = Column(Boolean, default=True)  # Ob der Anime automatisch aktualisiert werden soll
    last_scan_time = Column(DateTime, nullable=True)  # Zeitpunkt des letzten Scans
    
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
    cover_local_path = Column(String(255), nullable=True)  # Pfad zum lokal gecachten Cover-Bild
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
    availability_status = Column(Enum(EpisodeAvailabilityStatus), nullable=False, default=EpisodeAvailabilityStatus.NOT_AVAILABLE)
    local_path = Column(String(512), nullable=True)  # Pfad zur lokalen Datei
    
    # Neue Felder für lokale Dateien
    file_size = Column(Integer, nullable=True)  # Größe der Datei in Bytes
    file_hash = Column(String(64), nullable=True)  # Hash der Datei (für Deduplizierung)
    resolution = Column(String(20), nullable=True)  # z.B. "1080p"
    codec = Column(String(20), nullable=True)  # z.B. "x265"
    audio_format = Column(String(20), nullable=True)  # z.B. "DTS"
    
    air_date = Column(Date, nullable=True)
    anime_loads_episode_url = Column(String(512), nullable=True)
    hinzugefuegt_am = Column(TIMESTAMP, server_default=func.now())
    zuletzt_aktualisiert_am = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    anime = relationship("Anime", back_populates="episodes")
