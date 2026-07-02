import datetime
import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
import os
import plotly.express as px

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# 1. Wide Layout: Nutzt den gesamten Bildschirm
st.set_page_config(page_title="Buchungssystem", page_icon="📒", layout="wide")

st.markdown("""
    <style>
    /* Versteckt nur den globalen Header/Menü oben, lässt die Sidebar in Ruhe */
    header {visibility: visible;}
    /* Versteckt den 'Made with Streamlit' Footer */
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# 0) Login-System (Session State)
# ---------------------------------------------------------------
if "angemeldet" not in st.session_state:
    st.session_state.angemeldet = False
    st.session_state.rolle = None

if not st.session_state.angemeldet:
    # Login zentrieren und in eine "Karte" (Container) packen
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.write("") # Etwas Abstand nach oben
        st.write("")
        with st.container(border=True):
            st.title("🔒 Login")
            benutzername = st.text_input("Benutzername")
            passwort = st.text_input("Passwort", type="password")

            if st.button("Anmelden", use_container_width=True):
                try:
                    antwort = requests.post(
                        f"{API_URL}/login",
                        json={"benutzername": benutzername, "passwort": passwort},
                    )
                    ergebnis = antwort.json()
                except requests.exceptions.ConnectionError:
                    st.error("Backend nicht erreichbar – läuft der Server?")
                else:
                    if ergebnis["erfolg"]:
                        st.session_state.angemeldet = True
                        st.session_state.rolle = ergebnis["rolle"]
                        st.rerun()
                    else:
                        st.error("Falscher Benutzername oder Passwort.")
    st.stop()

# ---------------------------------------------------------------
# Sidebar für Status und Logout
# ---------------------------------------------------------------
with st.sidebar:
    st.write(f"Angemeldet als: **{st.session_state.rolle}**")
    st.divider()
    if st.button("📂 Demo-Daten laden", use_container_width=True):
        antwort = requests.post(f"{API_URL}/buchungen/demo")
        if antwort.status_code == 200:
            ergebnis = antwort.json()
            if ergebnis["eingefuegt"] > 0:
                st.toast(f"{ergebnis['eingefuegt']} Demo-Buchungen geladen!")
                st.rerun()
            else:
                st.toast("Es existieren bereits Buchungen.")
    if st.button("Logout", use_container_width=True):
        st.session_state.angemeldet = False
        st.session_state.rolle = None
        st.rerun()

st.title("📒 Buchungssystem Dashboard")
st.divider()

# ---------------------------------------------------------------
# Admin-Ansicht (Voller Zugriff mit Tabs)
# ---------------------------------------------------------------
if st.session_state.rolle == "Admin":

    # Tabs für eine aufgeräumte Navigation anlegen
    tab_uebersicht, tab_dashboard, tab_guv, tab_forecast, tab_bilanz, tab_analysen = st.tabs([
        "📝 Erfassen & Übersicht",
        "💹 Dashboard",
        "📊 GuV-Auswertung",
        "🔮 30-Tage Forecast",
        "📈 Bilanz",
        "🔍 Analysen",
    ])

    # --- TAB 1: EINGABE & TABELLE ---
    with tab_uebersicht:
        # Bildschirm teilen: Links 1/3 (Formular), Rechts 2/3 (Tabelle)
        col_form, col_table = st.columns([1, 2])

        with col_form:
            st.subheader("Neue Buchung")
            with st.container(border=True):
                with st.form("neue_buchung"):
                    datum = st.date_input("Datum", value=datetime.date.today())
                    betrag = st.number_input("Betrag (€)", min_value=0.01, step=10.0)
                    kategorie = st.text_input("Kategorie")
                    typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"])
                    konto = st.selectbox("Konto", ["Bank", "Kasse", "Eigenkapital", "Verbindlichkeit"])
                    partner = st.text_input("Geschäftspartner")
                    kostenstelle = st.selectbox("Kostenstelle", ["Vertrieb", "Marketing", "IT", "Verwaltung", "Beratung", "Betrieb", "Schulung"])
                    bezahlt = st.checkbox("Bereits bezahlt?", value=True)
                    beschreibung = st.text_input("Beschreibung")
                    absenden = st.form_submit_button("Speichern", use_container_width=True)

                if absenden:
                    daten = {"datum": datum.isoformat(), "betrag": betrag, "kategorie": kategorie, "typ": typ, "beschreibung": beschreibung, "konto": konto, "partner": partner, "kostenstelle": kostenstelle, "bezahlt": bezahlt}
                    antwort = requests.post(f"{API_URL}/buchungen", json=daten)
                    if antwort.status_code == 200:
                        st.toast("Buchung erfolgreich gespeichert!")
                        st.rerun()
                    else:
                        st.error(f"Fehler: {antwort.text}")

        with col_table:
            st.subheader("Alle Buchungen")
            buchungen = requests.get(f"{API_URL}/buchungen").json()
            if buchungen:
                # hide_index=True entfernt die unnötige Zahlen-Spalte links
                st.dataframe(pd.DataFrame(buchungen), width='stretch', hide_index=True)
            else:
                st.info("Noch keine Buchungen erfasst.")

        # ---------------------------------------------------------------
        # NEU: Buchung bearbeiten oder löschen
        # ---------------------------------------------------------------
        st.divider()
        st.subheader("✏️ Buchung bearbeiten oder löschen")

        if buchungen:
            # Auswahl-Liste: lesbarer Text  ->  komplette Buchung (als Dict)
            optionen = {
                f"ID {b['id']} · {b['typ']} · {b['betrag']:.2f} € · {b['beschreibung']}": b
                for b in buchungen
            }
            auswahl = st.selectbox("Welche Buchung möchtest du bearbeiten?", list(optionen.keys()))
            gewaehlt = optionen[auswahl]   # die komplette Buchung, die gerade ausgewählt ist

            # Feste Auswahllisten (wie im Anlege-Formular)
            TYPEN = ["Einnahme", "Ausgabe"]
            KONTEN = ["Bank", "Kasse", "Eigenkapital", "Verbindlichkeit"]
            KOSTENSTELLEN = ["Vertrieb", "Marketing", "IT", "Verwaltung", "Beratung", "Betrieb", "Schulung"]

            def _pos(liste, wert):
                # Findet die Position des aktuellen Werts – oder 0, falls er nicht in der Liste steht.
                return liste.index(wert) if wert in liste else 0

            with st.container(border=True):
                with st.form("buchung_bearbeiten"):
                    # value=... füllt jedes Feld mit dem bisherigen Wert vor
                    e_datum = st.date_input("Datum", value=datetime.date.fromisoformat(gewaehlt["datum"]))
                    e_betrag = st.number_input("Betrag (€)", min_value=0.01, step=10.0, value=float(gewaehlt["betrag"]))
                    e_kategorie = st.text_input("Kategorie", value=gewaehlt["kategorie"])
                    e_typ = st.selectbox("Typ", TYPEN, index=_pos(TYPEN, gewaehlt["typ"]))
                    e_konto = st.selectbox("Konto", KONTEN, index=_pos(KONTEN, gewaehlt["konto"]))
                    e_partner = st.text_input("Geschäftspartner", value=gewaehlt["partner"] or "")
                    e_kostenstelle = st.selectbox("Kostenstelle", KOSTENSTELLEN, index=_pos(KOSTENSTELLEN, gewaehlt["kostenstelle"]))
                    e_bezahlt = st.checkbox("Bereits bezahlt?", value=bool(gewaehlt["bezahlt"]))
                    e_beschreibung = st.text_input("Beschreibung", value=gewaehlt["beschreibung"] or "")

                    # Zwei Buttons nebeneinander: Speichern (PUT) und Löschen (DELETE)
                    sp_speichern, sp_loeschen = st.columns(2)
                    btn_speichern = sp_speichern.form_submit_button("💾 Änderungen speichern", use_container_width=True)
                    btn_loeschen = sp_loeschen.form_submit_button("🗑️ Löschen", use_container_width=True)

            # Reaktion auf "Speichern": schickt die geänderten Daten per PUT ans Backend
            if btn_speichern:
                daten = {
                    "datum": e_datum.isoformat(), "betrag": e_betrag, "kategorie": e_kategorie,
                    "typ": e_typ, "beschreibung": e_beschreibung, "konto": e_konto,
                    "partner": e_partner, "kostenstelle": e_kostenstelle, "bezahlt": e_bezahlt,
                }
                antwort = requests.put(f"{API_URL}/buchungen/{gewaehlt['id']}", json=daten)
                if antwort.status_code == 200:
                    st.toast("Buchung aktualisiert!")
                    st.rerun()   # Seite neu laden -> Tabelle zeigt sofort die Änderung
                else:
                    st.error(f"Fehler: {antwort.text}")

            # Reaktion auf "Löschen": schickt ein DELETE ans Backend
            if btn_loeschen:
                antwort = requests.delete(f"{API_URL}/buchungen/{gewaehlt['id']}")
                if antwort.status_code == 200:
                    st.toast("Buchung gelöscht!")
                    st.rerun()
                else:
                    st.error(f"Fehler: {antwort.text}")
        else:
            st.info("Noch keine Buchungen zum Bearbeiten vorhanden.")

    # --- TAB: DASHBOARD (vertiefte KPIs) ---
    with tab_dashboard:
        st.subheader("Kennzahlen-Dashboard")

        # Daten vom Backend holen
        guv = requests.get(f"{API_URL}/auswertung/guv").json()
        monatsdaten = requests.get(f"{API_URL}/auswertung/monatsentwicklung").json()
        cashflow = requests.get(f"{API_URL}/auswertung/cashflow").json()

        # Kennzahlen oben: Einnahmen, Gewinn, Gewinnmarge
        einnahmen = guv["einnahmen"]
        gewinn = guv["gewinn"]
        marge = (gewinn / einnahmen * 100) if einnahmen > 0 else 0.0

        k1, k2, k3 = st.columns(3)
        k1.metric("Gesamteinnahmen", f"{einnahmen:,.2f} €")
        k2.metric("Gesamtgewinn", f"{gewinn:,.2f} €")
        k3.metric("Gewinnmarge", f"{marge:.1f} %")
        st.divider()

        # Monatsentwicklung (Zeitreihe)
        st.markdown("**Monatsentwicklung**")
        if monatsdaten:
            df_m = pd.DataFrame(monatsdaten)
            fig1 = px.line(
                df_m, x="monat", y=["einnahmen", "ausgaben"], markers=True,
                labels={"monat": "Monat", "value": "Euro", "variable": ""},
                color_discrete_map={"einnahmen": "#2e7d32", "ausgaben": "#c62828"},
            )
            fig1.update_layout(margin=dict(t=10, b=0, l=0, r=0), legend_title_text="")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Keine Daten für die Monatsentwicklung.")

        st.divider()
        col_links, col_rechts = st.columns(2)

        # Top-Ausgaben nach Kategorie (aus den GuV-Daten)
        with col_links:
            st.markdown("**Top-Ausgaben nach Kategorie**")
            ausgaben_kat = guv["ausgaben_nach_kategorie"]
            if ausgaben_kat:
                df_k = pd.DataFrame(list(ausgaben_kat.items()), columns=["Kategorie", "Betrag"])
                df_k = df_k.sort_values("Betrag", ascending=True)
                fig2 = px.bar(
                    df_k, x="Betrag", y="Kategorie", orientation="h",
                    labels={"Betrag": "Euro", "Kategorie": ""},
                    color_discrete_sequence=["#c62828"],
                )
                fig2.update_layout(margin=dict(t=10, b=0, l=0, r=0))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Keine Ausgaben erfasst.")

        # Cashflow-Verlauf (kumulierter Kontostand)
        with col_rechts:
            st.markdown("**Cashflow-Verlauf (Kontostand)**")
            if cashflow:
                df_c = pd.DataFrame(cashflow)
                df_c["datum"] = pd.to_datetime(df_c["datum"])
                fig3 = px.area(
                    df_c, x="datum", y="kontostand",
                    labels={"datum": "Datum", "kontostand": "Euro"},
                    color_discrete_sequence=["#1565c0"],
                )
                fig3.update_layout(margin=dict(t=10, b=0, l=0, r=0))
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Kein Cashflow vorhanden.")

    # --- TAB: ANALYSEN (tiefe KPIs) ---
    with tab_analysen:
        st.subheader("Vertiefte Analysen")

        top_partner = requests.get(f"{API_URL}/auswertung/top-partner").json()
        offene = requests.get(f"{API_URL}/auswertung/offene-posten").json()
        kostenstellen = requests.get(f"{API_URL}/auswertung/kostenstellen").json()

        # Offene Posten als Kennzahlen
        st.markdown("**Offene Posten**")
        o1, o2, o3 = st.columns(3)
        o1.metric("Offene Forderungen", f"{offene['offene_forderungen']:,.2f} €")
        o2.metric("Offene Verbindlichkeiten", f"{offene['offene_verbindlichkeiten']:,.2f} €")
        o3.metric("Anzahl offener Posten", offene["anzahl_offen"])
        st.divider()

        col_l, col_r = st.columns(2)

        # Top-Kunden und Top-Lieferanten als Tabellen
        with col_l:
            st.markdown("**Top-Kunden (Umsatz)**")
            if top_partner["top_kunden"]:
                df_k = pd.DataFrame(list(top_partner["top_kunden"].items()),
                                    columns=["Kunde", "Umsatz (€)"])
                st.dataframe(df_k, use_container_width=True, hide_index=True)
            else:
                st.info("Keine Kundenumsätze.")

            st.markdown("**Top-Lieferanten (Kosten)**")
            if top_partner["top_lieferanten"]:
                df_li = pd.DataFrame(list(top_partner["top_lieferanten"].items()),
                                     columns=["Lieferant", "Kosten (€)"])
                st.dataframe(df_li, use_container_width=True, hide_index=True)
            else:
                st.info("Keine Lieferantenkosten.")

        # Kosten nach Kostenstelle als Tortendiagramm
        with col_r:
            st.markdown("**Kosten nach Kostenstelle**")
            if kostenstellen:
                fig = px.pie(
                    names=list(kostenstellen.keys()),
                    values=list(kostenstellen.values()),
                    hole=0.4,
                )
                fig.update_layout(margin=dict(t=10, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Kostenstellen-Daten.")

    # --- TAB 2: GUV & DIAGRAMM ---
    with tab_guv:
        st.subheader("Gewinn- und Verlustrechnung")
        with st.container(border=True):
            spalte_von, spalte_bis = st.columns(2)
            von = spalte_von.date_input("Von (optional)", value=None)
            bis = spalte_bis.date_input("Bis (optional)", value=None)

        params = {}
        if von: params["von"] = von.isoformat()
        if bis: params["bis"] = bis.isoformat()

        guv = requests.get(f"{API_URL}/auswertung/guv", params=params).json()

        st.write("")
        m1, m2, m3 = st.columns(3)
        m1.metric("Einnahmen", f"{guv['einnahmen']:.2f} €")
        m2.metric("Ausgaben", f"{guv['ausgaben']:.2f} €")
        m3.metric("Gewinn", f"{guv['gewinn']:.2f} €")
        st.divider()

        # Diagramm mit transparentem Hintergrund
        df_guv = pd.DataFrame({
            "Typ": ["Einnahmen", "Ausgaben"],
            "Euro": [guv["einnahmen"], guv["ausgaben"]],
        })
        fig = px.bar(
            df_guv, x="Typ", y="Euro", color="Typ",
            color_discrete_map={"Einnahmen": "#2e7d32", "Ausgaben": "#c62828"},
        )
        fig.update_layout(margin=dict(t=10, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 3: FORECAST ---
    with tab_forecast:
        st.subheader("Prognose")
        st.info("Basierend auf dem durchschnittlichen Tagestrend der bisherigen Daten wird die Entwicklung für die nächsten 30 Tage prognostiziert.")

        with st.container(border=True):
            forecast = requests.get(f"{API_URL}/auswertung/forecast").json()
            f1, f2, f3 = st.columns(3)
            f1.metric("Erwartete Einnahmen", f"{forecast['erwartete_einnahmen_30_tage']:.2f} €")
            f2.metric("Erwartete Ausgaben", f"{forecast['erwartete_ausgaben_30_tage']:.2f} €")
            f3.metric("Erwarteter Gewinn", f"{forecast['erwarteter_gewinn_30_tage']:.2f} €")

    # --- TAB 4: BILANZ (Refactored) ---
    with tab_bilanz:
        st.subheader("Bilanzübersicht")

        # 1. Stichtag in einer schönen Spalte
        col_stichtag, col_status = st.columns([2, 1])
        with col_stichtag:
            stichtag = st.date_input("Stichtag wählen", value=datetime.date.today())

        bilanz = requests.get(f"{API_URL}/auswertung/bilanz", params={"stichtag": stichtag.isoformat()}).json()

        # 2. Status-Indikator
        with col_status:
            if abs(bilanz['aktiva'] - bilanz['passiva']) < 0.01:
                st.success("Bilanz ausgeglichen ✓")
            else:
                st.warning("Bilanz nicht ausgeglichen!")

        # 3. KPI-Boxen für Aktiva/Passiva
        m1, m2 = st.columns(2)
        m1.metric("Summe Aktiva", f"{bilanz['aktiva']:.2f} €")
        m2.metric("Summe Passiva", f"{bilanz['passiva']:.2f} €")

        st.divider()

        # 4. Details als saubere Tabelle statt JSON
        st.write("Detaillierte Kontenübersicht:")
        df_details = pd.DataFrame(list(bilanz['details'].items()), columns=["Konto", "Stand (€)"])
        st.dataframe(df_details, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------
# User-Ansicht (Eingeschränkter Zugriff)
# ---------------------------------------------------------------
else:
    st.info("Du bist als User angemeldet. Die Auswertungen sind Administratoren vorbehalten.")

    # Formular zentriert darstellen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Neue Buchung")
        with st.container(border=True):
            with st.form("neue_buchung_user"):
                datum = st.date_input("Datum", value=datetime.date.today())
                betrag = st.number_input("Betrag (€)", min_value=0.01, step=10.0)
                kategorie = st.text_input("Kategorie")
                typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"])
                konto = st.selectbox("Konto", ["Bank", "Kasse", "Eigenkapital", "Verbindlichkeit"])
                partner = st.text_input("Geschäftspartner")
                kostenstelle = st.selectbox("Kostenstelle", ["Vertrieb", "Marketing", "IT", "Verwaltung", "Beratung", "Betrieb", "Schulung"])
                bezahlt = st.checkbox("Bereits bezahlt?", value=True)
                beschreibung = st.text_input("Beschreibung")
                absenden = st.form_submit_button("Speichern", use_container_width=True)

            if absenden:
                daten = {"datum": datum.isoformat(), "betrag": betrag, "kategorie": kategorie, "typ": typ, "beschreibung": beschreibung, "konto": konto, "partner": partner, "kostenstelle": kostenstelle, "bezahlt": bezahlt}
                antwort = requests.post(f"{API_URL}/buchungen", json=daten)
                if antwort.status_code == 200:
                    st.toast("Buchung erfolgreich gespeichert!")
                else:
                    st.error(f"Fehler: {antwort.text}")
