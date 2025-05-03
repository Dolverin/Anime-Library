#!/usr/bin/env python3
"""
Debug-Skript zum Testen des Bild-Downloads
"""
import os
import sys
import logging
import requests
import argparse
from pathlib import Path

# Damit wir das Skript vom Projektstamm ausführen können
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper.scraper import download_image

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion zum Testen des Bild-Downloads"""
    parser = argparse.ArgumentParser(description='Teste den Bild-Download')
    parser.add_argument('--url', default="https://www.anime-loads.org/files/image/w200-ore-dake-level-up-na-ken-how-to-get-stronger.png", 
                      help='URL zum Bild (Standard: Solo Leveling Bild)')
    parser.add_argument('--output', default="test_image.png", help='Ausgabedatei (Standard: test_image.png)')
    
    args = parser.parse_args()
    
    url = args.url
    output_file = args.output
    
    # Test mit direktem requests
    logger.info(f"Teste direkten Download mit requests von {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'de,en-US;q=0.9,en;q=0.8',
            'Referer': 'https://anime-loads.org/',
            'Origin': 'https://anime-loads.org',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            with open("direct_" + output_file, "wb") as f:
                f.write(response.content)
            logger.info(f"Direkter Download erfolgreich: {len(response.content)} Bytes")
        else:
            logger.error(f"Direkter Download fehlgeschlagen mit Status {response.status_code}")
    except Exception as e:
        logger.error(f"Fehler beim direkten Download: {str(e)}")
    
    # Test mit download_image Funktion
    logger.info(f"Teste download_image Funktion mit {url}")
    image_data = download_image(url)
    
    if image_data:
        with open(output_file, "wb") as f:
            f.write(image_data)
        logger.info(f"Download mit download_image erfolgreich: {len(image_data)} Bytes")
    else:
        logger.error("Download mit download_image fehlgeschlagen")

if __name__ == "__main__":
    main()
