#!/usr/bin/env python3
"""
Skript zum Überprüfen der Homepage von anime-loads.org und Extrahieren von Links
"""
import logging
from bs4 import BeautifulSoup
from app.scraper.scraper import get_page_content

# Logger einrichten
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.anime-loads.org"

def main():
    """Hauptfunktion zum Überprüfen der Homepage und Extrahieren von Links."""
    # Homepage abrufen
    logger.info(f"Rufe Homepage ab: {BASE_URL}")
    soup = get_page_content(BASE_URL)
    
    if not soup:
        logger.error("Konnte keine Verbindung zur Homepage herstellen")
        return
    
    # HTML in Datei speichern
    with open("homepage.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    logger.info("Homepage HTML wurde in 'homepage.html' gespeichert")
    
    # Extrahiere Links zu Anime-Seiten
    logger.info("Suche nach Anime-Links...")
    
    # Verschiedene Selektoren ausprobieren, um Anime-Links zu finden
    selectors = [
        'a.card-link', 
        'div.card a', 
        'div.media a',
        'a[href*="/media/"]',  # Links, die "/media/" enthalten
        'a[href*="/anime/"]',  # Links, die "/anime/" enthalten
        'a[href*="/title/"]'   # Links, die "/title/" enthalten
    ]
    
    all_anime_links = []
    
    for selector in selectors:
        links = soup.select(selector)
        logger.info(f"Selektor '{selector}': {len(links)} Links gefunden")
        
        for link in links[:10]:  # Nur die ersten 10 anzeigen
            href = link.get('href', '')
            if href:
                # Prüfen, ob es ein Anime-Link ist (enthält typischerweise "/media/", "/anime/" oder "/title/")
                if any(pattern in href for pattern in ['/media/', '/anime/', '/title/']):
                    full_url = href if href.startswith('http') else BASE_URL + href
                    text = link.get_text().strip() or "Kein Text"
                    all_anime_links.append((text, full_url))
                    logger.info(f"  - {text}: {full_url}")
    
    # Einzigartige Links ausgeben
    unique_links = list(set(all_anime_links))
    logger.info(f"Insgesamt {len(unique_links)} einzigartige Anime-Links gefunden")
    
    print(f"\n{'=' * 50}")
    print("GEFUNDENE ANIME-LINKS")
    print(f"{'=' * 50}")
    
    for i, (text, url) in enumerate(unique_links[:20], 1):  # Begrenzen auf die ersten 20
        print(f"{i}. {text}")
        print(f"   URL: {url}")
        print()
    
    # Prüfe, ob "Solo Leveling" unter den Links ist
    solo_links = [link for text, link in unique_links if "solo" in text.lower()]
    if solo_links:
        print(f"\n{'=' * 50}")
        print("GEFUNDENE LINKS ZU SOLO LEVELING")
        print(f"{'=' * 50}")
        for i, link in enumerate(solo_links, 1):
            print(f"{i}. {link}")

if __name__ == "__main__":
    main()
