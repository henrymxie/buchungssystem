import pandas as pd   
# für Datenauswertung: gruppieren, summieren, Datum filtern

"""Berechnet eine GuV aus einer Liste von Buchungen. von/bis sind optionale ISO-Datumsstrings ('2026-06-01') zur Eingrenzung."""
def berechne_guv(buchungen, von=None, bis=None):  
    # Leerer Datensatz -> alles 0, sonst würde Pandas meckern.
    if not buchungen:
        return {
            "einnahmen": 0.0, "ausgaben": 0.0, "gewinn": 0.0,
            "einnahmen_nach_kategorie": {}, "ausgaben_nach_kategorie": {},
        }

    df = pd.DataFrame(buchungen)              # Liste von Dicts -> Tabelle
    df["datum"] = pd.to_datetime(df["datum"]) # Text -> echtes Datum

    # Optional auf einen Zeitraum eingrenzen
    if von:
        df = df[df["datum"] >= pd.to_datetime(von)]
    if bis:
        df = df[df["datum"] <= pd.to_datetime(bis)]

    einnahmen_df = df[df["typ"] == "Einnahme"]
    ausgaben_df = df[df["typ"] == "Ausgabe"]

    einnahmen = float(einnahmen_df["betrag"].sum())
    ausgaben = float(ausgaben_df["betrag"].sum())

    return {
        "einnahmen": einnahmen,
        "ausgaben": ausgaben,
        "gewinn": einnahmen - ausgaben,
        # Aufschlüsselung pro Kategorie – praktisch für den späteren Chart
        "einnahmen_nach_kategorie": einnahmen_df.groupby("kategorie")["betrag"].sum().to_dict(),
        "ausgaben_nach_kategorie": ausgaben_df.groupby("kategorie")["betrag"].sum().to_dict(),
    }

"""Berechnet eine einfache 30-Tage-Prognose basierend auf historischen Tagesdurchschnitten."""
def berechne_forecast(buchungen):
    if not buchungen:
        return {
            "erwartete_einnahmen_30_tage": 0.0, 
            "erwartete_ausgaben_30_tage": 0.0, 
            "erwarteter_gewinn_30_tage": 0.0
        }

    df = pd.DataFrame(buchungen)
    df["datum"] = pd.to_datetime(df["datum"])
    
    # Zeitraum der bisherigen Daten ermitteln
    min_datum = df["datum"].min()
    max_datum = df["datum"].max()
    # +1, damit auch ein einzelner Tag als 1 Tag zählt und wir nicht durch 0 teilen
    tage = (max_datum - min_datum).days + 1 
    
    einnahmen_gesamt = df[df["typ"] == "Einnahme"]["betrag"].sum()
    ausgaben_gesamt = df[df["typ"] == "Ausgabe"]["betrag"].sum()
    
    # Tagesdurchschnitt berechnen und auf 30 Tage hochrechnen
    einnahmen_30d = (einnahmen_gesamt / tage) * 30
    ausgaben_30d = (ausgaben_gesamt / tage) * 30
    
    return {
        "erwartete_einnahmen_30_tage": float(einnahmen_30d),
        "erwartete_ausgaben_30_tage": float(ausgaben_30d),
        "erwarteter_gewinn_30_tage": float(einnahmen_30d - ausgaben_30d)
    }

def berechne_bilanz(buchungen, stichtag):
    """Berechnet die Bilanzwerte zu einem Stichtag basierend auf den Kontentypen."""
    if not buchungen:
        return {"aktiva": 0.0, "passiva": 0.0, "details": {}}
        
    df = pd.DataFrame(buchungen)
    df["datum"] = pd.to_datetime(df["datum"])
    
    # Filtere alle Buchungen bis zum Stichtag
    df_stichtag = df[df["datum"] <= pd.to_datetime(stichtag)]
    
    # Gruppierung nach Konto
    bestaende = df_stichtag.groupby("konto")["betrag"].sum().to_dict()
    
    # Definition: 
    # Aktiva: Was das Unternehmen "hat" (Bank + Kasse)
    # Passiva: Woher das Geld kommt (Eigenkapital + Verbindlichkeiten)
    aktiva = bestaende.get("Bank", 0.0) + bestaende.get("Kasse", 0.0)
    passiva = bestaende.get("Eigenkapital", 0.0) + bestaende.get("Verbindlichkeit", 0.0)
    
    return {
        "aktiva": aktiva,
        "passiva": passiva,
        "details": bestaende
    }

