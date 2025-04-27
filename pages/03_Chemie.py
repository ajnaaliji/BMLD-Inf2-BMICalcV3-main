import streamlit as st
from datetime import datetime
import os
import pandas as pd
import base64

# ==== Dateipfad definieren ====
dateipfad = "data/data_chemie.csv"
os.makedirs("data", exist_ok=True)

# ==== Bilder laden ====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

img_chemie = load_icon_base64("assets/chemie.png")
img_experiment = load_icon_base64("assets/experiment.png")
img_goal = load_icon_base64("assets/goal.png")
img_steps = load_icon_base64("assets/steps.png")
img_time = load_icon_base64("assets/timetable.png")
img_question = load_icon_base64("assets/thinking-bubble.png")
img_beschreib = load_icon_base64("assets/contract.png")
img_mark = load_icon_base64("assets/question.png")
img_flag = load_icon_base64("assets/goal-flag.png")

# ==== Bearbeitungsmodus prüfen ====
edit_index = st.query_params.get("edit", None)
eintrag = {}
bearbeiten = False

if edit_index is not None and os.path.exists(dateipfad):
    df = pd.read_csv(dateipfad)
    try:
        idx = int(edit_index)
        if idx < len(df):
            eintrag = df.iloc[idx].to_dict()
            bearbeiten = True
    except:
        pass

# ==== Titel ====
st.markdown(f"""
<h1 style='display: flex; align-items: center; gap: 24px; font-size: 40px;'>
    Chemie
    <img src='data:image/png;base64,{img_chemie}' width='50'>
</h1>
""", unsafe_allow_html=True)

# ==== Formular-Struktur ====

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("**Titel des Praktikums**")
    titel = st.text_input("", value=eintrag.get("titel", ""), key="titel_input")

with col2:
    st.markdown("**Datum**")
    datum_value = datetime.today()
    if bearbeiten and "datum" in eintrag:
        try:
            datum_value = datetime.strptime(eintrag["datum"], "%Y-%m-%d")
        except:
            pass
    datum = st.date_input("", value=datum_value, key="datum_input")

# Beschreibung
st.markdown("**Beschreibung des Versuchs**")
beschreibung = st.text_area("", height=120, value=eintrag.get("beschreibung", ""), key="beschreibung_input")

# Material & Fragen
col3, col4 = st.columns(2)
with col3:
    st.markdown("**Benötigtes Material**")
    material = st.text_area("", height=100, value=eintrag.get("material", ""), key="material_input")

with col4:
    st.markdown("**Vorbereitung + Fragen**")
    fragen = st.text_area("", height=100, value=eintrag.get("fragen", ""), key="fragen_input")

# Arbeitsschritte
st.markdown("**Arbeitsschritte**")
arbeitsschritte = st.text_area("", height=120, value=eintrag.get("arbeitsschritte", ""), key="steps_input")

# Ziel
st.markdown("**Ziel des Versuchs**")
ziel = st.text_area("", height=100, value=eintrag.get("ziel", ""), key="goal_input")

# ==== Speichern-Button ====
if st.button("💾 Eintrag speichern"):
    neuer_eintrag = {
        "titel": titel,
        "datum": datum.strftime("%Y-%m-%d"),
        "beschreibung": beschreibung,
        "material": material,
        "fragen": fragen,
        "arbeitsschritte": arbeitsschritte,
        "ziel": ziel,
        "zeit": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists(dateipfad):
        df = pd.read_csv(dateipfad)
        if bearbeiten:
            df.loc[int(edit_index)] = neuer_eintrag
        else:
            df = pd.concat([df, pd.DataFrame([neuer_eintrag])], ignore_index=True)
    else:
        df = pd.DataFrame([neuer_eintrag])

    df.to_csv(dateipfad, index=False)
    st.success("✅ Eintrag wurde erfolgreich gespeichert!")

# ==== Zurück-Button ====
if st.button("🔙 Zurück"):
    st.switch_page("pages/01_Datei.py")
