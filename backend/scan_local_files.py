#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import logging
import argparse
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# SQLAlchemy und Datenbankmodelle importieren
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Projekt-spezifische Importe
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.models import Anime, Episode, EpisodeAvailabilityStatus
from app.database import SessionLocal, get_db
from app import crud

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Verschiedene Regex-Patterns für das Parsen von Dateinamen
PATTERNS = [
    # Pattern 1: [Gruppe] Anime Name - Episode [Qualität].Erweiterung
    r'\[(?P<group>[^\]]+)\]\s*(?P<title>[^-]+)-\s*(?P<episode>\d+)(?:\s*v\d+)?\s*(?:\[(?P<quality>[^\]]+)\])?\..+',
    
    # Pattern 2: Anime Name - Episode.Erweiterung
    r'(?P<title>[^-]+)-\s*(?P<episode>\d+)(?:\s*v\d+)?\..+',
    
    # Pattern 3: Anime Name EpisodeErweiterung (ohne Trennzeichen)
    r'(?P<title>.*?)(?P<episode>\d{2,3})(?:v\d+)?\.(?P<ext>[a-zA-Z0-9]+)$',
    
    # Pattern 4: Anime.Name.S01E01.Info.Erweiterung (TV-Format mit Punkten)
    r'(?P<title>.*?)\.S\d+E(?P<episode>\d+)\..*?\.(?P<ext>[a-zA-Z0-9]+)$',
    
    # Pattern 5: Anime Name S01E01.Erweiterung (TV-Format mit Leerzeichen)
    r'(?P<title>.*?)\sS\d+E(?P<episode>\d+)\.(?P<ext>[a-zA-Z0-9]+)$',

    # Pattern 6: Anime Name/Season 01/EpisodeX.Erweiterung (Basierend auf Verzeichnisstruktur)
    r'.*?/(?P<title>.*?)/Season\s+\d+/.*?(?P<episode>\d+).*\.(?P<ext>[a-zA-Z0-9]+)$',
]

def parse_filename(filename: str) -> Optional[Dict[str, str]]:
    """
    Versucht, den Anime-Titel und die Episodennummer aus einem Dateinamen zu extrahieren.
    
    Args:
        filename: Der zu parsende Dateiname
        
    Returns:
        Ein Dictionary mit 'title' und 'episode', oder None, wenn das Parsing fehlschlägt
    """
    basename = os.path.basename(filename)
    
    # Versuche zuerst Pattern, die auf dem vollen Pfad basieren (für Verzeichnisstruktur-basiertes Matching)
    for pattern in [p for p in PATTERNS if '/' in p]:
        match = re.match(pattern, filename)
        if match:
            data = match.groupdict()
            # Titel bereinigen
            if 'title' in data:
                data['title'] = data['title'].strip().replace('.', ' ')
            # Episodennummer in Integer umwandeln
            if 'episode' in data:
                data['episode'] = int(data['episode'])
            logger.debug(f"Geparst mit Verzeichnispattern: {filename} -> {data}")
            return data
    
    # Dann versuche die restlichen Pattern mit dem Basisnamen
    for i, pattern in enumerate([p for p in PATTERNS if '/' not in p]):
        match = re.match(pattern, basename)
        if match:
            data = match.groupdict()
            # Titel bereinigen
            if 'title' in data:
                data['title'] = data['title'].strip().replace('.', ' ')
            # Episodennummer in Integer umwandeln
            if 'episode' in data:
                data['episode'] = int(data['episode'])
            logger.debug(f"Geparst mit Pattern {i+1}: {basename} -> {data}")
            return data
    
    # Für Dateien mit speziellem TV-Format, extrahiere manuell
    if re.search(r'S\d+E\d+', basename):
        # Extrahiere den Teil vor S01E01 als Titel
        title_match = re.match(r'(.*?)\.S\d+E\d+', basename)
        if title_match:
            title = title_match.group(1).replace('.', ' ')
            # Extrahiere die Episodennummer
            ep_match = re.search(r'S\d+E(\d+)', basename)
            if ep_match:
                episode = int(ep_match.group(1))
                logger.debug(f"Manuell geparst: {basename} -> Titel: {title}, Episode: {episode}")
                return {'title': title, 'episode': episode}
            
    logger.warning(f"Konnte Datei nicht parsen: {basename}")
    return None

