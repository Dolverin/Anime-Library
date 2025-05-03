"""
Scraper-Funktionen für anime-loads.org

Dieses Modul enthält Funktionen zum Extrahieren von Anime-Daten von anime-loads.org
"""

import re
import logging
import random
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

from .. import schemas
from ..models import AnimeStatus
from playwright.sync_api import sync_playwright, Error as PlaywrightError

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konstanten
BASE_URL = "https://www.anime-loads.org"

# Browser Headers - zufällige Auswahl für jede Anfrage
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
]

def get_random_user_agent():
    """Gibt einen zufälligen User-Agent zurück."""
    return random.choice(USER_AGENTS)

def get_page_content(url: str) -> Optional[BeautifulSoup]:
    """Fetches page content using Playwright and returns a BeautifulSoup object."""
    user_agent = get_random_user_agent()
    logger.info(f"Attempting to fetch URL: {url} using Playwright with User-Agent: {user_agent}")
    try:
        with sync_playwright() as p:
            # Firefox statt Chromium verwenden, da einige Webseiten Chromium-automatisierung stärker erkennen
            browser = p.firefox.launch(headless=True)
            
            # Browser-Kontext mit zusätzlichen Optionen erstellen
            context = browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1366, 'height': 768},
                locale='de-DE',
                timezone_id='Europe/Berlin',
                # Geolocation auf deutschen Standort setzen
                geolocation={'latitude': 52.5200, 'longitude': 13.4050, 'accuracy': 100},
                # JavaScript-Ausführung erlauben
                java_script_enabled=True,
                # Verhindert das Erkennen der Automation
                bypass_csp=True,
                # Cookies akzeptieren
                accept_downloads=True,
            )
            
            # Neue Seite erstellen
            page = context.new_page()
            
            # Cookie-Banner akzeptieren, falls vorhanden - häufig wird dadurch der Zugriff ermöglicht
            page.goto(BASE_URL, wait_until='domcontentloaded', timeout=30000)
            
            # Kurze Pause, damit die Seite vollständig geladen wird
            page.wait_for_timeout(2000 + random.randint(500, 2000))
            
            # Versuche Cookie-Banner zu akzeptieren (häufige Selektoren)
            for selector in [
                'button[aria-label="Alle akzeptieren"]', 
                'button:has-text("Akzeptieren")', 
                'button:has-text("Zustimmen")',
                'button.btn-primary',
                'a:has-text("Akzeptieren")'
            ]:
                try:
                    if page.locator(selector).count() > 0:
                        page.locator(selector).first.click()
                        logger.info(f"Clicked on cookie consent using selector: {selector}")
                        # Nach dem Klick kurz warten
                        page.wait_for_timeout(1000 + random.randint(500, 1500))
                        break
                except Exception as e:
                    logger.debug(f"Could not click selector {selector}: {e}")
            
            # Menschliches Scrollverhalten simulieren
            for _ in range(3):
                # Random Scroll nach unten
                page.mouse.wheel(0, random.randint(300, 700))
                page.wait_for_timeout(random.randint(500, 1500))
            
            # Jetzt zur eigentlichen URL navigieren
            logger.info(f"Navigating to: {url}")
            response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Zufällige Wartezeit nach dem Laden
            page.wait_for_timeout(2000 + random.randint(500, 2000))
            
            # Menschliches Scrollverhalten simulieren
            for _ in range(3):
                # Random Scroll nach unten
                page.mouse.wheel(0, random.randint(300, 700))
                page.wait_for_timeout(random.randint(500, 1500))
            
            if response and response.ok:
                # Mit wait_for_load_state sicherstellen, dass die Seite vollständig geladen ist
                page.wait_for_load_state('networkidle')
                content = page.content()
                browser.close()
                logger.info(f"Successfully fetched content from {url}")
                return BeautifulSoup(content, 'html.parser')
            else:
                status = response.status if response else 'No Response'
                logger.error(f"Failed to fetch {url}. Status: {status}")
                
                # Bei 403 oder 429 Fehler, versuche ein Screenshot zu machen, um das Problem zu diagnostizieren
                if response and (response.status == 403 or response.status == 429):
                    logger.info("Capturing screenshot of blocked page for debugging")
                    page.screenshot(path="blocked_page.png")
                
                browser.close()
                return None
                
    except PlaywrightError as e:
        logger.error(f"Playwright error fetching {url}: {e}")
        # Ensure browser is closed in case of error before page.goto completes
        if 'browser' in locals() and browser.is_connected():
             browser.close()
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching {url}: {e}")
        if 'browser' in locals() and browser.is_connected():
             browser.close()
        return None

