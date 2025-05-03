#!/usr/bin/env python3
"""
Debug-Script zum Testen des Bild-Downloads
"""
import os
import sys
import logging
import requests
from pprint import pprint

# Damit wir das Skript vom Projektstamm ausführen können
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper.scraper import download_image

# Logger konfigurieren
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_image_download(url: str) -> None:
    """
    Testet den Download eines Bildes von einer URL
    
    Args:
        url: Die URL zum Bild
    """
    logger.info(f"Teste Bild-Download für URL: {url}")
    
    # 1. Test mit requests direkt
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Referer': 'https://www.anime-loads.org/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            logger.info(f"Direkter Download erfolgreich - Status: {response.status_code}, Content-Type: {response.headers.get('Content-Type')}, Größe: {len(response.content)} Bytes")
        else:
            logger.error(f"Direkter Download fehlgeschlagen - Status: {response.status_code}, Inhalt: {response.text[:100]}")
    except Exception as e:
        logger.error(f"Fehler beim direkten Download: {e}")
    
    # 2. Test mit unserer Download-Funktion
    try:
        image_data = download_image(url)
        if image_data:
            logger.info(f"Download mit unserer Funktion erfolgreich - Größe: {len(image_data)} Bytes")
        else:
            logger.error("Download mit unserer Funktion fehlgeschlagen - Keine Daten zurückgegeben")
    except Exception as e:
        logger.error(f"Fehler beim Download mit unserer Funktion: {e}")

if __name__ == "__main__":
    # Standardbeispiel-URL oder vom Benutzer bereitgestellte URL verwenden
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.anime-loads.org/files/media/cover/2060-ore-dake-level-up-na-ken.jpg"
    test_image_download(url)
