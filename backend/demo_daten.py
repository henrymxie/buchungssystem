import random                                   # zufällige Auswahl und Beträge
from datetime import date, timedelta            # zufällige Buchungsdaten
from decimal import Decimal, ROUND_HALF_UP      # saubere Cent-Beträge


def _dec(x):
    """Rundet kaufmännisch auf zwei Nachkommastellen."""
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


KUNDEN = [
    "Alpha GmbH", "Beta Solutions", "City Bakery", "Delta Studio", "Eco Store",
    "Futura Labs", "Green Office", "Havel Hotel", "Innotech AG", "Juno Media",
]

LIEFERANTEN = [
    "Adobe", "AWS", "Deutsche Bahn", "CoWorking Berlin", "Meta Ads",
    "Microsoft", "Notebookshop", "Office Depot", "Telekom", "Travel Partner",
]

EINNAHME_VORLAGEN = [
    {"kategorie": "Dienstleistungen", "text": "Webprojekt",    "bereich": (800, 4500), "konto": "Bank",  "kostenstelle": "Beratung"},
    {"kategorie": "Produktverkauf",   "text": "Softwarelizenz", "bereich": (150, 1800), "konto": "Bank",  "kostenstelle": "IT"},
    {"kategorie": "Sonstiges",        "text": "Workshop",       "bereich": (250, 2200), "konto": "Kasse", "kostenstelle": "Schulung"},
]

AUSGABE_VORLAGEN = [
    {"kategorie": "Wareneinsatz", "text": "Wareneinkauf",   "bereich": (120, 2200), "konto": "Verbindlichkeit", "kostenstelle": "Betrieb"},
    {"kategorie": "Marketing",    "text": "Onlinekampagne", "bereich": (80, 900),   "konto": "Bank",            "kostenstelle": "Marketing"},
    {"kategorie": "Software",     "text": "SaaS Abo",       "bereich": (20, 300),   "konto": "Bank",            "kostenstelle": "IT"},
    {"kategorie": "Miete",        "text": "Büro Miete",     "bereich": (900, 1400), "konto": "Bank",            "kostenstelle": "Verwaltung"},
    {"kategorie": "Reisekosten",  "text": "Dienstreise",    "bereich": (40, 350),   "konto": "Kasse",           "kostenstelle": "Vertrieb"},
]


def generiere_demo_buchungen(anzahl=150, jahr=2025):
    """Erzeugt eine Liste von Demo-Buchungen passend zu unserem Datenmodell."""
    random.seed(42)  # gleicher Seed -> immer dieselben Daten (reproduzierbar)
    start = date(jahr, 1, 1)
    ende = date(jahr, 12, 31)
    tage_spanne = (ende - start).days
    buchungen = []

    for _ in range(anzahl):
        ist_einnahme = random.random() < 0.45
        vorlage = random.choice(EINNAHME_VORLAGEN if ist_einnahme else AUSGABE_VORLAGEN)
        partner = random.choice(KUNDEN if ist_einnahme else LIEFERANTEN)

        buchungen.append({
            "datum": (start + timedelta(days=random.randint(0, tage_spanne))).isoformat(),
            "betrag": _dec(random.uniform(*vorlage["bereich"])),
            "kategorie": vorlage["kategorie"],
            "typ": "Einnahme" if ist_einnahme else "Ausgabe",
            "beschreibung": f"{vorlage['text']} – {partner}",
            "konto": vorlage["konto"],
            "partner": partner,
            "kostenstelle": vorlage["kostenstelle"],
            "bezahlt": random.random() < 0.78,   # ~22 % bleiben offen -> für offene Posten
        })

    return buchungen