def find_anime_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Findet alle Anime-Dateien im angegebenen Verzeichnis mit den angegebenen Erweiterungen.
    
    Args:
        directory: Das zu durchsuchende Verzeichnis
        extensions: Liste der zu suchenden Dateiendungen (ohne Punkt)
        
    Returns:
        Eine Liste von Pfaden zu Anime-Dateien
    """
    if extensions is None:
        extensions = ['mkv', 'mp4', 'avi']
        
    anime_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in extensions:
                anime_files.append(os.path.join(root, file))
                
    return anime_files

def find_matching_anime(db: Session, title: str) -> Optional[Anime]:
    """
    Sucht nach einem passenden Anime in der Datenbank.
    
    Args:
        db: Die Datenbankverbindung
        title: Der zu suchende Anime-Titel
        
    Returns:
        Das Anime-Objekt oder None, wenn kein passender Anime gefunden wurde
    """
    # Verschiedene Varianten der Suche probieren
    # 1. Exakte Übereinstimmung
    anime = db.query(Anime).filter(Anime.titel == title).first()
    if anime:
        return anime
        
    # 2. Teilstring-Suche
    anime = db.query(Anime).filter(Anime.titel.like(f"%{title}%")).first()
    if anime:
        return anime
        
    # 3. Ähnlichkeitssuche - vereinfachte Version
    # Entferne Sonderzeichen und nicht-alphanumerische Zeichen für den Vergleich
    simplified_title = re.sub(r'[^\w\s]', '', title).lower()
    
    all_anime = db.query(Anime).all()
    for a in all_anime:
        simplified_db_title = re.sub(r'[^\w\s]', '', a.titel).lower()
        # Wenn einer ein Teilstring des anderen ist, betrachten wir das als Match
        if simplified_title in simplified_db_title or simplified_db_title in simplified_title:
            return a
            
    return None

def update_episode_status(db: Session, anime: Anime, episode_number: int, file_path: str) -> None:
    """
    Aktualisiert den Status einer Episode in der Datenbank.
    
    Args:
        db: Die Datenbankverbindung
        anime: Das Anime-Objekt
        episode_number: Die Episodennummer
        file_path: Der Pfad zur lokalen Datei
    """
    episode = db.query(Episode).filter(
        Episode.anime_id == anime.id,
        Episode.episoden_nummer == episode_number
    ).first()
    
    if episode:
        # Aktualisiere den Status basierend auf dem aktuellen Status
        current_status = episode.availability_status
        
        if current_status == EpisodeAvailabilityStatus.AVAILABLE_ONLINE:
            # Episode ist online und lokal verfügbar
            new_status = EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE
        elif current_status == EpisodeAvailabilityStatus.NOT_AVAILABLE:
            # Episode ist nur lokal verfügbar
            new_status = EpisodeAvailabilityStatus.OWNED_LOCALLY
        elif current_status in [EpisodeAvailabilityStatus.OWNED_LOCALLY, EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE]:
            # Status bleibt unverändert, wenn Episode bereits als lokal markiert ist
            return
            
        episode.availability_status = new_status
        episode.local_path = file_path
        episode.zuletzt_aktualisiert_am = datetime.now()
        
        db.add(episode)
        logger.info(f"Episode {episode_number} von '{anime.titel}' auf Status {new_status} aktualisiert")
    else:
        # Episode existiert noch nicht in der Datenbank, erstelle sie
        new_episode = Episode(
            anime_id=anime.id,
            episoden_nummer=episode_number,
            titel=f"Episode {episode_number}",  # Standard-Titel
            local_path=file_path,
            availability_status=EpisodeAvailabilityStatus.OWNED_LOCALLY
        )
        db.add(new_episode)
        logger.info(f"Neue Episode {episode_number} für '{anime.titel}' erstellt (Lokal verfügbar)")

def scan_and_update(media_dir: str, db: Session) -> Tuple[int, int, int]:
    """
    Scannt das Medienverzeichnis und aktualisiert die Datenbank.
    
    Args:
        media_dir: Das zu scannende Verzeichnis
        db: Die Datenbankverbindung
        
    Returns:
        Tuple mit (gefundene Dateien, gefundene Animes, aktualisierte Episoden)
    """
    anime_files = find_anime_files(media_dir)
    logger.info(f"{len(anime_files)} Anime-Dateien gefunden in {media_dir}")
    
    matched_animes = set()
    updated_episodes = 0
    unmatched_files = []
    
    for file_path in anime_files:
        parsed_data = parse_filename(file_path)
        if not parsed_data:
            unmatched_files.append(file_path)
            continue
            
        title = parsed_data.get('title')
        episode = parsed_data.get('episode')
        
        if not title or not episode:
            unmatched_files.append(file_path)
            continue
            
        anime = find_matching_anime(db, title)
        if anime:
            update_episode_status(db, anime, episode, file_path)
            updated_episodes += 1
            matched_animes.add(anime.id)
        else:
            logger.warning(f"Kein passender Anime für '{title}' gefunden")
            unmatched_files.append(file_path)
    
    # Änderungen speichern
    db.commit()
    
    # Nicht geparste Dateien loggen
    if unmatched_files:
        logger.warning(f"{len(unmatched_files)} Dateien konnten nicht geparst oder keinem Anime zugeordnet werden:")
        for file in unmatched_files[:10]:  # Nur die ersten 10 anzeigen, um die Ausgabe übersichtlich zu halten
            logger.warning(f"  - {file}")
        if len(unmatched_files) > 10:
            logger.warning(f"  ... und {len(unmatched_files) - 10} weitere")
    
    return len(anime_files), len(matched_animes), updated_episodes

def main():
    parser = argparse.ArgumentParser(description='Scannt lokale Anime-Dateien und aktualisiert die Datenbank')
    parser.add_argument('--media-dir', type=str, default='/mnt/mediathek', help='Pfad zum Mediathek-Verzeichnis')
    parser.add_argument('--anime-subdir', type=str, default='Anime', help='Anime-Unterverzeichnis in der Mediathek')
    parser.add_argument('--include-movies', action='store_true', help='Filme-Verzeichnis ebenfalls scannen')
    args = parser.parse_args()
    
    media_dir = os.path.join(args.media_dir, args.anime_subdir)
    
    if not os.path.exists(media_dir):
        logger.error(f"Verzeichnis existiert nicht: {media_dir}")
        sys.exit(1)
    
    logger.info(f"Starte Scan von {media_dir}...")
    
    # Datenbankverbindung herstellen
    db = SessionLocal()
    try:
        files, animes, episodes = scan_and_update(media_dir, db)
        logger.info(f"Scan abgeschlossen: {files} Dateien gefunden, {animes} Animes gematcht, {episodes} Episoden aktualisiert")
        
        # Optionaler Scan des Film-Verzeichnisses
        if args.include_movies:
            movie_dir = os.path.join(args.media_dir, 'Anime Movie')
            if os.path.exists(movie_dir):
                logger.info(f"Starte Scan von {movie_dir}...")
                m_files, m_animes, m_episodes = scan_and_update(movie_dir, db)
                logger.info(f"Film-Scan abgeschlossen: {m_files} Dateien gefunden, {m_animes} Animes gematcht, {m_episodes} Episoden aktualisiert")
                
                # Gesamtergebnisse
                logger.info(f"Gesamtergebnis: {files + m_files} Dateien gefunden, {animes + m_animes} Animes gematcht, {episodes + m_episodes} Episoden aktualisiert")
            else:
                logger.warning(f"Film-Verzeichnis existiert nicht: {movie_dir}")
                
    except SQLAlchemyError as e:
        logger.error(f"Datenbankfehler: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
