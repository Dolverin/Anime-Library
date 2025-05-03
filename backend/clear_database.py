#!/usr/bin/env python3
import sys
import mysql.connector
from app.config import settings

def clear_database():
    """
    Leert alle Tabellen in der Anime-Library-Datenbank durch direkte
    Verwendung von MySQL-Connector. 
    """
    # Datenbankverbindung aus settings.database_url extrahieren
    db_url = settings.database_url.replace('mysql+mysqlconnector://', '')
    auth, db_info = db_url.split('@')
    username, password = auth.split(':')
    host_port, db_name = db_info.split('/')
    
    if ':' in host_port:
        host, port = host_port.split(':')
        port = int(port)
    else:
        host = host_port
        port = 3306
    
    print(f"Verbinde mit Datenbank {db_name} auf {host}:{port}...")
    
    # Verbindung zur Datenbank herstellen
    try:
        connection = mysql.connector.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            database=db_name
        )
        cursor = connection.cursor()
        
        # Liste aller Tabellen in der Datenbank abrufen
        print("Rufe Tabellenliste ab...")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if not tables:
            print("Keine Tabellen gefunden.")
            cursor.close()
            connection.close()
            return
        
        print(f"Gefundene Tabellen: {', '.join(tables)}")
        
        # Foreign Key Checks deaktivieren
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Jede Tabelle leeren
        for table in tables:
            print(f"Leere Tabelle {table}...")
            cursor.execute(f"TRUNCATE TABLE `{table}`")
        
        # Foreign Key Checks wieder aktivieren
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Änderungen übernehmen
        connection.commit()
        
        cursor.close()
        connection.close()
        
        print("✅ Datenbankeinträge erfolgreich bereinigt.")
    except mysql.connector.Error as err:
        print(f"❌ Fehler beim Bereinigen der Datenbank: {err}")
        sys.exit(1)

if __name__ == "__main__":
    clear_database()
    sys.exit(0)
