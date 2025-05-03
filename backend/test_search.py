#!/usr/bin/env python3
"""
Test-Skript für die Anime-Suche auf anime-loads.org
"""
import sys
import logging
from app.scraper.scraper import search_anime

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion für den Test der Anime-Suche."""
    query = "solo" if len(sys.argv) < 2 else sys.argv[1]
    
    logger.info(f"Starte Suche nach: {query}")
    results = search_anime(query)
    
    if not results:
        logger.info(f"Keine Anime für '{query}' gefunden.")
        return
    
    print(f"\n{'=' * 50}")
    print(f"SUCHERGEBNISSE FÜR: {query}")
    print(f"{'=' * 50}")
    
    for i, anime in enumerate(results, 1):
        print(f"\n{i}. {anime['title']}")
        print(f"   URL: {anime['url']}")
        if anime.get('image_url'):
            print(f"   Bild: {anime['image_url']}")
    
    print(f"\n{'=' * 50}")
    print(f"Insgesamt {len(results)} Ergebnisse gefunden.")
    print(f"{'=' * 50}\n")

if __name__ == "__main__":
    main()
