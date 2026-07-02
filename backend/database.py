import sqlite3
from pathlib import Path

# Die Datenbankdatei legen wir neben diese Datei in den backend-Ordner.
DB_PFAD = Path(__file__).parent / "buchungen.db"

"""Legt die Tabelle an, aber nur, falls sie noch nicht existiert."""
def init_db():
    with sqlite3.connect(DB_PFAD) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buchungen (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                datum        TEXT NOT NULL,
                betrag       REAL NOT NULL,
                kategorie    TEXT NOT NULL,
                typ          TEXT NOT NULL,
                beschreibung TEXT,
                konto        TEXT NOT NULL,
                partner      TEXT,
                kostenstelle TEXT,
                bezahlt      INTEGER NOT NULL DEFAULT 1
            )
        """)

"""Speichert eine Buchung und gibt die neu vergebene id zurück."""
def buchung_einfuegen(datum, betrag, kategorie, typ, beschreibung, konto, partner="", kostenstelle="", bezahlt=True):
    with sqlite3.connect(DB_PFAD) as conn:
        cursor = conn.execute(
            """INSERT INTO buchungen (datum, betrag, kategorie, typ, beschreibung, konto, partner, kostenstelle, bezahlt)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (datum, betrag, kategorie, typ, beschreibung, konto, partner, kostenstelle, int(bezahlt)),
        )
        return cursor.lastrowid

"""Liest alle Buchungen als Liste von Dicts (sortiert nach Datum)."""
def alle_buchungen():
    with sqlite3.connect(DB_PFAD) as conn:
        conn.row_factory = sqlite3.Row  # Zugriff per Spaltenname statt Index
        rows = conn.execute("SELECT * FROM buchungen ORDER BY datum").fetchall()
        return [dict(row) for row in rows]


# ---------------------------------------------------------------
# NEU: Buchung ändern und löschen
# ---------------------------------------------------------------

"""Ändert eine bestehende Buchung. Gibt True zurück, wenn wirklich eine Zeile geändert wurde."""
def buchung_aktualisieren(id, datum, betrag, kategorie, typ, beschreibung, konto, partner="", kostenstelle="", bezahlt=True):
    with sqlite3.connect(DB_PFAD) as conn:
        cursor = conn.execute(
            """UPDATE buchungen
               SET datum=?, betrag=?, kategorie=?, typ=?, beschreibung=?, konto=?, partner=?, kostenstelle=?, bezahlt=?
               WHERE id=?""",
            (datum, betrag, kategorie, typ, beschreibung, konto, partner, kostenstelle, int(bezahlt), id),
        )
        # rowcount = Anzahl geänderter Zeilen. 0 heißt: diese id gab es gar nicht.
        return cursor.rowcount > 0

"""Löscht eine Buchung anhand ihrer id. Gibt True zurück, wenn etwas gelöscht wurde."""
def buchung_loeschen(id):
    with sqlite3.connect(DB_PFAD) as conn:
        cursor = conn.execute("DELETE FROM buchungen WHERE id=?", (id,))
        return cursor.rowcount > 0


# Kleiner Selbsttest: nur, wenn man diese Datei direkt ausführt.
if __name__ == "__main__":
    init_db()
    neue_id = buchung_einfuegen("2026-06-09", 1500.0, "Umsatz", "Einnahme", "Testbuchung", "Bank")
    print(f"Buchung mit id {neue_id} gespeichert.")
    print(alle_buchungen())
