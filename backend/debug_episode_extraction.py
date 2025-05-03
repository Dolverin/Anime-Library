#!/usr/bin/env python3
"""
Debug-Script zur Analyse der Episoden-Extraktion für Solo Leveling: Wie man stärker wird
"""
import os
import sys
import logging
from pprint import pprint

# Damit wir das Skript vom Projektstamm ausführen können
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper.scraper import get_page_content, extract_episode_list

# Logger konfigurieren
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_episode_extraction(url: str) -> None:
    """
    Debuggt die Episoden-Extraktion für eine bestimmte URL.
    
    Args:
        url: Die URL zur Anime-Seite
    """
    logger.info(f"Starte Debug der Episoden-Extraktion für URL: {url}")
    
    # Hole den HTML-Inhalt
    soup = get_page_content(url)
    
    if not soup:
        logger.error(f"Konnte keine Verbindung zur Seite herstellen: {url}")
        return
    
    # Debug: Alle a-Tags mit href, die mit Episode zu tun haben könnten
    episode_links_raw = soup.select('a')
    logger.info(f"Gefundene <a>-Tags insgesamt: {len(episode_links_raw)}")
    
    episode_links = []
    for link in episode_links_raw:
        href = link.get('href', '')
        text = link.text.strip()
        if (href and ('episode' in href.lower() or 'folge' in href.lower() or 'ep' in href.lower())) or \
           (text and ('episode' in text.lower() or 'folge' in text.lower() or 'ep' in text.lower())):
            episode_links.append({
                'href': href,
                'text': text
            })
    
    logger.info(f"Episoden-bezogene Links: {len(episode_links)}")
    logger.info("Details der gefundenen Links:")
    for i, link in enumerate(episode_links, 1):
        logger.info(f"Link {i}: Text: '{link['text']}', Href: '{link['href']}'")
    
    # Debug: Alle div-Tags mit episode im class-Namen
    episode_divs = soup.select('div[class*="episode"], div.episodes, div.episoden')
    logger.info(f"Episoden-bezogene Div-Tags: {len(episode_divs)}")
    
    # Debug: Alle div-Tags mit download im class-Namen
    download_divs = soup.select('div[class*="download"], div[id*="download"]')
    logger.info(f"Download-bezogene Div-Tags: {len(download_divs)}")
    for i, div in enumerate(download_divs, 1):
        logger.info(f"Download Div {i}: ID: '{div.get('id')}', Class: '{div.get('class')}'")
        links_in_div = div.select('a')
        logger.info(f"  Enthält {len(links_in_div)} Links")
        for j, link in enumerate(links_in_div, 1):
            logger.info(f"    Link {j}: Text: '{link.text.strip()}', Href: '{link.get('href', '')}'")
    
    # Extrahiere Episoden mit unserem Algorithmus
    episodes = extract_episode_list(soup)
    
    logger.info(f"Extrahierte Episoden: {len(episodes)}")
    logger.info("Details der extrahierten Episoden:")
    for episode in episodes:
        logger.info(f"Episode {episode['number']}: {episode['title']}")
        logger.info(f"  URLs: {episode['urls']}")

if __name__ == "__main__":
    # Nutze den Kommandozeilenparameter als URL oder default
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.anime-loads.org/media/ore-dake-level-up-na-ken-how-to-get-stronger"
    debug_episode_extraction(url)
