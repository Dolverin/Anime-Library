from sqlalchemy import Column, Integer, String, Enum, Text, ForeignKey, TIMESTAMP, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

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
    titel = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(Enum(AnimeStatus), nullable=False, default=AnimeStatus.plan_to_watch)
    beschreibung = Column(Text, nullable=True)
    anime_loads_url = Column(String(512), nullable=True, unique=True)
    cover_image_url = Column(String(512), nullable=True)
    hinzugefuegt_am = Column(TIMESTAMP, server_default=func.now())
    zuletzt_aktualisiert_am = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    episoden = relationship("Episode", back_populates="anime")

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

    anime = relationship("Anime", back_populates="episoden")