def save_debug_screenshot(page, filename: str = "debug_screenshot.png"):
    """Speichert einen Screenshot zur Fehlerbehebung."""
    try:
        logger.info(f"Speichere Debug-Screenshot als '{filename}'")
        page.screenshot(path=filename)
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Screenshots: {e}")

def download_image(url: str) -> Optional[bytes]:
    """
    Lädt ein Bild von einer URL herunter und gibt es als Binärdaten zurück.
    
    Args:
        url: Die URL des Bildes
        
    Returns:
        Binärdaten des Bildes oder None bei Fehler
    """
    try:
        logger.info(f"Lade Bild herunter: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Fehler beim Herunterladen des Bildes von {url}: {e}")
        return None

def extract_anime_info(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Extrahiert Anime-Informationen aus einem BeautifulSoup-Objekt.
    
    Args:
        soup: BeautifulSoup-Objekt mit dem HTML-Inhalt
        url: Original-URL der Anime-Seite
        
    Returns:
        Dictionary mit Anime-Informationen
    """
    anime_info = {
        "title": "Unbekannt",
        "original_titel": "",
        "synonyme": "",
        "beschreibung": "Keine Beschreibung",
        "status": AnimeStatus.plan_to_watch,
        "typ": "",
        "jahr": None,
        "episoden_anzahl": "",
        "laufzeit": "",
        "hauptgenre": "",
        "nebengenres": "",
        "tags": "",
        "cover_image": "Kein Bild",
        "cover_image_data": None,
        "url": url,
        "anime_loads_id": url.split('/')[-1] if url else "",
        "anisearch_url": "",
        "relations": []
    }
    
    try:
        # Suche nach dem Titel in verschiedenen möglichen Selektoren
        title_selectors = [
            'h1.title', 
            'h1.anime-title', 
            'div.media-heading h1', 
            'div.title h1',
            'h1',
            'div.info h2',
            'meta[property="og:title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                if selector == 'meta[property="og:title"]':
                    anime_info["title"] = title_elem.get('content', '').strip()
                else:
                    anime_info["title"] = title_elem.text.strip()
                logger.info(f"Titel gefunden mit Selektor '{selector}': {anime_info['title']}")
                break
        
        if anime_info["title"] == "Unbekannt":
            logger.warning("Titel konnte nicht gefunden werden")
            # Versuche alternativ den Seitentitel zu verwenden
            if soup.title:
                page_title = soup.title.text.strip()
                if page_title and page_title != "Such Ergebnisse":
                    anime_info["title"] = page_title
                    logger.info(f"Verwende Seitentitel: {anime_info['title']}")
        
        # Beschreibung
        description_selectors = [
            'div.description', 
            'div.anime-description', 
            'div.content p',
            'meta[property="og:description"]',
            'meta[name="description"]',
            'div.info p',
            'div.description-content'
        ]
        
        for selector in description_selectors:
            desc_elems = soup.select(selector)
            if desc_elems:
                desc_texts = [elem.get('content', '').strip() if selector.startswith('meta') else elem.text.strip() 
                              for elem in desc_elems]
                desc_text = ' '.join([t for t in desc_texts if t and "downloads und streams von anime" not in t.lower()])
                
                if desc_text:
                    anime_info["beschreibung"] = desc_text
                    logger.info(f"Beschreibung gefunden mit Selektor '{selector}'")
                    # Suche nach "Quelle: aniSearch" in der Beschreibung
                    if "quelle: anisearch" in desc_text.lower():
                        anime_info["anisearch_url"] = "https://www.anisearch.de/anime/?" + anime_info["title"].replace(" ", "+")
                        logger.info(f"AniSearch-Referenz in der Beschreibung gefunden")
                    break
        
        # Cover-Bild
        cover_selectors = [
            'div.cover img', 
            'div.anime-cover img', 
            'div.media-left img',
            'meta[property="og:image"]',
            'div.poster img',
            'img.cover-image'
        ]
        
        for selector in cover_selectors:
            cover_elem = soup.select_one(selector)
            if cover_elem:
                if selector.startswith('meta'):
                    cover_url = cover_elem.get('content', '')
                else:
                    cover_url = cover_elem.get('src', '')
                
                if cover_url and not cover_url.endswith('logo_meta.png'):
                    # Absolute URL sicherstellen
                    if not cover_url.startswith(('http://', 'https://')):
                        cover_url = urljoin(BASE_URL, cover_url)
                    
                    anime_info["cover_image"] = cover_url
                    logger.info(f"Cover-Bild gefunden mit Selektor '{selector}': {cover_url}")
                    
                    # Cover-Bild herunterladen
                    cover_image_data = download_image(cover_url)
                    if cover_image_data:
                        anime_info["cover_image_data"] = cover_image_data
                        logger.info(f"Cover-Bild erfolgreich heruntergeladen: {len(cover_image_data)} Bytes")
                    break
        
        # Metadaten extrahieren (Typ, Jahr, Episoden, etc.)
        info_rows = soup.select('div.info-table tr') or soup.select('table.info-table tr')
        
        for row in info_rows:
            label_elem = row.select_one('th') or row.select_one('td:first-child')
            value_elem = row.select_one('td:last-child')
            
            if not (label_elem and value_elem):
                continue
                
            label = label_elem.text.strip().lower()
            value = value_elem.text.strip()
            
            if not value:
                continue
                
            if 'titel' in label:
                if anime_info["original_titel"] == "":
                    anime_info["original_titel"] = value
                
            elif 'synonym' in label:
                anime_info["synonyme"] = value
                
            elif 'typ' in label:
                anime_info["typ"] = value
                
            elif 'episoden' in label:
                anime_info["episoden_anzahl"] = value
                
            elif 'jahr' in label:
                try:
                    anime_info["jahr"] = int(value)
                except ValueError:
                    anime_info["jahr"] = None
                    
            elif 'laufzeit' in label:
                anime_info["laufzeit"] = value
                
            elif 'status' in label:
                if 'abgeschlossen' in value.lower():
                    anime_info["status"] = AnimeStatus.completed
                elif 'läuft' in value.lower() or 'laufend' in value.lower():
                    anime_info["status"] = AnimeStatus.watching
                    
            elif 'hauptgenre' in label:
                anime_info["hauptgenre"] = value
                
            elif 'nebengenre' in label:
                anime_info["nebengenres"] = value
                
            elif 'tag' in label:
                anime_info["tags"] = value
                
            elif 'quelle' in label and 'anisearch' in value.lower():
                anisearch_link = value_elem.select_one('a')
                if anisearch_link and anisearch_link.get('href'):
                    anime_info["anisearch_url"] = anisearch_link.get('href')
                    logger.info(f"AniSearch-Link gefunden: {anime_info['anisearch_url']}")
        
        # Genres
        genre_selectors = [
            'div.genres a', 
            'div.genre-list a', 
            'div.tags a',
            'span.genre'
        ]
        
        for selector in genre_selectors:
            genre_elems = soup.select(selector)
            if genre_elems:
                genres = [genre.text.strip() for genre in genre_elems if genre.text.strip()]
                if genres:
                    if not anime_info["hauptgenre"] and genres:
                        anime_info["hauptgenre"] = genres[0]
                        
                    if not anime_info["nebengenres"] and len(genres) > 1:
                        anime_info["nebengenres"] = " ".join(genres[1:])
                        
                    logger.info(f"Genres gefunden mit Selektor '{selector}': {genres}")
                    break
        
        # Suche nach dem "Related" Tab oder Bereich, um Relationen zu extrahieren
        # Versuche direkt den Link zu finden
        relation_url = urljoin(url, "#related")
        logger.info(f"Suche nach Relationen auf: {relation_url}")
        
        related_section = soup.select_one('#related') or soup.select_one('div.related')
        
        if related_section:
            relation_links = related_section.select('a[href*="/media/"]')
            
            for link in relation_links:
                relation_url = link.get('href', '')
                if not relation_url:
                    continue
                    
                # Absolute URL sicherstellen
                if not relation_url.startswith(('http://', 'https://')):
                    relation_url = urljoin(BASE_URL, relation_url)
                
                relation_title = link.text.strip()
                if not relation_title:
                    relation_title = relation_url.split('/')[-1].replace('-', ' ').title()
                
                # Versuche, den Relationstyp zu ermitteln
                relation_type = "related"  # Standardwert
                relation_parent = link.parent
                
                if relation_parent:
                    relation_label = relation_parent.select_one('span') or relation_parent.previous_sibling
                    if relation_label:
                        relation_label_text = relation_label.text.strip().lower()
                        
                        if "sequel" in relation_label_text or "fortsetzung" in relation_label_text:
                            relation_type = "sequel"
                        elif "prequel" in relation_label_text or "vorgeschichte" in relation_label_text:
                            relation_type = "prequel"
                        elif "spin-off" in relation_label_text:
                            relation_type = "spin-off"
                        elif "alternativ" in relation_label_text:
                            relation_type = "alternative"
                
                anime_info["relations"].append({
                    "url": relation_url,
                    "title": relation_title,
                    "type": relation_type
                })
                logger.info(f"Relation gefunden: {relation_title} ({relation_url}) - Typ: {relation_type}")
        
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren der Anime-Informationen: {e}")
    
    return anime_info

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
        # Verschiedene Selektoren für Episoden-Container ausprobieren
        episode_selectors = [
            'div.episodes div.episode',
            'div.episode-list div.episode',
            'div.episode-container',
            'div.episode-list-item',
            'div.episodes li',
            'ul.episodes li',
            'div.episodes a',
            'table.episodes tr'
        ]
        
        episode_containers = None
        used_selector = None
        
        for selector in episode_selectors:
            containers = soup.select(selector)
            if containers:
                episode_containers = containers
                used_selector = selector
                logger.info(f"Episoden gefunden mit Selektor '{selector}': {len(containers)}")
                break
        
        if not episode_containers:
            logger.warning("Keine Episoden gefunden mit den verfügbaren Selektoren")
            return episodes
        
        for i, episode in enumerate(episode_containers, 1):
            episode_data = {
                'number': i,
                'title': f"Episode {i}",
                'url': "",
                'anime_loads_episode_url': ""
            }
            
            # Versuche, die Nummer der Episode zu extrahieren
            number_selectors = [
                'div.number', 
                'span.number', 
                'span.episode-number',
                'td:first-child',
                '.episode-num'
            ]
            
            for selector in number_selectors:
                number_elem = episode.select_one(selector)
                if number_elem and number_elem.text.strip():
                    try:
                        # Versuche, die Nummer als Integer zu parsen
                        number_text = number_elem.text.strip()
                        if number_text.isdigit():
                            episode_data['number'] = int(number_text)
                        else:
                            # Extraktion von Zahlen aus Text wie "Episode 5"
                            matches = re.findall(r'\d+', number_text)
                            if matches:
                                episode_data['number'] = int(matches[0])
                        break
                    except (ValueError, IndexError):
                        # Weiterhin die Standard-Nummerierung verwenden
                        pass
            
            # Versuche, den Titel der Episode zu extrahieren
            title_selectors = [
                'div.title', 
                'span.title', 
                'a.episode-link',
                'td:nth-child(2)',
                '.episode-title'
            ]
            
            for selector in title_selectors:
                title_elem = episode.select_one(selector)
                if title_elem and title_elem.text.strip():
                    episode_title = title_elem.text.strip()
                    if episode_title:
                        episode_data['title'] = episode_title
                        break
            
            # Versuche, den Link zur Episode zu extrahieren
            link_elem = episode.select_one('a') or episode.parent if episode.name != 'a' else episode
            
            if link_elem and hasattr(link_elem, 'get') and link_elem.get('href'):
                episode_url = link_elem.get('href')
                # Absolute URL sicherstellen
                if not episode_url.startswith(('http://', 'https://')):
                    episode_url = urljoin(BASE_URL, episode_url)
                
                episode_data['url'] = episode_url
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
            titel=anime_data.get('title', "Unbekannter Titel"),
            status=anime_data.get('status', AnimeStatus.plan_to_watch),
            beschreibung=anime_data.get('beschreibung', ""),
            anime_loads_url=anime_data.get('url', url),
            cover_image_url=anime_data.get('cover_image', None)
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
                episoden_nummer=ep_data.get('number', 0),
                titel=ep_data.get('title', f"Episode {ep_data.get('number', 0)}"),
                status=ep_data.get('status', "nicht_gesehen"),
                anime_loads_episode_url=ep_data.get('anime_loads_episode_url', None),
                air_date=ep_data.get('air_date', None)
            )
            episodes.append(episode)
        
        return episodes
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der EpisodeCreate-Objekte: {e}")
        return None

def search_anime(query: str) -> List[Dict[str, str]]:
    """
    Sucht nach Anime auf anime-loads.org anhand des Suchbegriffs.
    
    Args:
        query: Der Suchbegriff
        
    Returns:
        Liste von Dictionaries mit Informationen zu den gefundenen Anime (Titel, URL, Cover-Bild)
    """
    search_url = f"{BASE_URL}/search?q={query}"
    logger.info(f"Suche nach Anime mit Suchbegriff: {query}")
    
    results = []
    soup = get_page_content(search_url)
    
    if not soup:
        logger.error(f"Keine Suchergebnisse gefunden für: {query}")
        return results
    
    # HTML für Debug-Zwecke speichern
    with open(f"search_results_{query}.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    logger.info(f"HTML der Suchergebnisse wurde in 'search_results_{query}.html' gespeichert")
    
    # Verschiedene Selektoren für Anime-Karten/Ergebnisse ausprobieren
    anime_selectors = [
        'div.card',
        'div.media',
        'div.result',
        'div.search-result',
        'div.item',
        'div.anime-item',
        'div.result-item',
        'div.media-container',
        'article.media',
        'a[href*="/media/"]'  # Links die "/media/" im Pfad haben
    ]
    
    for selector in anime_selectors:
        anime_elems = soup.select(selector)
        
        if anime_elems:
            logger.info(f"Anime-Elemente gefunden mit Selektor '{selector}': {len(anime_elems)}")
            
            for anime_elem in anime_elems:
                try:
                    anime_data = {}
                    
                    # Link und URL extrahieren
                    link_elem = anime_elem if anime_elem.name == 'a' else anime_elem.select_one('a[href*="/media/"]')
                    
                    if not link_elem:
                        # Falls kein direkter Link zu /media/ gefunden wurde, jeden Link überprüfen
                        all_links = anime_elem.select('a')
                        for a_tag in all_links:
                            href = a_tag.get('href', '')
                            if href and '/media/' in href:
                                link_elem = a_tag
                                break
                    
                    if not link_elem or not link_elem.get('href'):
                        continue
                    
                    anime_url = link_elem.get('href')
                    # Absolute URL sicherstellen
                    if not anime_url.startswith(('http://', 'https://')):
                        anime_url = urljoin(BASE_URL, anime_url)
                    
                    anime_data['url'] = anime_url
                    
                    # Titel extrahieren (aus verschiedenen möglichen Elementen)
                    title_selectors = [
                        'h5.card-title',
                        'h3.title',
                        'div.title',
                        'span.title',
                        '.anime-title',
                        'h4',
                        'h5'
                    ]
                    
                    title_found = False
                    for title_selector in title_selectors:
                        title_elem = anime_elem.select_one(title_selector)
                        if title_elem and title_elem.text.strip():
                            anime_data['title'] = title_elem.text.strip()
                            title_found = True
                            break
                    
                    # Falls kein Titel gefunden wurde, versuche den Text des Links
                    if not title_found and link_elem.text.strip():
                        anime_data['title'] = link_elem.text.strip()
                    
                    # Falls immer noch kein Titel, versuche den letzten Teil der URL
                    if not title_found and 'title' not in anime_data:
                        path_parts = anime_url.rstrip('/').split('/')
                        if path_parts:
                            slug = path_parts[-1].replace('-', ' ').title()
                            anime_data['title'] = slug
                    
                    # Bild-URL extrahieren (aus verschiedenen möglichen Elementen)
                    img_selectors = [
                        'img.card-img-top',
                        'img.cover',
                        'img.thumb',
                        'img.poster',
                        'img'
                    ]
                    
                    for img_selector in img_selectors:
                        img_elem = anime_elem.select_one(img_selector)
                        if img_elem and img_elem.get('src'):
                            img_url = img_elem.get('src')
                            # Absolute URL sicherstellen
                            if not img_url.startswith(('http://', 'https://')):
                                img_url = urljoin(BASE_URL, img_url)
                            anime_data['image_url'] = img_url
                            break
                    
                    # Nur Ergebnisse mit Titel und URL hinzufügen
                    if 'title' in anime_data and 'url' in anime_data:
                        anime_id = anime_data['url'].split('/')[-1]
                        anime_data['id'] = anime_id
                        
                        # Prüfen, ob das Ergebnis bereits existiert, um Duplikate zu vermeiden
                        if not any(r.get('id') == anime_id for r in results):
                            results.append(anime_data)
                            logger.info(f"Anime gefunden: {anime_data['title']} ({anime_data['url']})")
                    
                except Exception as e:
                    logger.error(f"Fehler beim Parsen eines Anime-Suchergebnisses: {e}")
                    continue
            
            # Wenn wir mit diesem Selektor Ergebnisse gefunden haben, breche die Schleife ab
            if results:
                break
    
    # Spezialfall: Falls keine strukturierten Ergebnisse gefunden wurden, versuche alle Links zu /media/
    if not results:
        logger.info("Versuche direkt Links zu extrahieren")
        media_links = soup.select('a[href*="/media/"]')
        for link in media_links:
            try:
                anime_url = link.get('href')
                # Absolute URL sicherstellen
                if not anime_url.startswith(('http://', 'https://')):
                    anime_url = urljoin(BASE_URL, anime_url)
                
                # Extrahiere ID aus URL
                anime_id = anime_url.split('/')[-1]
                
                # Prüfen, ob das Ergebnis bereits existiert
                if any(r.get('id') == anime_id for r in results):
                    continue
                
                title = link.text.strip()
                if not title:
                    # Verwende den letzten Teil der URL als Titel
                    title = anime_id.replace('-', ' ').title()
                
                anime_data = {
                    'title': title,
                    'url': anime_url,
                    'id': anime_id
                }
                
                # Suche nach einem naheliegenden Bild
                parent = link.parent
                img = None
                
                # Suche im Elternelement und in Geschwisterelementen nach Bildern
                for _ in range(3):  # Begrenzen auf 3 Ebenen, um nicht zu weit zu gehen
                    if parent:
                        img = parent.select_one('img')
                        if img and img.get('src'):
                            break
                        parent = parent.parent
                
                if img and img.get('src'):
                    img_url = img.get('src')
                    # Absolute URL sicherstellen
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = urljoin(BASE_URL, img_url)
                    anime_data['image_url'] = img_url
                
                results.append(anime_data)
                logger.info(f"Anime-Link gefunden: {anime_data['title']} ({anime_data['url']})")
                
            except Exception as e:
                logger.error(f"Fehler beim Extrahieren eines Anime-Links: {e}")
                continue
    
    logger.info(f"Insgesamt {len(results)} Anime-Ergebnisse gefunden für: {query}")
    return results