def berechne_monatsentwicklung(buchungen):
    """Summiert Einnahmen und Ausgaben pro Monat - für die Zeitreihe."""
    if not buchungen:
        return []
    df = pd.DataFrame(buchungen)
    df["datum"] = pd.to_datetime(df["datum"])
    df["monat"] = df["datum"].dt.to_period("M").astype(str)   # z. B. "2025-01"

    ergebnis = []
    for monat, gruppe in df.groupby("monat"):
        einnahmen = float(gruppe[gruppe["typ"] == "Einnahme"]["betrag"].sum())
        ausgaben = float(gruppe[gruppe["typ"] == "Ausgabe"]["betrag"].sum())
        ergebnis.append({
            "monat": monat,
            "einnahmen": einnahmen,
            "ausgaben": ausgaben,
            "gewinn": einnahmen - ausgaben,
        })
    return ergebnis


def berechne_cashflow(buchungen):
    """Berechnet den kumulierten Kontostand-Verlauf über die Zeit."""
    if not buchungen:
        return []
    df = pd.DataFrame(buchungen)
    df["datum"] = pd.to_datetime(df["datum"])
    df = df.sort_values("datum")

    # Einnahme zählt positiv, Ausgabe negativ
    df["fluss"] = df["betrag"].where(df["typ"] == "Einnahme", -df["betrag"])
    # pro Tag summieren, dann fortlaufend aufaddieren (cumsum)
    taeglich = df.groupby(df["datum"].dt.date)["fluss"].sum().cumsum()

    return [{"datum": str(d), "kontostand": float(wert)} for d, wert in taeglich.items()]

def berechne_top_partner(buchungen, anzahl=5):
    """Top-Kunden nach Umsatz und Top-Lieferanten nach Kosten."""
    if not buchungen:
        return {"top_kunden": {}, "top_lieferanten": {}}
    df = pd.DataFrame(buchungen)

    einnahmen = df[(df["typ"] == "Einnahme") & (df["partner"] != "")]
    ausgaben = df[(df["typ"] == "Ausgabe") & (df["partner"] != "")]

    top_kunden = (einnahmen.groupby("partner")["betrag"].sum()
                  .sort_values(ascending=False).head(anzahl).to_dict())
    top_lieferanten = (ausgaben.groupby("partner")["betrag"].sum()
                       .sort_values(ascending=False).head(anzahl).to_dict())
    return {"top_kunden": top_kunden, "top_lieferanten": top_lieferanten}

def berechne_offene_posten(buchungen):
    """Offene (unbezahlte) Forderungen und Verbindlichkeiten."""
    if not buchungen:
        return {"offene_forderungen": 0.0, "offene_verbindlichkeiten": 0.0, "anzahl_offen": 0}
    df = pd.DataFrame(buchungen)
    offen = df[~df["bezahlt"].astype(bool)]   # nur unbezahlte Buchungen

    forderungen = float(offen[offen["typ"] == "Einnahme"]["betrag"].sum())
    verbindlichkeiten = float(offen[offen["typ"] == "Ausgabe"]["betrag"].sum())
    return {
        "offene_forderungen": forderungen,
        "offene_verbindlichkeiten": verbindlichkeiten,
        "anzahl_offen": int(len(offen)),
    }

def berechne_kostenstellen(buchungen):
    """Summiert die Ausgaben je Kostenstelle."""
    if not buchungen:
        return {}
    df = pd.DataFrame(buchungen)
    ausgaben = df[(df["typ"] == "Ausgabe") & (df["kostenstelle"] != "")]
    return (ausgaben.groupby("kostenstelle")["betrag"].sum()
            .sort_values(ascending=False).to_dict())