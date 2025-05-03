#!/usr/bin/env python3
"""
Debug-Skript zum Analysieren des HTML-Codes der Suchergebnisse auf anime-loads.org
"""
import sys
import logging
import os
from app.scraper.scraper import get_page_content

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion zum Debuggen der Suchergebnisse."""
    query = "solo" if len(sys.argv) < 2 else sys.argv[1]
    search_url = f"https://www.anime-loads.org/search?s={query}"
    
    logger.info(f"Debugging HTML der Suchergebnisse für: {query}")
    
    # HTML-Inhalt der Suchergebnisseite abrufen
    soup = get_page_content(search_url)
    
    if not soup:
        logger.error(f"Konnte keine Verbindung zur Seite herstellen für: {query}")
        return
    
    # HTML in eine Datei speichern
    html_file = "search_results.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(str(soup))
    
    logger.info(f"HTML-Code wurde in {html_file} gespeichert")
    
    # Analyse der wichtigsten Strukturen
    logger.info("Analysiere HTML-Struktur...")
    
    # Verschiedene selektoren ausprobieren
    selectors_to_try = [
        "div.card", 
        "div.anime-card", 
        "div.search-result", 
        "div.results", 
        "div.anime", 
        "div.anime-item",
        "article",
        "div.row div"
    ]
    
    for selector in selectors_to_try:
        elements = soup.select(selector)
        logger.info(f"Selektor '{selector}': {len(elements)} Elemente gefunden")
    
    # Suche nach dem title-Element für Solo Leveling
    title_elements = soup.find_all(string=lambda text: text and "solo" in text.lower())
    logger.info(f"Textelemente mit 'solo': {len(title_elements)}")
    for i, elem in enumerate(title_elements[:10]):  # Beschränke auf die ersten 10
        parent_tag = elem.parent.name if elem.parent else "None"
        logger.info(f"  {i+1}. Text: '{elem.strip()}', Parent-Tag: {parent_tag}")
    
    # Title und body untersuchen
    title = soup.find("title")
    logger.info(f"Seitentitel: {title.text if title else 'Nicht gefunden'}")
    
    # Meta-Tags überprüfen
    for meta in soup.find_all("meta"):
        if meta.get("name") in ["description", "keywords"] or meta.get("property", "").startswith("og:"):
            logger.info(f"Meta-Tag: {meta}")

if __name__ == "__main__":
    main()
