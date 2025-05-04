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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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
    logger.debug(f"Versuche Datei zu parsen: {filename}")
    
    # Spezialfall: Extrahiere den Anime-Titel aus dem übergeordneten Verzeichnis
    # (für Dateien, die in einem Verzeichnis mit dem Anime-Namen liegen)
    try:
        # Versuche, den Anime-Namen aus dem Verzeichnisnamen zu extrahieren
        anime_dir = os.path.basename(os.path.dirname(os.path.dirname(filename)))
        logger.debug(f"Extrahierter Anime-Ordnername: {anime_dir}")
        
        if anime_dir and anime_dir != "Anime":
            # Versuche, die Episodennummer aus dem Dateinamen zu extrahieren
            # Für TV-Format (S01E01)
            ep_match = re.search(r'S\d+E(\d{1,3})', basename)
            if ep_match:
                episode = int(ep_match.group(1))
                logger.debug(f"Aus Verzeichnis geparst mit TV-Format: {filename} -> Titel: {anime_dir}, Episode: {episode}")
                return {'title': anime_dir, 'episode': episode}
            
            # Alternativ: Versuche einfach eine Zahl zu finden
            ep_match = re.search(r'[^0-9](\d{1,3})[^0-9]', basename)
            if ep_match:
                episode = int(ep_match.group(1))
                logger.debug(f"Aus Verzeichnis geparst mit Zahlenmuster: {filename} -> Titel: {anime_dir}, Episode: {episode}")
                return {'title': anime_dir, 'episode': episode}
    except Exception as e:
        logger.debug(f"Fehler beim Parsen des Verzeichnisnamens: {e}")
    
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
        logger.debug(f"Versuche Pattern {i+1}: {pattern} auf {basename}")
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

# Bekannte Titel-Mappings zwischen englischen/deutschen und japanischen Titeln
TITLE_MAPPINGS = {
    "a certain magical index": "toaru majutsu no index",
    "index die zauberin": "toaru majutsu no index",
    "to aru majutsu no index": "toaru majutsu no index",
    "a certain scientific railgun": "toaru kagaku no railgun",
    "railgun": "toaru kagaku no railgun",
    "to love ru": "to-love-ru trouble",
    "to love ru trouble": "to-love-ru trouble",
    "to love ru darkness": "to-love-ru trouble darkness",
    "to loveru": "to-love-ru trouble",
    "to loveru trouble": "to-love-ru trouble",
    "to loveru darkness": "to-love-ru trouble darkness",
}

