"""
Scraper-Funktionen für anime-loads.org

Dieses Modul enthält Funktionen zum Extrahieren von Anime-Daten von anime-loads.org
"""

import re
import logging
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
import base64
import os

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
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()
            
            # Cookie-Banner akzeptieren
            try:
                page.goto("https://anime-loads.org")
                page.wait_for_timeout(random.randint(2000, 4000))
                cookie_accept_button = page.query_selector("button.btn-primary")
                if cookie_accept_button:
                    cookie_accept_button.click()
                    logger.info("Clicked on cookie consent using selector: button.btn-primary")
                    page.wait_for_timeout(random.randint(1000, 2000))
            except PlaywrightError as e:
                logger.warning(f"Error handling cookie banner: {e}")
            
            # Navigiere zur gewünschten URL
            logger.info(f"Navigating to: {url}")
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            if response.status != 200:
                logger.error(f"Failed to fetch {url}. Status: {response.status}")
                browser.close()
                return None
            
            # Warte auf das Laden der Seite und simuliere menschliches Verhalten
            page.wait_for_timeout(random.randint(3000, 5000))
            page.mouse.wheel(0, random.randint(300, 700))
            page.wait_for_timeout(random.randint(1000, 3000))
            
            html_content = page.content()
            browser.close()
            return BeautifulSoup(html_content, 'html.parser')
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
    Verwendet verschiedene Methoden, um DDoS-Schutzmaßnahmen zu umgehen.
    
    Args:
        url: Die URL des Bildes
        
    Returns:
        Binärdaten des Bildes oder None bei Fehler
    """
    try:
        # Method 1: Use FlareSolverr proxy
        flaresolverr_url = "http://localhost:8191/v1"
        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": 60000
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(flaresolverr_url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                image_url = data["solution"]["url"]
                image_response = requests.get(image_url, timeout=10)
                if image_response.status_code == 200:
                    return image_response.content
        logger.warning(f"FlareSolverr failed for {url}")
    except Exception as e:
        logger.error(f"Error using FlareSolverr for {url}: {str(e)}")

    # Spezialmethode für anime-loads.org Bilder
    if "anime-loads.org" in url and "/files/image/" in url:
        try:
            logger.info(f"Versuche spezielle Methode für anime-loads.org Bilder: {url}")
            # Extrahiere den Bildnamen aus der URL
            image_name = url.split('/')[-1]
            referer_url = "https://www.anime-loads.org/"
            
            # 1. Methode: Versuche mit speziellen Headern
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'de,en-US;q=0.9,en;q=0.8',
                'Referer': referer_url,
                'Origin': 'https://www.anime-loads.org',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'same-origin',
                'Cache-Control': 'max-age=0',
            }
            
            session = requests.Session()
            # Besuche zuerst die Hauptseite, um Cookies zu setzen
            main_page = session.get(referer_url, headers=headers, timeout=10)
            if main_page.status_code == 200:
                # Dann versuche das Bild zu holen
                img_response = session.get(url, headers=headers, timeout=10)
                if img_response.status_code == 200:
                    logger.info(f"Spezielle Methode für anime-loads.org erfolgreich: {len(img_response.content)} Bytes")
                    return img_response.content
                    
            # Versuch mit korrigierter URL (falls Bindestrich falsch ist)
            corrected_url = url.replace("/w200-", "/w200/")
            if corrected_url != url:
                logger.info(f"Versuche mit korrigierter URL: {corrected_url}")
                img_response = session.get(corrected_url, headers=headers, timeout=10)
                if img_response.status_code == 200:
                    logger.info(f"Spezielle Methode mit korrigierter URL erfolgreich: {len(img_response.content)} Bytes")
                    return img_response.content
        except Exception as e:
            logger.error(f"Fehler bei spezieller anime-loads.org Methode: {str(e)}")
            
    # Versuch, das Bild aus der Anime-Detailseite zu extrahieren
    if "anime-loads.org" in url:
        try:
            # Extrahiere die Anime-ID oder den Namen aus der URL
            parts = url.split('/')
            if len(parts) >= 5:
                # Versuche die Anime-Detailseite aus dem Bildpfad abzuleiten
                anime_id = None
                for part in parts:
                    if part.startswith("ore-dake") or "level-up" in part:
                        anime_id = part
                        break
                
                if anime_id:
                    # Konstruiere die URL zur Anime-Detailseite
                    anime_url = f"https://www.anime-loads.org/media/{anime_id}"
                    logger.info(f"Versuche Anime-Detailseite zu laden: {anime_url}")
                    
                    # Verwende Playwright, um die Seite zu laden und einen Screenshot zu machen
                    with sync_playwright() as p:
                        browser = p.firefox.launch(headless=True)
                        context = browser.new_context(
                            user_agent=get_random_user_agent(),
                            viewport={'width': 1366, 'height': 768}
                        )
                        page = context.new_page()
                        
                        try:
                            # Cookies akzeptieren
                            page.goto("https://www.anime-loads.org")
                            page.wait_for_timeout(random.randint(2000, 4000))
                            cookie_accept_button = page.query_selector("button.btn-primary")
                            if cookie_accept_button:
                                cookie_accept_button.click()
                                logger.info("Clicked on cookie consent using selector: button.btn-primary")
                                page.wait_for_timeout(random.randint(1000, 2000))
                        except Exception as e:
                            logger.warning(f"Error handling cookie banner: {e}")
                        
                        # Navigiere zur Anime-Seite
                        response = page.goto(anime_url, wait_until="domcontentloaded", timeout=30000)
                        
                        if response.status == 200:
                            # Warte auf das Laden der Seite
                            page.wait_for_timeout(random.randint(3000, 5000))
                            
                            # Finde das Cover-Element
                            cover_element = page.query_selector(".cover-image img, .anime-cover img, .cover img")
                            if cover_element:
                                # Mache einen Screenshot des Cover-Elements
                                screenshot = cover_element.screenshot()
                                browser.close()
                                logger.info(f"Cover-Screenshot erfolgreich: {len(screenshot)} Bytes")
                                return screenshot
                        
                        browser.close()
        except Exception as e:
            logger.error(f"Fehler beim Extrahieren des Cover-Bildes aus der Detailseite: {str(e)}")

    # Fallback to previous methods if FlareSolverr fails
    # Zuerst mit normalen HTTP-Anfragen versuchen
    try:
        logger.info(f"Lade Bild herunter (Methode 1 - Requests): {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Referer': 'https://www.anime-loads.org/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
        }
        
        session = requests.Session()
        # Zuerst die Hauptseite besuchen, um Cookies zu erhalten
        session.get('https://www.anime-loads.org/', headers=headers, timeout=15)
        
        # Dann das Bild anfordern
        response = session.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            logger.info(f"Bild erfolgreich heruntergeladen: {len(response.content)} Bytes")
            return response.content
        else:
            logger.warning(f"Konnte Bild nicht mit Requests herunterladen: Status {response.status_code}")
    except Exception as e:
        logger.warning(f"Fehler bei Methode 1: {e}")
    
    # Wenn das fehlschlägt, versuche es mit Playwright
    try:
        logger.info(f"Lade Bild herunter (Methode 2 - Playwright): {url}")
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
            )
            page = context.new_page()
            
            # Besuche die Hauptseite
            page.goto('https://www.anime-loads.org/', wait_until='domcontentloaded', timeout=30000)
            
            # Klicke den Cookie-Banner weg, falls vorhanden
            try:
                page.click('button.btn-primary', timeout=5000)
                logger.info("Clicked on cookie consent using selector: button.btn-primary")
            except Exception:
                pass  # Ignoriere Fehler, wenn der Banner nicht existiert
            
            # Lade das Bild herunter
            response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            if response and response.status == 200:
                # Verwende Playwright, um den Binärinhalt zu erhalten
                image_data = page.content()  # Dies ist nicht der richtige Ansatz für Bilder
                
                # Alternative Methode: Screenshot der Seite machen (funktioniert, aber nicht optimal)
                buffer = page.screenshot(full_page=True)
                
                browser.close()
                logger.info(f"Bild erfolgreich mit Playwright heruntergeladen")
                return buffer  # Verwende das Screenshot als Fallback
            
            browser.close()
            logger.warning(f"Konnte Bild nicht mit Playwright herunterladen")
    except Exception as e:
        logger.error(f"Fehler bei Methode 2: {e}")
    
    # Letzte Chance: Erstelle einen Screenshot des Bildes
    try:
        logger.info(f"Lade Bild herunter (Methode 3 - Screenshot): {url}")
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
            )
            
            page = context.new_page()
            
            # Setze die Viewport-Größe groß genug für das Bild
            page.set_viewport_size({"width": 1280, "height": 1024})
            
            # Besuche die Hauptseite und akzeptiere Cookies
            page.goto('https://www.anime-loads.org/', wait_until='domcontentloaded', timeout=30000)
            
            # Klicke den Cookie-Banner weg, falls vorhanden
            try:
                page.click('button.btn-primary', timeout=5000)
                logger.info("Clicked on cookie consent using selector: button.btn-primary")
            except Exception:
                pass
            
            # Besuche die Bildseite
            response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            if response and response.status == 200:
                # Mache einen Screenshot des Bildes
                logger.info("Bild erfolgreich geladen, erstelle Screenshot")
                screenshot = page.screenshot(full_page=True)
                browser.close()
                logger.info(f"Bild erfolgreich per Screenshot erfasst: {len(screenshot)} Bytes")
                return screenshot
            else:
                browser.close()
                logger.warning(f"Konnte Bild nicht laden: Status {response.status if response else 'unbekannt'}")
    except Exception as e:
        logger.error(f"Fehler bei Methode 3: {e}")
    
    # Fallback: Verwende ein lokales Standardbild als Platzhalter
    try:
        logger.warning(f"Alle Methoden zum Herunterladen des Bildes fehlgeschlagen, verwende Platzhalter")
        placeholder_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "placeholder.jpg")
        if os.path.exists(placeholder_path):
            with open(placeholder_path, "rb") as f:
                placeholder_data = f.read()
                logger.info(f"Verwende Platzhalter-Bild: {len(placeholder_data)} Bytes")
                return placeholder_data
    except Exception as e:
        logger.error(f"Fehler beim Lesen des Platzhalter-Bildes: {e}")
    
    logger.error(f"Alle Methoden zum Herunterladen des Bildes von {url} sind fehlgeschlagen")
    return None

def extract_anime_info(soup: BeautifulSoup, url: str, skip_cover_download: bool = False) -> Dict[str, Any]:
    """
    Extrahiert Anime-Informationen aus einem BeautifulSoup-Objekt.
    
    Args:
        soup: BeautifulSoup-Objekt mit dem HTML-Inhalt
        url: Original-URL der Anime-Seite
        skip_cover_download: Wenn True, wird der Cover-Download übersprungen
        
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
        cover_url = None
        cover_image_data = None
        
        # 1. Versuche, das Cover-Bild aus dem OpenGraph-Tag zu extrahieren
        og_image = soup.select_one('meta[property="og:image"]')
        if og_image and og_image.get('content'):
            cover_url = og_image.get('content')
            logger.info(f"Cover-Bild gefunden mit Selektor 'meta[property=\"og:image\"]': {cover_url}")
        else:
            # 2. Versuche, ein Bild innerhalb der Anime-Detailseite zu finden
            img_selectors = [
                'img.cover',
                '.anime-cover img',
                '.anime-image img',
                '.anime-detail-cover img',
                '.anime-header img'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    cover_url = img.get('src')
                    logger.info(f"Cover-Bild gefunden mit Selektor '{selector}': {cover_url}")
                    break
        
        # Stelle sicher, dass wir eine absolute URL haben
        if cover_url and not cover_url.startswith(('http://', 'https://')):
            cover_url = urljoin(BASE_URL, cover_url)
        
        # Lade das Cover-Bild herunter, wenn eine URL gefunden wurde und das Überspringen nicht aktiviert ist
        if cover_url and not skip_cover_download:
            cover_image_data = download_image(cover_url)
        
        anime_info["cover_image"] = cover_url
        anime_info["cover_image_data"] = cover_image_data
        
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
    
    Berücksichtigt verschiedene Quellen (Releases) für dieselben Episoden und
    gruppiert sie anhand ihrer Episodennummern, um Duplikate zu vermeiden.
    Extrahiert die Source-Links im Format anime-loads.org/media/anime#downloads_episodes_X_cnl
    
    Args:
        soup: BeautifulSoup-Objekt der Anime-Detailseite
        
    Returns:
        Liste von Episoden-Dictionaries mit einzigartigen Episoden
    """
    episoden_dict = {}  # Dictionary zur Gruppierung von Episoden nach Nummer
    
    try:
        # 1. Identifiziere die Release-Quellen 
        releases = {}  # Dictionary mit Release-ID -> Release-Infos
        
        # Finde alle Download-Tabs (die verschiedenen Releases)
        download_tabs = soup.select('div.download, div#downloads div[id^="download_"]')
        
        for tab in download_tabs:
            release_id = None
            release_name = "Unbekanntes Release"
            
            # Versuche, die Release-ID zu extrahieren
            if tab.get('id') and tab.get('id').startswith('download_'):
                try:
                    release_id = tab.get('id').replace('download_', '')
                    release_id = int(release_id)
                except ValueError:
                    pass
            
            # Versuche, den Release-Namen zu extrahieren
            title_elem = tab.select_one('h3, h4, div.title, span.title')
            if title_elem and title_elem.text.strip():
                release_name = title_elem.text.strip()
            
            if release_id:
                releases[release_id] = {
                    'name': release_name,
                    'id': release_id
                }
                logger.info(f"Release-Quelle gefunden: {release_name} (ID: {release_id})")
        
        logger.info(f"Insgesamt {len(releases)} Release-Quellen gefunden")
        
        # 2. Extrahiere direkt den Episode-Downloads-Link für jede Quelle/Episode
        # Suche nach Links im Format #downloads_episodes_X_Y
        source_episode_links = {}
        
        # Zuerst suchen wir gezielt nach den episode_downloads Links
        for release_id in releases.keys():
            # Suche nach spezifischen Links für jede Release-Quelle
            episode_containers = soup.select(f'div#downloads_episodes_{release_id}_0, div[data-source="{release_id}"]')
            
            if episode_containers:
                logger.info(f"Episoden-Container für Release {release_id} gefunden: {len(episode_containers)}")
                
                # Extrahiere die Links zu den einzelnen Episoden
                for container in episode_containers:
                    episode_links = container.select('a')
                    
                    for link in episode_links:
                        link_text = link.text.strip()
                        
                        # Versuche, die Episodennummer zu extrahieren
                        episode_number = None
                        
                        # Regex-Muster zur Extraktion von Episodennummern
                        ep_number_patterns = [
                            r'episode[_-]?(\d+)',  # episode1, episode-1, episode_1
                            r'ep[_-]?(\d+)',       # ep1, ep-1, ep_1
                            r'folge[_-]?(\d+)',    # folge1, folge-1, folge_1
                            r'[^a-zA-Z](\d+)[^a-zA-Z]',  # isolierte Zahl
                            r'Episode\s+(\d+)',    # "Episode 1"
                            r'Folge\s+(\d+)',      # "Folge 1"
                            r'Ep\.\s*(\d+)',       # "Ep. 1"
                            r'#(\d+)',             # "#1"
                        ]
                        
                        # Suche nach Episodennummer in Text oder URL
                        for pattern in ep_number_patterns:
                            if not episode_number:  # Sobald eine Nummer gefunden wurde, aufhören
                                matches = re.search(pattern, link_text, re.IGNORECASE)
                                if matches:
                                    try:
                                        episode_number = int(matches.group(1))
                                        break
                                    except (ValueError, IndexError):
                                        continue
                        
                        # Extrahiere direkt die Episodennummer vom Anfang des Textes (z.B. "1 Solo Leveling")
                        if not episode_number and link_text:
                            # Versuche, die echte Episodennummer zu extrahieren
                            number_matches = re.match(r'^(\d+)', link_text.strip())
                            if number_matches:
                                try:
                                    episode_number = int(number_matches.group(1))
                                    logger.debug(f"Echte Episodennummer vom Anfang des Texts extrahiert: {episode_number} (aus '{link_text}')")
                                except (ValueError, IndexError):
                                    pass
                        
                        if not episode_number:
                            logger.warning(f"Konnte keine Episodennummer extrahieren: {link_text}")
                            continue
                        
                        # Konstruiere den Source-Link direkt
                        anime_url = soup.select_one('meta[property="og:url"]')
                        base_url = anime_url.get('content') if anime_url else ''
                        
                        if not base_url:
                            # Versuche, die URL aus dem head > link[rel="canonical"] zu extrahieren
                            canonical = soup.select_one('link[rel="canonical"]')
                            if canonical and canonical.get('href'):
                                base_url = canonical.get('href')
                        
                        # Wenn immer noch keine URL, verwende die aktuelle URL ohne Anker
                        if not base_url:
                            base_url = re.sub(r'#.*$', '', link.get('href', ''))
                        
                        # Konstruiere den Source-Link
                        source_link = f"{base_url}#downloads_episodes_{release_id}_cnl"
                        
                        # Extrahiere die eigentliche Episodennummer aus dem Text
                        # Bisher nur das "1" aus "1 Solo Leveling: Wie man stärker wird"
                        matched_episode_number = None
                        if link_text:
                            # Versuche, die echte Episodennummer zu extrahieren
                            number_matches = re.match(r'^(\d+)', link_text.strip())
                            if number_matches:
                                try:
                                    matched_episode_number = int(number_matches.group(1))
                                    logger.debug(f"Echte Episodennummer aus Text extrahiert: {matched_episode_number} (aus '{link_text}')")
                                except (ValueError, IndexError):
                                    pass
                        
                        # Wenn eine echte Episodennummer gefunden wurde, verwende diese statt der erkannten Nummer
                        if matched_episode_number is not None:
                            episode_number = matched_episode_number
                        
                        # Speichere den Source-Link für diese Episode und Quelle
                        if episode_number not in source_episode_links:
                            source_episode_links[episode_number] = {}
                        
                        source_episode_links[episode_number][release_id] = {
                            'source_link': source_link,
                            'release_name': releases[release_id]['name'],
                            'title': link_text
                        }
                        
                        logger.debug(f"Source-Link für Episode {episode_number}, Release {release_id}: {source_link}")
        
        # 3. Erstelle nun die einzigartigen Episode-Einträge mit allen Quellen
        for episode_number, sources in source_episode_links.items():
            episode_title = f"Episode {episode_number}"
            
            # Finde den besten Titel (den längsten oder informativsten)
            for source_id, source_info in sources.items():
                current_title = source_info['title']
                if len(current_title) > len(episode_title) and not current_title.startswith(("Episode", "Folge")):
                    episode_title = current_title
            
            # Sammle alle Source-Links für diese Episode
            episode_urls = [source_info['source_link'] for source_id, source_info in sources.items()]
            
            # Erstelle den Episoden-Eintrag
            episoden_dict[episode_number] = {
                'number': episode_number,
                'title': episode_title,
                'urls': episode_urls,
                'anime_loads_episode_url': episode_urls[0] if episode_urls else "",  # Erste URL als Haupt-URL
                'status': "missing",  # Nach Vorgabe
                'air_date': None      # Könnte in Zukunft extrahiert werden
            }
        
        # Fallback: Wenn keine Episoden gefunden wurden, verwende den alten Algorithmus
        if not episoden_dict:
            logger.warning("Keine Episoden über Release-Quellen gefunden, verwende Fallback-Methode...")
            
            # Extrahiere alle Episoden-Links direkt von der Seite
            episode_links = soup.select('div.episodes a, a.episode, div.download-links a, div.downloads a')
            
            if not episode_links:
                logger.warning("Keine Episoden-Links gefunden, versuche alternativ...")
                episode_links = soup.select('a[href*="episode"], a[href*="ep-"]')
            
            logger.info(f"Insgesamt {len(episode_links)} Episoden-Links gefunden")
            
            # Regex-Muster zur Extraktion von Episodennummern
            ep_number_patterns = [
                r'episode[_-]?(\d+)',  # episode1, episode-1, episode_1
                r'ep[_-]?(\d+)',       # ep1, ep-1, ep_1
                r'folge[_-]?(\d+)',    # folge1, folge-1, folge_1
                r'[^a-zA-Z](\d+)[^a-zA-Z]',  # isolierte Zahl
                r'Episode\s+(\d+)',    # "Episode 1"
                r'Folge\s+(\d+)',      # "Folge 1"
                r'Ep\.\s*(\d+)',       # "Ep. 1"
                r'#(\d+)',             # "#1"
            ]
            
            # Analysiere jeden Link
            for link in episode_links:
                link_text = link.text.strip()
                link_url = link.get('href', '')
                
                # Standardwerte für diesen Link
                detected_number = None
                episode_title = link_text if link_text else "Ohne Titel"
                
                # 1. Versuche, Episodennummer aus dem Text zu extrahieren
                for pattern in ep_number_patterns:
                    if not detected_number:  # Sobald eine Nummer gefunden wurde, aufhören
                        matches = re.search(pattern, link_text, re.IGNORECASE)
                        if matches:
                            try:
                                detected_number = int(matches.group(1))
                                logger.debug(f"Nummer {detected_number} aus Text extrahiert mit Muster '{pattern}': {link_text}")
                                break
                            except (ValueError, IndexError):
                                continue
                
                # Extrahiere direkt die Episodennummer vom Anfang des Textes (z.B. "1 Solo Leveling")
                if not detected_number and link_text:
                    # Versuche, die echte Episodennummer zu extrahieren
                    number_matches = re.match(r'^(\d+)', link_text.strip())
                    if number_matches:
                        try:
                            detected_number = int(number_matches.group(1))
                            logger.debug(f"Echte Episodennummer vom Anfang des Texts extrahiert: {detected_number} (aus '{link_text}')")
                        except (ValueError, IndexError):
                            pass
                
                # 2. Versuche, Episodennummer aus der URL zu extrahieren, falls nicht im Text gefunden
                if not detected_number and link_url:
                    for pattern in ep_number_patterns:
                        matches = re.search(pattern, link_url, re.IGNORECASE)
                        if matches:
                            try:
                                detected_number = int(matches.group(1))
                                logger.debug(f"Nummer {detected_number} aus URL extrahiert mit Muster '{pattern}': {link_url}")
                                break
                            except (ValueError, IndexError):
                                continue
                
                # 3. Fallback: Wenn keine Nummer gefunden wurde, verwende Position im Array
                if not detected_number:
                    # Letzte Möglichkeit: Suche nach jeder Zahl im Text
                    all_numbers = re.findall(r'\d+', link_text)
                    if all_numbers and 1 <= int(all_numbers[0]) <= 100:  # Sinnvolle Grenzen für Episodennummern
                        detected_number = int(all_numbers[0])
                        logger.debug(f"Nummer {detected_number} als Fallback extrahiert: {link_text}")
                
                # Wenn immer noch keine Nummer gefunden wurde, überspringen
                if not detected_number:
                    logger.warning(f"Konnte keine Episodennummer für Link extrahieren: {link_text} / {link_url}")
                    continue
                
                # Normalisiere URL zu absoluter Form
                absolute_url = link_url
                if link_url and not link_url.startswith(('http://', 'https://')):
                    absolute_url = urljoin(BASE_URL, link_url)
                
                # Prüfe, ob diese Episode bereits existiert
                if detected_number in episoden_dict:
                    # Hinzufügen der neuen Quelle zur bestehenden Episode
                    if absolute_url and absolute_url not in episoden_dict[detected_number]['urls']:
                        episoden_dict[detected_number]['urls'].append(absolute_url)
                        logger.debug(f"Neue Quelle für Episode {detected_number} hinzugefügt: {absolute_url}")
                    
                    # Möglicherweise besserer Titel gefunden?
                    current_title = episoden_dict[detected_number]['title']
                    if (len(episode_title) > len(current_title) and 
                        not current_title.startswith("Episode") and 
                        not current_title.startswith("Folge")):
                        episoden_dict[detected_number]['title'] = episode_title
                        logger.debug(f"Besserer Titel für Episode {detected_number} gefunden: {episode_title}")
                else:
                    # Neue Episode erstellen
                    episoden_dict[detected_number] = {
                        'number': detected_number,
                        'title': episode_title,
                        'urls': [absolute_url] if absolute_url else [],
                        'anime_loads_episode_url': absolute_url,  # Erste URL als Haupt-URL
                        'status': "missing",  # Nach Vorgabe
                        'air_date': None      # Könnte in Zukunft extrahiert werden
                    }
                    logger.debug(f"Neue einzigartige Episode gefunden: {detected_number} - {episode_title}")
    
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren der Episodenliste: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # Konvertiere das Dictionary in eine sortierte Liste
    episodes = [episoden_dict[key] for key in sorted(episoden_dict.keys())]
    logger.info(f"Insgesamt {len(episodes)} einzigartige Episoden gefunden (aus allen Quellen)")
    
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
