#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test-Skript für den Import lokaler Anime-Dateien
"""

import os
import sys
import logging
from sqlalchemy.exc import SQLAlchemyError

# Projekt-Import-Pfad hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Eigene Module importieren
from app.database import SessionLocal
from scan_local_files import scan_and_update

# Logger konfigurieren
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_import(media_dir):
    """
    Testet den Import-Prozess für ein bestimmtes Verzeichnis.
    
    Args:
        media_dir: Das zu scannende Verzeichnis
    """
    logger.info(f"=== STARTE TEST-IMPORT FÜR: {media_dir} ===")
    
    # Verzeichnis überprüfen
    if not os.path.exists(media_dir):
        logger.error(f"Verzeichnis existiert nicht: {media_dir}")
        return
    
    if not os.path.isdir(media_dir):
        logger.error(f"Ist kein Verzeichnis: {media_dir}")
        return
    
    # Datenbankverbindung herstellen
    db = SessionLocal()
    
    try:
        # Import durchführen
        total_files, matched_animes, updated_episodes = scan_and_update(media_dir, db)
        
        # Ergebnisse ausgeben
        logger.info(f"=== IMPORT ERFOLGREICH ===")
        logger.info(f"Gefundene Dateien: {total_files}")
        logger.info(f"Zugeordnete Animes: {matched_animes}")
        logger.info(f"Aktualisierte Episoden: {updated_episodes}")
        
    except SQLAlchemyError as e:
        logger.error(f"Datenbankfehler: {str(e)}")
        db.rollback()
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Verbindung schließen
        db.close()
        logger.info("=== TEST-IMPORT BEENDET ===")

if __name__ == "__main__":
    # Verzeichnis als Argument oder Standardwert
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "/mnt/mediathek/Anime"
    test_import(target_dir)
