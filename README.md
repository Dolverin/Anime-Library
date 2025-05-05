# 🎬 Anime-Library

Eine moderne Webanwendung zur Verwaltung deiner persönlichen Anime-Sammlung. Verfolge deinen Fortschritt, importiere neue Anime und behalte den Überblick über deine komplette Anime-Bibliothek.

![Anime-Library](https://img.shields.io/badge/Anime--Library-v1.0-blue)
![Python](https://img.shields.io/badge/Backend-Python%2FFastAPI-green)
![React](https://img.shields.io/badge/Frontend-React%2FTypeScript-blue)
![MySQL](https://img.shields.io/badge/Datenbank-MySQL-orange)

## 🌟 Funktionen

### 📚 Anime-Verwaltung
- **Übersichtliche Darstellung** deiner Anime-Sammlung in Karten- oder Listenansicht
- **Detaillierte Informationen** zu jedem Anime mit Beschreibung, Genres und Metadaten
- **Fortschrittsverfolgung** für alle Serien (geplant, wird angeschaut, abgeschlossen)
- **Filterung und Sortierung** nach verschiedenen Kriterien wie Genre, Jahr oder Status

### 🔍 Import und Suche
- **Automatischer Import** von Anime-Informationen von anime-loads.org
- **Leistungsstarke Suchfunktion** zum Auffinden neuer Anime
- **Hinzufügen eigener Einträge** mit benutzerdefinierten Details

### 🖼️ Episoden-Management
- **Episodenverfolgung** mit Markierung gesehener Episoden
- **Verknüpfung mit lokalen Dateien** oder Stream-Links
- **Mehrsprachige Unterstützung** für Untertitel und Audio

### 💾 Lokale Integration
- **Scannen lokaler Mediendateien** und automatische Verknüpfung mit der Datenbank
- **Verwaltung von Cover-Bildern** für visuelle Darstellung

## 🚀 Technologie-Stack

### Backend (Python/FastAPI)
- **FastAPI**: Moderne, schnelle API mit automatischer OpenAPI-Dokumentation
- **MySQL**: Robuste Datenbank zur Speicherung aller Anime-Informationen
- **Web-Scraper**: Extrahiert Daten von anime-loads.org
- **Alembic**: Datenbank-Migrations-Tool

### Frontend (React/TypeScript)
- **React**: Komponentenbasierte UI-Bibliothek
- **TypeScript**: Typsichere Entwicklung
- **Bootstrap**: Responsive Design-Komponenten
- **React Router**: Clientseitige Navigation

## 📋 Installation und Einrichtung

### Voraussetzungen
- Python 3.8+
- Node.js 14+
- MySQL 5.7+

### Backend-Installation
```bash
# Repository klonen
git clone https://github.com/username/Anime-Library.git
cd Anime-Library/backend

# Virtuelle Umgebung erstellen und aktivieren
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbank erstellen
python create_db.py

# API-Server starten
uvicorn main:app --reload
```

### Frontend-Installation
```bash
# In das Frontend-Verzeichnis wechseln
cd ../frontend

# Abhängigkeiten installieren
npm install

# Entwicklungsserver starten
npm run dev
```

## 🖥️ Nutzung

1. **Anime importieren**: Beginne mit dem Import neuer Anime über die Suchfunktion
2. **Lokale Dateien scannen**: Verbinde deine lokalen Mediendateien mit der Datenbank
3. **Fortschritt verfolgen**: Markiere Episoden als gesehen und verfolge deinen Fortschritt
4. **Bibliothek organisieren**: Nutze Filter und Tags, um deine wachsende Sammlung zu organisieren

## 🌐 Screenshots

*(Hier würden Screenshots der Anwendung eingefügt werden)*

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

## 🤝 Beitragen

Beiträge sind willkommen! Öffne ein Issue oder sende einen Pull Request, um die Anime-Library zu verbessern.

---

**Anime-Library** - Entwickelt mit ❤️ für Anime-Fans