# ==== Datei: 01_Datei.py ====
import streamlit as st
import pandas as pd
import base64
import time
import ast
from utils.data_manager import DataManager
from utils.ui_helpers import apply_theme
from utils.ui_helpers import apply_theme

def entferne_verwaiste_eintraege(df, data_key, word_handler, anhang_handler, data_manager):
    neue_eintraege = []

    for _, row in df.iterrows():
        word_datei = row.get("dateiname", "")
        anhaenge = row.get("anhaenge", [])

        if isinstance(anhaenge, str):
            try:
                anhaenge = ast.literal_eval(anhaenge)
            except:
                anhaenge = []

        word_exists = word_handler.exists(word_datei) if word_datei else True
        all_attachments_exist = all(anhang_handler.exists(a) for a in anhaenge)

        if word_exists and all_attachments_exist:
            neue_eintraege.append(row)

    if len(neue_eintraege) != len(df):
        st.session_state[data_key] = pd.DataFrame(neue_eintraege)
        data_manager.save_data(data_key)
        st.success("Verwaiste Einträge wurden entfernt.")
        return pd.DataFrame(neue_eintraege)
    
    return df

# ===== Login-Schutz =====
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("/")
    st.stop()

# ===== Fachname lesen =====
fach_key = st.session_state.get("fach", "").lower().strip()

# ===== Session Cleanup für alte Einträge =====
eintrag_keys = {
    "chemie": "chemie_eintraege",
    "haematologie": "haematologie_eintraege",
    "klinische chemie": "klinische_eintraege"
}
eintrags_key = eintrag_keys.get(fach_key)
if eintrags_key and eintrags_key in st.session_state:
    del st.session_state[eintrags_key]

# ===== Icons laden =====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

icons = {
    "chemie": load_icon_base64("assets/adrenaline.png"),
    "haematologie": load_icon_base64("assets/blood.png"),
    "klinische chemie": load_icon_base64("assets/rna.png"),
    "semester": load_icon_base64("assets/semester.png"),
    "datum": load_icon_base64("assets/calendar.png"),
    "suchen": load_icon_base64("assets/search.png")
}

# ===== Session-Daten =====
st.set_page_config(page_title="Fachansicht", page_icon="📂")
apply_theme()
fach_key = st.session_state.get("fach", "").lower().strip()
username = st.session_state.get("username")

fach_namen = {
    "chemie": "Chemie",
    "haematologie": "Hämatologie",
    "klinische chemie": "Klinische Chemie"
}
ordner_pfade = {
    "chemie": "word_chemie",
    "haematologie": "word_haematologie",
    "klinische chemie": "word_klinische_chemie"
}

fach = fach_namen.get(fach_key, "Unbekannt")
fach_icon = icons.get(fach_key)

st.markdown(f"""
<h1 style='display: flex; align-items: center; gap: 20px; font-size: 36px;'>
    {fach}
    <img src="data:image/png;base64,{fach_icon}" width="48">
</h1>
""", unsafe_allow_html=True)

# ===== Navigation =====
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Start"):
        st.switch_page("Start.py")
with col2:
    if st.button("Neuer Eintrag"):
        seiten = {
            "haematologie": "pages/02_Haematologie.py",
            "klinische chemie": "pages/04_Klinische Chemie.py",
            "chemie": "pages/03_Chemie.py"
        }
        st.switch_page(seiten.get(fach_key, "Start.py"))
with col3:
    if fach_key == "haematologie" and st.button("Zellatlas"):
        st.switch_page("pages/08_Referenz_Haematologie.py")
    elif fach_key == "klinische chemie" and st.button("Referenzwerte"):
        st.switch_page("pages/07_Referenzwerte.py")

st.markdown("### Finde deine Einträge und lade sie herunter.")

# ===== DataManager initialisieren =====
data_manager = DataManager()
dh = data_manager._get_data_handler(f"{ordner_pfade.get(fach_key)}/{username}")

# === Einträge & Anhänge laden ===
if fach_key == "chemie":
    data_key = "chemie_eintraege"
    data_manager.load_user_data(data_key, "data_chemie.csv", initial_value=[])
    if data_key not in st.session_state or not isinstance(st.session_state[data_key], pd.DataFrame):
        st.session_state[data_key] = pd.DataFrame()
    dh_anhang = data_manager._get_data_handler(f"anhang_chemie/{username}")
    eintrags_df = pd.DataFrame(st.session_state[data_key])
    eintrags_df = entferne_verwaiste_eintraege(eintrags_df, data_key, dh, dh_anhang, data_manager)
    
    eintrags_df["semester"] = eintrags_df.get("semester", "").astype(str).fillna("")

