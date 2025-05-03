#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Direktes Einfügen von Solo Leveling in die Datenbank als Testdatensatz.
"""
import os
import sys
from datetime import datetime

# SQLAlchemy und Datenbankmodelle importieren
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Anime, Episode, AnimeStatus, EpisodeStatus, EpisodeAvailabilityStatus

def add_solo_leveling():
    """
    Fügt Solo Leveling als vollständigen Anime mit allen Episoden in die Datenbank ein.
    Berücksichtigt sowohl die online-Verfügbarkeit als auch lokale Dateien.
    """
    print("Füge Solo Leveling zur Datenbank hinzu...")
    
    db = SessionLocal()
    
    try:
        # Prüfen, ob der Anime bereits existiert
        existing_anime = db.query(Anime).filter(Anime.titel_de == "Solo Leveling").first()
        
        if existing_anime:
            print(f"Solo Leveling existiert bereits in der Datenbank (ID: {existing_anime.id})")
            return existing_anime.id
            
        # Anime-Eintrag erstellen
        anime = Anime(
            titel_de="Solo Leveling",
            titel_en="Solo Leveling",
            titel_jp="Solo Leveling",
            titel_org="나 혼자만 레벨업",
            synonyme="I Level Up Alone;Only I Level Up",
            status=AnimeStatus.watching,
            beschreibung="In einer Welt, in der Jäger mit übernatürlichen Fähigkeiten gegen Monster kämpfen, gilt Sung Jin-Woo als der schwächste aller Jäger. Nach einer schicksalhaften Begegnung in einem gefährlichen Dungeon erhält er die mysteriöse Fähigkeit, als Spieler zu leveln – eine Kraft, die es ihm ermöglicht, sein volles Potenzial zu entfalten.",
            anime_loads_url="https://www.anime-loads.org/media/solo-leveling",
            cover_image_url="https://cdn.myanimelist.net/images/anime/1170/138773.jpg",
            typ="Serie",
            jahr=2024,
            episoden_anzahl="12",
            hauptgenre="Action",
            nebengenres="Fantasy,Abenteuer,Übernatürlich",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(anime)
        db.flush()  # Um die ID zu generieren
        
        print(f"Anime 'Solo Leveling' erstellt mit ID {anime.id}")
        
        # Episoden erstellen - Solo Leveling hat 12 Episoden in Staffel 1
        episodes = []
        
        # Episodentitel für Solo Leveling (Staffel 1)
        episode_titles = [
            "Ich bin ein Jäger",
            "Ein E-Rang-Jäger",
            "Eine Einladung zu einem Dungeon",
            "Das Wahre Erwachen",
            "Der Stärkste Jäger",
            "Ich habe dich nicht gesehen, seit du gestorben bist",
            "Wer hat mich gerufen?",
            "Du hast alles getan, was du konntest",
            "Die wahre Identität von Kamish",
            "Ich habe nicht vor, dich hier zu lassen",
            "Die Rückkehr des Königs",
            "Ich bin nicht mehr derselbe wie früher"
        ]
        
        # Füge Episoden hinzu
        for i in range(1, 13):
            titel = episode_titles[i-1] if i <= len(episode_titles) else f"Episode {i}"
            
            # Jede Episode ist sowohl online als auch lokal verfügbar
            episode = Episode(
                anime_id=anime.id,
                episoden_nummer=i,
                titel=titel,
                status=EpisodeStatus.watched,  # Alle Episoden als gesehen markieren
                availability_status=EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE,
                stream_link=f"https://www.anime-loads.org/media/solo-leveling/episode-{i}",
                local_path=f"/pfad/zu/Solo_Leveling/Episode_{i:02d}.mp4"
            )
            
            episodes.append(episode)
            
        # Alle Episoden zur Datenbank hinzufügen
        db.add_all(episodes)
        db.commit()
        
        print(f"12 Episoden für Solo Leveling hinzugefügt")
        
        return anime.id
        
    except Exception as e:
        db.rollback()
        print(f"Fehler beim Hinzufügen von Solo Leveling: {str(e)}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    anime_id = add_solo_leveling()
    
    if anime_id:
        print(f"✅ Solo Leveling erfolgreich zur Datenbank hinzugefügt (ID: {anime_id})")
        sys.exit(0)
    else:
        print("❌ Fehler beim Hinzufügen von Solo Leveling")
        sys.exit(1)
