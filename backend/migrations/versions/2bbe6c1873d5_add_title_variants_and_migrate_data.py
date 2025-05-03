"""add_title_variants_and_migrate_data

Revision ID: 2bbe6c1873d5
Revises: 1d6d11d0ccc6
Create Date: 2025-05-03 21:31:49.706307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '2bbe6c1873d5'
down_revision: Union[str, None] = '1d6d11d0ccc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Hilfsfunktionen für die Datenmigration
def migrate_anime_titles(connection):
    """Migriert bestehende Anime-Titel in die neuen Spalten."""
    # Alle bestehenden Anime-Daten abrufen
    anime_records = connection.execute(text("SELECT id, titel, original_titel, synonyme FROM animes")).fetchall()
    
    print(f"Migriere Titeldaten für {len(anime_records)} Anime-Einträge...")
    
    for anime in anime_records:
        # Grundlegende Werte aus den bestehenden Feldern extrahieren
        anime_id = anime[0]
        titel = anime[1] or "Unbekannt"
        original_titel = anime[2] or ""
        
        # Standardwerte für die neuen Spalten
        titel_de = titel
        titel_jp = ""
        titel_org = original_titel
        titel_en = ""
        
        # Heuristik anwenden:
        # 1. Wenn der Titel keine deutschen Umlaute enthält, ist er möglicherweise englisch
        if not any(c in titel for c in "äöüÄÖÜß") and titel != "Unbekannt":
            titel_en = titel
        
        # 2. Wenn der Originaltitel japanische Schriftzeichen (über ASCII-Bereich) enthält, dann ist es der "titel_org"
        if original_titel and any(ord(c) > 127 for c in original_titel):
            titel_org = original_titel
            # Versuchen, die Romanisierung aus dem Titel zu extrahieren, wenn vorhanden
            if not any(c in titel for c in "äöüÄÖÜß") and titel != titel_org:
                titel_jp = titel
                # Wenn kein deutscher Titel vorhanden ist, diesen neu setzen
                if titel_de == titel_jp:
                    titel_de = "Unbekannt"
        
        # Update der Datenbank mit den neuen Werten
        update_query = text("""
            UPDATE animes 
            SET titel_de = :titel_de, titel_jp = :titel_jp, titel_org = :titel_org, titel_en = :titel_en 
            WHERE id = :anime_id
        """)
        connection.execute(
            update_query, 
            {"titel_de": titel_de, "titel_jp": titel_jp, "titel_org": titel_org, "titel_en": titel_en, "anime_id": anime_id}
        )
    
    print("Titelmigration abgeschlossen.")

def upgrade() -> None:
    """Upgrade schema."""
    # 1. Neue Spalten hinzufügen mit NULL-Constraint
    op.add_column('animes', sa.Column('titel_de', sa.String(length=255), nullable=True))
    op.add_column('animes', sa.Column('titel_jp', sa.String(length=255), nullable=True))
    op.add_column('animes', sa.Column('titel_org', sa.String(length=255), nullable=True))
    op.add_column('animes', sa.Column('titel_en', sa.String(length=255), nullable=True))
    
    # 2. Daten aus alten in neue Spalten übertragen
    conn = op.get_bind()
    migrate_anime_titles(conn)
    
    # 3. NOT NULL-Constraint für titel_de setzen (nach der Datenmigration)
    # MySQL erlaubt keine direkte Änderung von NULL zu NOT NULL, also müssen wir die Spalte ändern
    op.alter_column('animes', 'titel_de', existing_type=sa.String(length=255), nullable=False)
    
    # 4. Alte Spalten entfernen
    op.drop_column('animes', 'titel')
    op.drop_column('animes', 'original_titel')
    
    print("Upgrade abgeschlossen")


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Alte Spalten wieder hinzufügen
    op.add_column('animes', sa.Column('original_titel', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255), nullable=True))
    op.add_column('animes', sa.Column('titel', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255), nullable=True))
    
    # 2. Daten aus neuen in alte Spalten zurück kopieren
    conn = op.get_bind()
    conn.execute(text("""
        UPDATE animes 
        SET titel = titel_de, 
            original_titel = CASE 
                WHEN titel_org != '' THEN titel_org 
                WHEN titel_jp != '' THEN titel_jp 
                ELSE NULL 
            END
    """))
    
    # 3. NOT NULL-Constraint für titel setzen
    op.alter_column('animes', 'titel', existing_type=sa.String(length=255), nullable=False)
    
    # 4. Neue Spalten entfernen
    op.drop_column('animes', 'titel_en')
    op.drop_column('animes', 'titel_org')
    op.drop_column('animes', 'titel_jp')
    op.drop_column('animes', 'titel_de')
    
    print("Downgrade abgeschlossen")
