#!/usr/bin/env python3
"""
Import-Tool für Anime-Daten von anime-loads.org
"""
import os
import sys
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Damit wir das Skript vom Projektstamm ausführen können
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper.scraper import get_page_content, extract_anime_info, extract_episode_list
from app import crud, schemas, models
from app.database import get_db, SessionLocal

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def import_anime(url: str) -> Optional[models.Anime]:
    """
    Importiert einen Anime von anime-loads.org in die Datenbank.
    
    Args:
        url: Die URL zur Anime-Seite
        
    Returns:
        Das erstellte Anime-Modell oder None bei Fehler
    """
    logger.info(f"Starte Import von URL: {url}")
    
    # Hole den HTML-Inhalt
    soup = get_page_content(url)
    
    if not soup:
        logger.error(f"Konnte keine Verbindung zur Seite herstellen: {url}")
        return None
    
    # Extrahiere Anime-Informationen
    anime_data = extract_anime_info(soup, url)
    
    if not anime_data:
        logger.error("Konnte keine Anime-Informationen extrahieren")
        return None
    
    logger.info(f"Anime-Informationen extrahiert: {anime_data['title']}")
    
    # Erstelle ein AnimeCreate-Objekt
    try:
        anime_create = schemas.AnimeCreate(
            titel=anime_data.get('title', "Unbekannter Titel"),
            original_titel=anime_data.get('original_titel', ""),
            synonyme=anime_data.get('synonyme', ""),
            beschreibung=anime_data.get('beschreibung', ""),
            status=anime_data.get('status', models.AnimeStatus.plan_to_watch),
            typ=anime_data.get('typ', ""),
            jahr=anime_data.get('jahr'),
            episoden_anzahl=anime_data.get('episoden_anzahl', ""),
            laufzeit=anime_data.get('laufzeit', ""),
            hauptgenre=anime_data.get('hauptgenre', ""),
            nebengenres=anime_data.get('nebengenres', ""),
            tags=anime_data.get('tags', ""),
            anime_loads_url=anime_data.get('url', url),
            anime_loads_id=anime_data.get('anime_loads_id', ""),
            anisearch_url=anime_data.get('anisearch_url', ""),
            cover_image_url=anime_data.get('cover_image', "")
        )
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des AnimeCreate-Objekts: {e}")
        return None
    
    # Extrahiere Episoden
    episodes_data = extract_episode_list(soup)
    
    if not episodes_data:
        logger.warning("Keine Episoden gefunden, importiere nur Anime-Daten")
    else:
        logger.info(f"{len(episodes_data)} Episoden gefunden")
    
    # Verbindung zur Datenbank herstellen
    db = SessionLocal()
    
    try:
        # Prüfe, ob der Anime bereits existiert
        existing_anime = crud.get_anime_by_url(db, anime_data.get('url', url))
        
        if existing_anime:
            logger.info(f"Anime existiert bereits in der Datenbank (ID: {existing_anime.id}), aktualisiere...")
            
            # Aktualisiere den Anime
            anime_update = schemas.AnimeUpdate(
                titel=anime_create.titel,
                original_titel=anime_create.original_titel,
                synonyme=anime_create.synonyme,
                beschreibung=anime_create.beschreibung,
                status=anime_create.status,
                typ=anime_create.typ,
                jahr=anime_create.jahr,
                episoden_anzahl=anime_create.episoden_anzahl,
                laufzeit=anime_create.laufzeit,
                hauptgenre=anime_create.hauptgenre,
                nebengenres=anime_create.nebengenres,
                tags=anime_create.tags,
                anime_loads_url=anime_create.anime_loads_url,
                anisearch_url=anime_create.anisearch_url,
                cover_image_url=anime_create.cover_image_url
            )
            
            anime = crud.update_anime(db, existing_anime.id, anime_update)
        else:
            logger.info("Erstelle neuen Anime in der Datenbank...")
            anime = crud.create_anime(db, anime_create)
        
        # Cover-Bild-Daten speichern, falls vorhanden
        if anime_data.get('cover_image_data'):
            logger.info(f"Speichere Cover-Bild-Daten ({len(anime_data['cover_image_data'])} Bytes)")
            anime.cover_image_data = anime_data['cover_image_data']
            db.commit()
        
        # Importiere Episoden, falls vorhanden
        if episodes_data:
            for ep_data in episodes_data:
                # Prüfe, ob die Episode bereits existiert
                existing_episode = crud.get_episode_by_url(db, ep_data.get('anime_loads_episode_url', ''))
                
                if existing_episode:
                    logger.info(f"Episode {ep_data.get('number')} existiert bereits, überspringe...")
                    continue
                
                episode_create = schemas.EpisodeCreate(
                    episoden_nummer=ep_data.get('number', 0),
                    titel=ep_data.get('title', f"Episode {ep_data.get('number', 0)}"),
                    status="missing",
                    anime_loads_episode_url=ep_data.get('anime_loads_episode_url', None),
                    air_date=ep_data.get('air_date', None),
                    anime_id=anime.id
                )
                
                crud.create_episode(db, episode_create, anime.id)
                logger.info(f"Episode {ep_data.get('number')} erstellt")
        
        # Importiere Relationen, falls vorhanden
        if anime_data.get('relations'):
            logger.info(f"{len(anime_data['relations'])} Relationen gefunden")
            
            for relation in anime_data['relations']:
                relation_url = relation.get('url', '')
                relation_type = relation.get('type', 'related')
                
                if not relation_url:
                    continue
                
                # Prüfe, ob der verknüpfte Anime bereits in der Datenbank existiert
                target_anime = crud.get_anime_by_url(db, relation_url)
                
                if not target_anime:
                    logger.info(f"Relation-Anime nicht in Datenbank, versuche Import: {relation.get('title', '')}")
                    # Versuche, den verknüpften Anime zu importieren
                    target_anime = import_anime(relation_url)
                
                if target_anime:
                    # Prüfe, ob die Relation bereits existiert
                    existing_relation = db.query(models.AnimeRelation).filter(
                        models.AnimeRelation.source_anime_id == anime.id,
                        models.AnimeRelation.target_anime_id == target_anime.id
                    ).first()
                    
                    if existing_relation:
                        logger.info(f"Relation existiert bereits, überspringe...")
                        continue
                    
                    # Erstelle neue Relation
                    relation_create = schemas.AnimeRelationCreate(
                        source_anime_id=anime.id,
                        target_anime_id=target_anime.id,
                        relation_type=relation_type
                    )
                    
                    db.add(models.AnimeRelation(**relation_create.dict()))
                    db.commit()
                    logger.info(f"Relation erstellt: {anime.titel} -> {target_anime.titel} ({relation_type})")
        
        logger.info(f"Import erfolgreich abgeschlossen für: {anime.titel}")
        return anime
        
    except Exception as e:
        logger.error(f"Fehler beim Import des Anime: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def main():
    """Hauptfunktion für das Import-Tool"""
    parser = argparse.ArgumentParser(description='Importiere Anime-Daten von anime-loads.org')
    parser.add_argument('url', help='URL zur Anime-Seite auf anime-loads.org')
    
    args = parser.parse_args()
    
    result = import_anime(args.url)
    
    if result:
        print(f"Import erfolgreich: {result.titel}")
        sys.exit(0)
    else:
        print("Import fehlgeschlagen!")
        sys.exit(1)

if __name__ == "__main__":
    main()
