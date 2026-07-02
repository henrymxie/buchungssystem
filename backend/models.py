from datetime import date
from enum import Enum
from pydantic import BaseModel, Field

"""Enum für die Art der Buchung. Erlaubt nur genau diese zwei Werte, alles andere lehnt Pydantic ab."""
class BuchungsTyp(str, Enum):
    einnahme = "Einnahme"
    ausgabe = "Ausgabe"

# NEU: Die Konten für die Bilanz
class KontoTyp(str, Enum):
    bank = "Bank"
    kasse = "Kasse"
    eigenkapital = "Eigenkapital"
    verbindlichkeit = "Verbindlichkeit"

"""Das schickt das Frontend ans Backend, um eine neue Buchung anzulegen. Noch ohne id, die vergibt erst die Datenbank."""
class BuchungCreate(BaseModel):
    datum: date
    betrag: float = Field(gt=0, description="Betrag in Euro, immer positiv")
    kategorie: str = Field(min_length=1)
    typ: BuchungsTyp
    beschreibung: str = ""
    konto: KontoTyp
    partner: str = ""
    kostenstelle: str = ""
    bezahlt: bool = True


"""Eine bereits gespeicherte Buchung: alles von BuchungCreate plus die id."""
class Buchung(BuchungCreate):
    id: int

class GuVErgebnis(BaseModel):
    einnahmen: float
    ausgaben: float
    gewinn: float
    einnahmen_nach_kategorie: dict[str, float]
    ausgaben_nach_kategorie: dict[str, float]

class ForecastErgebnis(BaseModel):
    erwartete_einnahmen_30_tage: float
    erwartete_ausgaben_30_tage: float
    erwarteter_gewinn_30_tage: float

class BilanzErgebnis(BaseModel):
    aktiva: float
    passiva: float
    details: dict[str, float]  

class MonatsWert(BaseModel):
    monat: str
    einnahmen: float
    ausgaben: float
    gewinn: float

class CashflowWert(BaseModel):
    datum: str
    kontostand: float

class TopPartnerErgebnis(BaseModel):
    top_kunden: dict[str, float]
    top_lieferanten: dict[str, float]

class OffenePostenErgebnis(BaseModel):
    offene_forderungen: float
    offene_verbindlichkeiten: float
    anzahl_offen: int

class LoginDaten(BaseModel):
    benutzername: str
    passwort: str

class LoginErgebnis(BaseModel):
    erfolg: bool
    rolle: str | None = None