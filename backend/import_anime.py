"""
CLI-Tool zum Importieren von Animes von anime-loads.org in die Datenbank.

Verwendung:
python import_anime.py https://www.anime-loads.org/media/anime-name

Dieses Skript scrapt einen Anime von anime-loads.org und fügt ihn in die Datenbank ein.
"""

import sys
import argparse
from sqlalchemy.orm import Session

# Backend-Pakete importieren
from backend.app import crud, schemas
from backend.app.database import SessionLocal
from backend.app.scraper import scrape_anime, scrape_episode_list

def import_anime(url: str, db: Session) -> None:
    """
    Importiert einen Anime von anime-loads.org in die Datenbank.
    
    Args:
        url: Die URL der Anime-Detailseite
        db: Datenbankverbindung
    """
    print(f"Starte Scraping für URL: {url}")
    
    # Anime-Daten scrapen
    anime_data = scrape_anime(url)
    if not anime_data:
        print("Fehler: Konnte keine Anime-Daten extrahieren.")
        return
    
    print(f"Anime gefunden: {anime_data.titel}")
    print(f"Beschreibung: {anime_data.beschreibung[:100]}..." if len(anime_data.beschreibung) > 100 else f"Beschreibung: {anime_data.beschreibung}")
    
    # Prüfe, ob Anime bereits existiert
    existing_anime = crud.get_anime_by_titel(db, titel=anime_data.titel)
    if existing_anime:
        print(f"Anime '{anime_data.titel}' existiert bereits in der Datenbank (ID: {existing_anime.id}).")
        anime_id = existing_anime.id
        # Hier könnte man ein Update implementieren
    else:
        # Anime in Datenbank speichern
        db_anime = crud.create_anime(db, anime=anime_data)
        print(f"Anime '{db_anime.titel}' wurde erfolgreich in die Datenbank eingefügt (ID: {db_anime.id}).")
        anime_id = db_anime.id
    
    # Episodenliste scrapen
    print("Scrape Episodenliste...")
    episodes_data = scrape_episode_list(url)
    if not episodes_data:
        print("Warnung: Keine Episoden gefunden oder Fehler beim Scrapen der Episodenliste.")
        return
    
    print(f"{len(episodes_data)} Episoden gefunden.")
    
    # Episoden in Datenbank speichern
    for episode_data in episodes_data:
        existing_episode = crud.get_episode_by_anime_id_and_number(
            db, 
            anime_id=anime_id, 
            episoden_nummer=episode_data.episoden_nummer
        )
        
        if existing_episode:
            print(f"Episode {episode_data.episoden_nummer} existiert bereits.")
            # Hier könnte man ein Update implementieren
        else:
            db_episode = crud.create_episode(db, episode=episode_data, anime_id=anime_id)
            print(f"Episode {db_episode.episoden_nummer}: '{db_episode.titel}' wurde erfolgreich hinzugefügt.")
    
    print("Import abgeschlossen!")

def main():
    # Command-Line-Parser
    parser = argparse.ArgumentParser(description="Importiere einen Anime von anime-loads.org in die Datenbank")
    parser.add_argument("url", help="URL der Anime-Detailseite auf anime-loads.org")
    args = parser.parse_args()
    
    # Datenbankverbindung öffnen
    db = SessionLocal()
    try:
        import_anime(args.url, db)
    except Exception as e:
        print(f"Fehler beim Import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
