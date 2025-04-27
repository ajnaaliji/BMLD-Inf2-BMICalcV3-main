import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# ==== Dateipfad zur CSV definieren ====
dateipfad = "data/data_klinische_chemie.csv"
os.makedirs("data", exist_ok=True)

# ==== Eintrags-ID und Lade-Logik ====
eintrag_id = st.session_state.get("bearbeite_id")
bearbeiten = eintrag_id is not None

def lade_eintrag(eintrag_id):
    df = pd.read_csv(dateipfad)
    return df[df['id'] == eintrag_id].iloc[0] if eintrag_id in df['id'].values else None

# ==== Vorbefüllung (wenn Bearbeiten) ====
eintrag = lade_eintrag(eintrag_id) if bearbeiten else {}

def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
img_clinic = load_icon_base64("assets/clinical_chemistry.png")

st.markdown(f"""
<h1 style='display: flex; align-items: center; gap: 24px;'>
    Klinische Chemie
    <img src='data:image/png;base64,{img_clinic}' width='50'>
</h1>
""", unsafe_allow_html=True)

from datetime import datetime

fach = "Klinische Chemie"  # du kannst das auch dynamisch machen
eintrag_id = st.session_state.get("bearbeite_id", None)

st.markdown(f"""
<div style='background-color: #eef6ff; padding: 10px 15px; border-radius: 8px; margin-bottom: 20px;'>
    <strong>Fach:</strong> 🧪 {fach} <br>
    <strong>Datum:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')} <br>
    {f"<strong>Eintrags-ID:</strong> {eintrag_id}" if eintrag_id else ""}
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Patientenname", eintrag.get("name", ""))
    geburt = st.text_input("Geburtstag/Alter", eintrag.get("geburt", ""))
    geschlecht = st.selectbox("Biologisches Geschlecht", ["", "weiblich", "männlich", "divers"], index=0 if not bearbeiten else ["", "weiblich", "männlich", "divers"].index(eintrag.get("geschlecht", "")))
with col2:
    groesse = st.text_input("Grösse (cm)", eintrag.get("groesse", ""))
    gewicht = st.text_input("Gewicht (kg)", eintrag.get("gewicht", ""))

vorbefunde = st.text_area("Vorbefunde (falls vorhanden)", eintrag.get("vorbefunde", ""))

st.subheader("Präanalytik")
probenmaterial = st.text_input("Probenmaterial", eintrag.get("probenmaterial", ""))
makro = st.text_area("Makroskopische Beurteilung", eintrag.get("makro", ""))

st.subheader("Analytik")
reagenzien = st.text_area("Reagenzien (Name/LOT/Verfall)", eintrag.get("reagenzien", ""))
qc = st.text_area("Qualitätskontrolle (Name/LOT/Verfall)", eintrag.get("qc", ""))
methode = st.text_input("Methode/Gerät", eintrag.get("methode", ""))
validation = st.text_area("Technische Validation der QC (Soll/Ist)", eintrag.get("validation", ""))

st.subheader("Postanalytik")
bio_val = st.text_area("Biomedizinische Validation", eintrag.get("bio_val", ""))
transversal = st.text_area("Transversalbeurteilung (n/p↑/↓)", eintrag.get("transversal", ""))
plausi = st.text_area("Plausibilitätskontrolle", eintrag.get("plausi", ""))
extremwerte = st.text_area("Extremwerte", eintrag.get("extremwerte", ""))
trend = st.text_area("Trend (zu Vorbefunden)", eintrag.get("trend", ""))
konstellation = st.text_area("Konstellationskontrolle", eintrag.get("konstellation", ""))

# ==== Speichern ====
if st.button("💾 Eintrag speichern"):
    daten = {
        "id": eintrag_id if bearbeiten else f"CC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "name": name,
        "geburt": geburt,
        "geschlecht": geschlecht,
        "groesse": groesse,
        "gewicht": gewicht,
        "vorbefunde": vorbefunde,
        "probenmaterial": probenmaterial,
        "makro": makro,
        "reagenzien": reagenzien,
        "qc": qc,
        "methode": methode,
        "validation": validation,
        "bio_val": bio_val,
        "transversal": transversal,
        "plausi": plausi,
        "extremwerte": extremwerte,
        "trend": trend,
        "konstellation": konstellation,
        "zeit": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists(dateipfad):
        df = pd.read_csv(dateipfad)
        if bearbeiten and eintrag_id in df['id'].values:
            df.loc[df['id'] == eintrag_id] = daten
        else:
            df = pd.concat([df, pd.DataFrame([daten])], ignore_index=True)
    else:
        df = pd.DataFrame([daten])

    df.to_csv(dateipfad, index=False)
    st.success("✅ Eintrag wurde gespeichert!")

# ==== Zurück-Button ====
if st.button("🔙 Zurück"):
    st.switch_page("pages/01_Datei.py")
