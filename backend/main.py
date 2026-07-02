from fastapi import FastAPI, HTTPException
from backend.models import Buchung, BuchungCreate, GuVErgebnis, ForecastErgebnis, BilanzErgebnis, MonatsWert, CashflowWert, TopPartnerErgebnis, OffenePostenErgebnis, LoginDaten, LoginErgebnis
from backend import database, auswertung
from backend.demo_daten import generiere_demo_buchungen   # NEU
from backend.config import settings

app = FastAPI(title="Buchungssystem API")

# Beim Start sicherstellen, dass die Tabelle existiert.
database.init_db()


# Für die öffentliche Demo: falls aktiviert und die DB leer ist, einmal Demo-Daten einspielen.
if settings.auto_seed and not database.alle_buchungen():
    for b in generiere_demo_buchungen():
        database.buchung_einfuegen(
            b["datum"], b["betrag"], b["kategorie"], b["typ"],
            b["beschreibung"], b["konto"], b["partner"], b["kostenstelle"], b["bezahlt"],
        )

@app.post("/login", response_model=LoginErgebnis)
def login(daten: LoginDaten):
    """Prüft Benutzername + Passwort gegen die Werte aus der Konfiguration."""
    if daten.benutzername == settings.admin_username and daten.passwort == settings.admin_password:
        return LoginErgebnis(erfolg=True, rolle="Admin")
    if daten.benutzername == settings.user_username and daten.passwort == settings.user_password:
        return LoginErgebnis(erfolg=True, rolle="User")
    return LoginErgebnis(erfolg=False, rolle=None)

@app.get("/buchungen", response_model=list[Buchung])
def buchungen_abrufen():
    """Gibt alle gespeicherten Buchungen zurück."""
    return database.alle_buchungen()


@app.post("/buchungen", response_model=Buchung)
def buchung_anlegen(buchung: BuchungCreate):
    """Legt eine neue Buchung an und gibt sie inkl. vergebener id zurück."""
    neue_id = database.buchung_einfuegen(
        buchung.datum.isoformat(),   # date -> Text "2026-06-09" für SQLite
        buchung.betrag,
        buchung.kategorie,
        buchung.typ.value,           # Enum -> reiner String "Einnahme"
        buchung.beschreibung,
        buchung.konto.value,         # Enum -> reiner String "Bank"
        buchung.partner,
        buchung.kostenstelle,
        buchung.bezahlt,
    )
    return Buchung(id=neue_id, **buchung.model_dump())


# ---------------------------------------------------------------
# NEU: Buchung bearbeiten (PUT) und löschen (DELETE)
# ---------------------------------------------------------------

@app.put("/buchungen/{buchung_id}", response_model=Buchung)
def buchung_bearbeiten(buchung_id: int, buchung: BuchungCreate):
    """Ändert eine bestehende Buchung. Gibt 404 zurück, wenn die id nicht existiert."""
    geaendert = database.buchung_aktualisieren(
        buchung_id,
        buchung.datum.isoformat(),
        buchung.betrag,
        buchung.kategorie,
        buchung.typ.value,
        buchung.beschreibung,
        buchung.konto.value,
        buchung.partner,
        buchung.kostenstelle,
        buchung.bezahlt,
    )
    if not geaendert:
        raise HTTPException(status_code=404, detail=f"Buchung {buchung_id} nicht gefunden.")
    return Buchung(id=buchung_id, **buchung.model_dump())


@app.delete("/buchungen/{buchung_id}")
def buchung_entfernen(buchung_id: int):
    """Löscht eine Buchung. Gibt 404 zurück, wenn die id nicht existiert."""
    geloescht = database.buchung_loeschen(buchung_id)
    if not geloescht:
        raise HTTPException(status_code=404, detail=f"Buchung {buchung_id} nicht gefunden.")
    return {"geloescht": buchung_id}


# NEU: Demo-Daten in die Datenbank laden (nur wenn noch leer)
@app.post("/buchungen/demo")
def demo_daten_laden():
    """Füllt die Datenbank mit Demo-Buchungen (nur wenn noch leer)."""
    if database.alle_buchungen():
        return {"eingefuegt": 0, "hinweis": "Es existieren bereits Buchungen."}
    buchungen = generiere_demo_buchungen()
    for b in buchungen:
        database.buchung_einfuegen(
            b["datum"], b["betrag"], b["kategorie"], b["typ"],
            b["beschreibung"], b["konto"],
            b["partner"], b["kostenstelle"], b["bezahlt"],
        )
    return {"eingefuegt": len(buchungen)}


@app.get("/auswertung/guv", response_model=GuVErgebnis)
def guv_abrufen(von: str | None = None, bis: str | None = None):
    """Berechnet die GuV, optional eingegrenzt auf einen Zeitraum (von/bis)."""
    buchungen = database.alle_buchungen()
    return auswertung.berechne_guv(buchungen, von, bis)


@app.get("/auswertung/forecast", response_model=ForecastErgebnis)
def forecast_abrufen():
    """Gibt eine 30-Tage-Prognose auf Basis der bisherigen Buchungen zurück."""
    buchungen = database.alle_buchungen()
    return auswertung.berechne_forecast(buchungen)


@app.get("/auswertung/bilanz", response_model=BilanzErgebnis)
def bilanz_abrufen(stichtag: str):
    """Berechnet eine Bilanz zum angegebenen Stichtag (ISO)."""
    buchungen = database.alle_buchungen()
    return auswertung.berechne_bilanz(buchungen, stichtag)


@app.get("/auswertung/monatsentwicklung", response_model=list[MonatsWert])
def monatsentwicklung_abrufen():
    """Einnahmen/Ausgaben pro Monat für die Zeitreihe."""
    return auswertung.berechne_monatsentwicklung(database.alle_buchungen())


@app.get("/auswertung/cashflow", response_model=list[CashflowWert])
def cashflow_abrufen():
    """Kumulierter Kontostand-Verlauf über die Zeit."""
    return auswertung.berechne_cashflow(database.alle_buchungen())


@app.get("/auswertung/top-partner", response_model=TopPartnerErgebnis)
def top_partner_abrufen():
    """Top-Kunden und Top-Lieferanten."""
    return auswertung.berechne_top_partner(database.alle_buchungen())


@app.get("/auswertung/offene-posten", response_model=OffenePostenErgebnis)
def offene_posten_abrufen():
    """Offene Forderungen und Verbindlichkeiten."""
    return auswertung.berechne_offene_posten(database.alle_buchungen())


@app.get("/auswertung/kostenstellen", response_model=dict[str, float])
def kostenstellen_abrufen():
    """Ausgaben je Kostenstelle."""
    return auswertung.berechne_kostenstellen(database.alle_buchungen())
