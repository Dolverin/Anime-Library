"""
Scraper-Funktionen für anime-loads.org

Dieses Modul enthält Funktionen zum Extrahieren von Anime-Daten von anime-loads.org
"""

import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

from .. import schemas
from ..models import AnimeStatus

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konstanten
BASE_URL = "https://www.anime-loads.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
}

def get_page_content(url: str) -> Optional[BeautifulSoup]:
    """
    Holt den HTML-Inhalt einer URL und gibt ein BeautifulSoup-Objekt zurück.
    
    Args:
        url: Die URL, von der der Inhalt abgerufen werden soll
        
    Returns:
        BeautifulSoup-Objekt oder None bei Fehlern
    """
    try:
        # Stelle sicher, dass die URL absolut ist
        if not url.startswith(('http://', 'https://')):
            url = urljoin(BASE_URL, url)
            
        logger.info(f"Rufe URL ab: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Wirft eine Exception bei HTTP-Fehlern
        
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der URL {url}: {e}")
        return None

def extract_anime_info(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Extrahiert Anime-Informationen aus dem BeautifulSoup-Objekt.
    
    Args:
        soup: BeautifulSoup-Objekt der Anime-Detailseite
        url: Die URL der Anime-Detailseite
        
    Returns:
        Dictionary mit Anime-Daten
    """
    anime_data = {}
    
    try:
        # Titel extrahieren
        title_element = soup.select_one('h1.title')
        if title_element:
            anime_data['titel'] = title_element.text.strip()
        else:
            logger.warning("Titel konnte nicht gefunden werden")
            anime_data['titel'] = "Unbekannter Titel"
        
        # Cover-Bild extrahieren
        cover_img = soup.select_one('div.cover img')
        if cover_img and cover_img.has_attr('src'):
            cover_url = cover_img['src']
            # Stelle sicher, dass die URL absolut ist
            if not cover_url.startswith(('http://', 'https://')):
                cover_url = urljoin(BASE_URL, cover_url)
            anime_data['cover_image_url'] = cover_url
        
        # Beschreibung extrahieren
        description = soup.select_one('div.description')
        if description:
            anime_data['beschreibung'] = description.text.strip()
        else:
            anime_data['beschreibung'] = ""
        
        # URL der Anime-Seite speichern
        anime_data['anime_loads_url'] = url
        
        # Status (standardmäßig auf "plan_to_watch" setzen)
        anime_data['status'] = AnimeStatus.plan_to_watch
        
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren der Anime-Informationen: {e}")
    
    return anime_data

def extract_episode_list(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Extrahiert die Episodenliste aus dem BeautifulSoup-Objekt.
    
    Args:
        soup: BeautifulSoup-Objekt der Anime-Detailseite
        
    Returns:
        Liste von Episoden-Dictionaries
    """
    episodes = []
    
    try:
        # Episodenliste finden
        episode_containers = soup.select('div.episodes div.episode')
        
        for i, episode in enumerate(episode_containers, 1):
            episode_data = {}
            
            # Episodennummer (falls nicht gefunden, verwende den Index)
            episode_data['episoden_nummer'] = i
            
            # Episodentitel
            title_element = episode.select_one('div.title')
            if title_element:
                episode_data['titel'] = title_element.text.strip()
            else:
                episode_data['titel'] = f"Episode {i}"
            
            # Link zur Episode
            link_element = episode.select_one('a')
            if link_element and link_element.has_attr('href'):
                episode_url = link_element['href']
                # Stelle sicher, dass die URL absolut ist
                if not episode_url.startswith(('http://', 'https://')):
                    episode_url = urljoin(BASE_URL, episode_url)
                episode_data['anime_loads_episode_url'] = episode_url
            
            # Standardwerte
            episode_data['status'] = "nicht_gesehen"  # oder ein entsprechendes Enum
            episode_data['air_date'] = None  # Könnte in Zukunft extrahiert werden
            
            episodes.append(episode_data)
            
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren der Episodenliste: {e}")
    
    return episodes

def scrape_anime(url: str) -> Optional[schemas.AnimeCreate]:
    """
    Scrapt einen Anime von anime-loads.org und gibt ein AnimeCreate-Objekt zurück.
    
    Args:
        url: Die URL der Anime-Detailseite
        
    Returns:
        AnimeCreate-Objekt oder None bei Fehlern
    """
    # Stelle sicher, dass die URL absolut ist
    if not url.startswith(('http://', 'https://')):
        url = urljoin(BASE_URL, url)
    
    # Extrahiere die Seite
    soup = get_page_content(url)
    if not soup:
        logger.error(f"Konnte die Seite {url} nicht abrufen")
        return None
    
    # Extrahiere Anime-Informationen
    anime_data = extract_anime_info(soup, url)
    
    # Erstelle ein AnimeCreate-Objekt
    try:
        anime = schemas.AnimeCreate(
            titel=anime_data.get('titel', "Unbekannter Titel"),
            status=anime_data.get('status', AnimeStatus.plan_to_watch),
            beschreibung=anime_data.get('beschreibung', ""),
            anime_loads_url=anime_data.get('anime_loads_url', url),
            cover_image_url=anime_data.get('cover_image_url', None)
        )
        return anime
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des AnimeCreate-Objekts: {e}")
        return None

def scrape_episode_list(url: str) -> Optional[List[schemas.EpisodeCreate]]:
    """
    Scrapt die Episodenliste eines Animes von anime-loads.org.
    
    Args:
        url: Die URL der Anime-Detailseite
        
    Returns:
        Liste von EpisodeCreate-Objekten oder None bei Fehlern
    """
    # Stelle sicher, dass die URL absolut ist
    if not url.startswith(('http://', 'https://')):
        url = urljoin(BASE_URL, url)
    
    # Extrahiere die Seite
    soup = get_page_content(url)
    if not soup:
        logger.error(f"Konnte die Seite {url} nicht abrufen")
        return None
    
    # Extrahiere Episodenliste
    episodes_data = extract_episode_list(soup)
    
    # Erstelle EpisodeCreate-Objekte
    try:
        episodes = []
        for ep_data in episodes_data:
            episode = schemas.EpisodeCreate(
                episoden_nummer=ep_data.get('episoden_nummer', 0),
                titel=ep_data.get('titel', f"Episode {ep_data.get('episoden_nummer', 0)}"),
                status=ep_data.get('status', "nicht_gesehen"),
                anime_loads_episode_url=ep_data.get('anime_loads_episode_url', None),
                air_date=ep_data.get('air_date', None)
            )
            episodes.append(episode)
        
        return episodes
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der EpisodeCreate-Objekte: {e}")
        return None