elif fach_key == "klinische chemie":
    data_key = "klinische_eintraege"
    data_manager.load_user_data(data_key, f"data_klinische_chemie_{username}.csv", initial_value=[])
    if data_key not in st.session_state or not isinstance(st.session_state[data_key], pd.DataFrame):
        st.session_state[data_key] = pd.DataFrame()
    dh_anhang = data_manager._get_data_handler(f"anhang_klinische_chemie/{username}")
    eintrags_df = pd.DataFrame(st.session_state[data_key])
    eintrags_df = entferne_verwaiste_eintraege(eintrags_df, data_key, dh, dh_anhang, data_manager)

    eintrags_df["semester"] = eintrags_df.get("semester", "").astype(str).fillna("")

elif fach_key == "haematologie":
    data_key = "haematologie_eintraege"
    data_manager.load_user_data(data_key, "data_haematologie.csv", initial_value=[])
    if data_key not in st.session_state or not isinstance(st.session_state[data_key], pd.DataFrame):
        st.session_state[data_key] = pd.DataFrame()
    dh_anhang = data_manager._get_data_handler(f"anhang_haematologie/{username}")
    eintrags_df = pd.DataFrame(st.session_state[data_key])
    eintrags_df = entferne_verwaiste_eintraege(eintrags_df, data_key, dh, dh_anhang, data_manager)

    if "semester" in eintrags_df.columns:
        eintrags_df["semester"] = eintrags_df["semester"].astype(str).fillna("")
    else:
        eintrags_df["semester"] = ""

# ==== Prüfung auf gültige Daten ====
if eintrags_df.empty or "titel" not in eintrags_df.columns or "datum" not in eintrags_df.columns:
    st.info("Noch keine gültigen Einträge vorhanden.")
    st.stop()

# Semesterfilter mit Icon
st.markdown(f"""
<div style='display: flex; align-items: center; gap: 10px; font-size: 18px; margin-top: 20px;'>
    <img src="data:image/png;base64,{icons['semester']}" width="26">
    <strong>Filter nach Semester</strong>
</div>
""", unsafe_allow_html=True)
semester_filter = st.selectbox("", ["Alle", "1", "2", "3", "4", "5", "6"])

# Suchfeld mit Icon
st.markdown(f"""
<div style='display: flex; align-items: center; gap: 10px; font-size: 18px; margin-top: 30px;'>
    <img src="data:image/png;base64,{icons['suchen']}" width="26">
    <strong>Suche nach Titel oder Datum</strong>
</div>
""", unsafe_allow_html=True)
suchbegriff = st.text_input("", placeholder="z. B. Vitamin oder 2025-05-08").strip().lower()

# 🇨🇭 Unterstützung für Schweizer Format
if "." in suchbegriff and len(suchbegriff) == 10:
    try:
        tag, monat, jahr = suchbegriff.split(".")
        suchbegriff = f"{jahr}-{monat.zfill(2)}-{tag.zfill(2)}"
    except:
        pass

eintrags_df["suchtext"] = eintrags_df["titel"].str.lower() + " " + eintrags_df["datum"].astype(str)

# 🧠 Kombinierte Filterung
gefiltert = eintrags_df.copy()
if semester_filter != "Alle":
    gefiltert = gefiltert[gefiltert["semester"] == semester_filter]
if suchbegriff:
    gefiltert = gefiltert[gefiltert["suchtext"].str.contains(suchbegriff, na=False)]


for _, row in gefiltert.iterrows():
    col1, col2 = st.columns([6, 2])
    with col1:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 10px; font-size: 16px;'>
            <img src="data:image/png;base64,{icons['datum']}" width="24">
            <strong>{row['datum']}</strong> – <em>{row['titel']}</em>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        word_file = row.get("dateiname")
        if word_file:
            try:
                file_data = dh.read_binary(word_file)
                st.download_button(
                    label="⬇️ Word öffnen",
                    data=file_data,
                    file_name=word_file,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"word_{word_file}"
                )
            except Exception as e:
                st.warning(f"❌ Word-Datei fehlt: {e}")

    # === Anhänge anzeigen ===
    anhaenge = row.get("anhaenge", [])
    if isinstance(anhaenge, str):
        try:
            anhaenge = ast.literal_eval(anhaenge)
        except Exception:
            anhaenge = []

    if anhaenge:
        st.markdown("Zugehörige Anhänge:")
        for anhang in list(dict.fromkeys(anhaenge)):
            file_data = None
            for _ in range(3):
                try:
                    file_data = dh_anhang.read_binary(anhang)
                    break
                except FileNotFoundError:
                    time.sleep(1)
            if file_data:
                st.download_button(
                    label=f"⬇️ {anhang}",
                    data=file_data,
                    file_name=anhang,
                    mime="application/pdf" if anhang.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"anhang_{anhang}"
                )
            else:
                st.error(f"❌ Anhang nicht gefunden: {anhang}")

# ==== Zurück zur Startseite ====
if st.button("🔙 Zurück zur Übersicht"):
    st.session_state.ansicht = "start"
    st.switch_page("Start.py")

