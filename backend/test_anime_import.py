#!/usr/bin/env python3
"""
Test-Skript für das direkte Importieren eines Anime von anime-loads.org
"""
import sys
import logging
import json
from app.scraper.scraper import get_page_content, extract_anime_info, extract_episode_list

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion für den Test des Anime-Imports."""
    # Beispiel-URL, falls keine angegeben wurde
    url = "https://www.anime-loads.org/media/solo-leveling" if len(sys.argv) < 2 else sys.argv[1]
    
    logger.info(f"Starte Import des Anime: {url}")
    
    # Hole den HTML-Inhalt
    soup = get_page_content(url)
    
    if not soup:
        logger.error(f"Konnte keine Verbindung zur Seite herstellen für: {url}")
        return
    
    # HTML in eine Datei speichern zur Analyse
    with open("anime_page.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    logger.info("HTML-Seite wurde als 'anime_page.html' gespeichert")
    
    # Extrahiere Anime-Informationen
    anime_info = extract_anime_info(soup, url)
    
    if not anime_info:
        logger.error("Konnte keine Anime-Informationen extrahieren")
        return
    
    # Anime-Informationen ausgeben
    print(f"\n{'=' * 50}")
    print("ANIME-INFORMATIONEN")
    print(f"{'=' * 50}")
    
    # Formatierte Ausgabe der Anime-Informationen
    print(f"Titel: {anime_info.get('title', 'Unbekannt')}")
    print(f"Beschreibung: {anime_info.get('description', 'Keine Beschreibung')[:100]}...")
    print(f"Cover: {anime_info.get('cover_image', 'Kein Bild')}")
    print(f"Status: {anime_info.get('status', 'Unbekannt')}")
    print(f"Genres: {', '.join(anime_info.get('genres', ['Keine Genres']))}")
    
    # Anime-Informationen als JSON speichern
    with open("anime_info.json", "w", encoding="utf-8") as f:
        json.dump(anime_info, f, indent=4, ensure_ascii=False)
    logger.info("Anime-Informationen wurden als 'anime_info.json' gespeichert")
    
    # Extrahiere Episoden
    episodes = extract_episode_list(soup)
    
    if not episodes:
        logger.error("Konnte keine Episoden extrahieren")
        return
    
    # Episoden-Informationen ausgeben
    print(f"\n{'=' * 50}")
    print("EPISODEN-INFORMATIONEN")
    print(f"{'=' * 50}")
    print(f"Anzahl der Episoden: {len(episodes)}")
    
    # Formatierte Ausgabe der ersten 5 Episoden (oder weniger, falls weniger vorhanden)
    for i, episode in enumerate(episodes[:5]):
        print(f"\nEpisode {i+1}:")
        print(f"  Nummer: {episode.get('number', 'Unbekannt')}")
        print(f"  Titel: {episode.get('title', 'Unbekannt')}")
        print(f"  URL: {episode.get('url', 'Keine URL')}")
    
    # Episoden-Informationen als JSON speichern
    with open("episodes_info.json", "w", encoding="utf-8") as f:
        json.dump(episodes, f, indent=4, ensure_ascii=False)
    logger.info("Episoden-Informationen wurden als 'episodes_info.json' gespeichert")

if __name__ == "__main__":
    main()
