"""
Skript zum Erstellen der Datenbank anime_library auf dem MySQL-Server.
Führe dieses Skript aus, bevor du den Hauptserver startest.
"""

import mysql.connector
from mysql.connector import errorcode

# Verbindungsdaten
config = {
    'user': 'aniworld',
    'password': 'aniworld',
    'host': '192.168.178.9',
    'port': 3306,
}

# Verbindung zum MySQL-Server ohne spezifische Datenbank
try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    
    # Datenbank erstellen falls sie nicht existiert
    print("Erstelle Datenbank anime_library...")
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS anime_library "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    print("Datenbank erfolgreich erstellt!")
    
    # Überprüfen, ob die Datenbank existiert
    cursor.execute("SHOW DATABASES LIKE 'anime_library'")
    result = cursor.fetchone()
    if result:
        print("Datenbank anime_library existiert nun.")
    else:
        print("Fehler: Datenbank konnte nicht gefunden werden, obwohl sie erstellt wurde.")
    
    cursor.close()
    cnx.close()
    
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Fehler: Falsche Zugangsdaten für den MySQL-Server.")
    else:
        print(f"Fehler: {err}")