def normalize_title(title: str) -> str:
    """
    Normalisiert einen Titel für den Vergleich (Kleinbuchstaben, keine Sonderzeichen).
    
    Args:
        title: Der zu normalisierende Titel
        
    Returns:
        Normalisierter Titel
    """
    if not title:
        return ""
    
    # Zu Kleinbuchstaben konvertieren und Sonderzeichen entfernen
    normalized = re.sub(r'[^\w\s]', '', title.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    logger.debug(f"Normalisierter Titel: '{title}' -> '{normalized}'")
    
    # Bekannte Titel-Mappings anwenden
    if normalized in TITLE_MAPPINGS:
        mapped = TITLE_MAPPINGS[normalized]
        logger.debug(f"Titel-Mapping angewendet: '{normalized}' -> '{mapped}'")
        return mapped
    
    # Zusätzlich: Versuche eine flexiblere Matching-Strategie für bestimmte Muster
    if 'to love' in normalized:
        logger.debug(f"'to love' gefunden in '{normalized}', versuche flexibles Matching")
        if 'darkness' in normalized:
            return "to-love-ru trouble darkness"
        else:
            return "to-love-ru trouble"
    
    return normalized

def find_matching_anime(db: Session, title: str) -> Optional[Anime]:
    """
    Sucht nach einem passenden Anime in der Datenbank.
    
    Args:
        db: Die Datenbankverbindung
        title: Der zu suchende Anime-Titel
        
    Returns:
        Das Anime-Objekt oder None, wenn kein passender Anime gefunden wurde
    """
    if not title:
        return None
    
    logger.debug(f"Suche nach Anime-Titel: '{title}'")
    
    # Normalisiere den Eingabetitel
    normalized_title = normalize_title(title)
    
    # Alle Anime aus der Datenbank abrufen für Debugging
    all_anime = db.query(Anime).all()
    logger.debug(f"Anzahl der Animes in der Datenbank: {len(all_anime)}")
    if len(all_anime) <= 30:  # Nur anzeigen, wenn nicht zu viele
        logger.debug(f"Anime-Titel in der Datenbank: {[a.titel for a in all_anime]}")
    
    # 1. Exakte Übereinstimmung mit normalisiertem Titel
    for a in all_anime:
        db_title_normalized = normalize_title(a.titel)
        logger.debug(f"Vergleiche: '{normalized_title}' mit '{db_title_normalized}' (Original: '{a.titel}')")
        
        if normalized_title == db_title_normalized:
            logger.info(f"Exakte Übereinstimmung gefunden: '{title}' -> '{a.titel}'")
            return a
    
    # 2. Teilstring-Suche mit normalisiertem Titel
    for a in all_anime:
        db_title_normalized = normalize_title(a.titel)
        if normalized_title in db_title_normalized or db_title_normalized in normalized_title:
            logger.info(f"Teilstring-Übereinstimmung gefunden: '{title}' -> '{a.titel}'")
            return a
    
    # 3. Suche in Synonymen (wenn vorhanden)
    for a in all_anime:
        if a.synonyme:
            synonyms = [s.strip() for s in a.synonyme.split(',')]
            logger.debug(f"Synonyme für '{a.titel}': {synonyms}")
            
            for synonym in synonyms:
                synonym_normalized = normalize_title(synonym)
                if normalized_title == synonym_normalized:
                    logger.info(f"Übereinstimmung in Synonymen gefunden: '{title}' -> '{a.titel}' (Synonym: '{synonym}')")
                    return a
    
    # 4. Spezial-Matching für bestimmte Titel (z.B. To Love Ru)
    for a in all_anime:
        # Für To Love Ru: Spezielle Logik anwenden
        if 'to love' in normalized_title.lower() and 'to love' in normalize_title(a.titel).lower():
            # Unterscheide zwischen Darkness und nicht-Darkness
            is_input_darkness = 'darkness' in normalized_title.lower()
            is_db_darkness = 'darkness' in normalize_title(a.titel).lower()
            
            if is_input_darkness == is_db_darkness:
                logger.info(f"Spezial-Matching für To Love Ru gefunden: '{title}' -> '{a.titel}'")
                return a
    
    # 5. Ähnlichkeitssuche für Verzeichnisnamen
    # Wenn der Titel direkt aus einem Verzeichnisnamen kommt, versuche eine flexiblere Suche
    if os.path.sep in title or title.count(' ') < 3:  # Wahrscheinlich ein Verzeichnisname
        for a in all_anime:
            # Prüfe auf Teilübereinstimmung in beide Richtungen mit kleineren Tokens
            db_title_tokens = set(normalize_title(a.titel).split())
            input_title_tokens = set(normalized_title.split())
            
            # Wenn mindestens 50% der Tokens übereinstimmen
            common_tokens = db_title_tokens.intersection(input_title_tokens)
            
            logger.debug(f"Token-Vergleich für '{title}' vs '{a.titel}': " +
                        f"Common: {common_tokens}, DB: {db_title_tokens}, Input: {input_title_tokens}")
            
            if common_tokens and (len(common_tokens) / len(db_title_tokens) > 0.5 or 
                                  len(common_tokens) / len(input_title_tokens) > 0.5):
                logger.info(f"Token-Übereinstimmung gefunden: '{title}' -> '{a.titel}'")
                return a
    
    logger.warning(f"Kein passender Anime für '{title}' gefunden")
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

def create_anime_from_parsed_data(db: Session, parsed_data: Dict[str, str], file_path: str) -> Optional[Anime]:
    """
    Erstellt einen neuen Anime-Eintrag basierend auf lokalen Dateiinformationen.
    
    Args:
        db: Datenbankverbindung
        parsed_data: Geparste Daten aus dem Dateinamen
        file_path: Pfad zur Datei
        
    Returns:
        Das erstellte Anime-Objekt oder None bei Fehler
    """
    try:
        # Grundlegende Informationen aus dem Dateinamen extrahieren
        title = parsed_data.get('title')
        episode_number = parsed_data.get('episode')
        
        if not title or not episode_number:
            logger.warning(f"Unvollständige Daten für Anime-Erstellung: {parsed_data}")
            return None
            
        # Folder-Pfad ermitteln
        folder_path = os.path.dirname(file_path)
        
        # Anime-Basisverzeichnis ermitteln (ein Verzeichnis höher, wenn es ein Season-Verzeichnis gibt)
        if 'season' in os.path.basename(folder_path).lower():
            anime_base_dir = os.path.dirname(folder_path)
        else:
            anime_base_dir = folder_path
            
        logger.info(f"Erstelle Anime aus lokaler Datei: {title}, Verzeichnis: {anime_base_dir}")
        
        # Neuen Anime erstellen
        anime = Anime(
            titel_de=title,
            imported_from_local=True,
            local_path=anime_base_dir,
            auto_update=True,
            status=AnimeStatus.owned,  # Neuer Status für lokale Animes
            hinzugefuegt_am=datetime.now(),
            last_scan_time=datetime.now()
        )
        
        db.add(anime)
        db.flush()  # ID generieren, ohne zu committen
        
        logger.info(f"Anime '{title}' mit ID {anime.id} erstellt")
        
        # Episode erstellen
        if episode_number:
            try:
                episode_number_int = int(episode_number)
                
                # Dateigröße ermitteln, wenn die Datei existiert
                file_size = None
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                
                # Versuche Auflösung und Codec aus dem Dateinamen zu extrahieren
                resolution = None
                codec = None
                audio_format = None
                
                # Einfache Regex-Muster für Metadaten
                resolution_match = re.search(r'(1080p|720p|480p|2160p|4K)', file_path)
                if resolution_match:
                    resolution = resolution_match.group(1)
                    
                codec_match = re.search(r'(x264|x265|h264|h265|AVC|HEVC)', file_path)
                if codec_match:
                    codec = codec_match.group(1)
                    
                audio_match = re.search(r'(AC3|DTS|AAC|FLAC|TrueHD)', file_path)
                if audio_match:
                    audio_format = audio_match.group(1)
                
                episode = Episode(
                    anime_id=anime.id,
                    episoden_nummer=episode_number_int,
                    local_path=file_path,
                    file_size=file_size,
                    resolution=resolution,
                    codec=codec,
                    audio_format=audio_format,
                    status=EpisodeStatus.owned,
                    availability_status=EpisodeAvailabilityStatus.OWNED_LOCALLY,
                    hinzugefuegt_am=datetime.now()
                )
                
                db.add(episode)
                logger.info(f"Episode {episode_number} für Anime '{title}' erstellt")
                
            except ValueError:
                logger.error(f"Episodennummer '{episode_number}' konnte nicht in Integer konvertiert werden")
        
        return anime
        
    except Exception as e:
        logger.exception(f"Fehler beim Erstellen des Animes aus lokaler Datei: {str(e)}")
        return None

def find_matching_anime_by_path(db: Session, path: str) -> Optional[Anime]:
    """
    Sucht nach einem Anime mit dem angegebenen lokalen Pfad.
    
    Args:
        db: Datenbankverbindung
        path: Lokaler Pfad des Animes
        
    Returns:
        Das Anime-Objekt oder None, wenn kein passender Anime gefunden wurde
    """
    try:
        return db.query(Anime).filter(Anime.local_path == path).first()
    except Exception as e:
        logger.error(f"Fehler bei der Suche nach Anime mit Pfad '{path}': {str(e)}")
        return None

def scan_and_update(media_dir: str, db: Session, create_missing: bool = True) -> Tuple[int, int, int]:
    """
    Scannt das Medienverzeichnis und aktualisiert die Datenbank.
    
    Args:
        media_dir: Das zu scannende Verzeichnis
        db: Die Datenbankverbindung
        create_missing: Wenn True, werden neue Animes erstellt, wenn keine Übereinstimmung gefunden wird
        
    Returns:
        Tuple mit (gefundene Dateien, gefundene/erstellte Animes, aktualisierte Episoden)
    """
    try:
        logger.info(f"Starte Scan von Verzeichnis: {media_dir}")
        anime_files = find_anime_files(media_dir)
        logger.info(f"{len(anime_files)} Anime-Dateien gefunden in {media_dir}")
        
        matched_animes = set()
        created_animes = 0
        updated_episodes = 0
        unmatched_files = []
        
        for file_path in anime_files:
            try:
                parsed_data = parse_filename(file_path)
                if not parsed_data:
                    unmatched_files.append(file_path)
                    continue
                    
                title = parsed_data.get('title')
                episode = parsed_data.get('episode')
                
                if not title or not episode:
                    unmatched_files.append(file_path)
                    continue
                    
                # Versuche zuerst die Datei einem Anime zuzuordnen
                anime = find_matching_anime(db, title)
                
                # Wenn kein Anime gefunden wurde und create_missing aktiviert ist
                if not anime and create_missing:
                    # Prüfe, ob wir bereits einen Anime für dieses Verzeichnis erstellt haben
                    folder_path = os.path.dirname(file_path)
                    anime_base_dir = folder_path
                    
                    # Anime-Basisverzeichnis ermitteln (ein Verzeichnis höher, wenn es ein Season-Verzeichnis gibt)
                    if 'season' in os.path.basename(folder_path).lower():
                        anime_base_dir = os.path.dirname(folder_path)
                    
                    # Suche nach einem Anime mit diesem Pfad
                    anime_by_path = find_matching_anime_by_path(db, anime_base_dir)
                    
                    if anime_by_path:
                        # Verwende den existierenden Anime mit diesem Pfad
                        anime = anime_by_path
                        logger.info(f"Anime mit Pfad '{anime_base_dir}' gefunden: {anime.titel_de}")
                    else:
                        # Erstelle einen neuen Anime
                        anime = create_anime_from_parsed_data(db, parsed_data, file_path)
                        if anime:
                            created_animes += 1
                            logger.info(f"Neuer Anime '{anime.titel_de}' erstellt aus Datei: {file_path}")
                
                if anime:
                    # Update der Episode
                    if not any(ep.episoden_nummer == int(episode) and ep.local_path == file_path for ep in anime.episodes):
                        update_episode_status(db, anime, int(episode), file_path)
                        updated_episodes += 1
                    
                    matched_animes.add(anime.id)
                else:
                    logger.warning(f"Kein passender Anime für '{title}' gefunden")
                    unmatched_files.append(file_path)
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung von Datei {file_path}: {str(e)}")
                # Fahre mit nächster Datei fort, anstatt den ganzen Prozess zu beenden
                continue
        
        # Änderungen speichern
        try:
            logger.info("Speichere Änderungen in der Datenbank")
            db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Datenbankfehler beim Speichern der Änderungen: {str(e)}")
            db.rollback()
            raise
        
        # Nicht geparste Dateien loggen
        if unmatched_files:
            logger.warning(f"{len(unmatched_files)} Dateien konnten nicht geparst oder keinem Anime zugeordnet werden:")
            for file in unmatched_files[:10]:  # Nur die ersten 10 anzeigen, um die Ausgabe übersichtlich zu halten
                logger.warning(f"  - {file}")
            if len(unmatched_files) > 10:
                logger.warning(f"  ... und {len(unmatched_files) - 10} weitere")
        
        total_animes = len(matched_animes)
        logger.info(f"Scan abgeschlossen: {len(anime_files)} Dateien gefunden, {total_animes} Animes ({created_animes} neu erstellt), {updated_episodes} Episoden aktualisiert")
        
        return len(anime_files), total_animes, updated_episodes
    except Exception as e:
        logger.exception(f"Unerwarteter Fehler beim Scannen von {media_dir}: {str(e)}")
        raise

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
