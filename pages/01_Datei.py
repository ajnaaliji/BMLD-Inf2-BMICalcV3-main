import streamlit as st
import pandas as pd
import os
import base64

# ===== Login-Schutz =====
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("/")
    st.stop()

# ===== Bilder laden =====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

icons = {
    "chemie": load_icon_base64("assets/adrenaline.png"),
    "haematologie": load_icon_base64("assets/blood.png"),
    "klinische chemie": load_icon_base64("assets/rna.png")
}

# ===== Seiteneinstellungen =====
st.set_page_config(page_title="Fachansicht", page_icon="📂")

# ===== Session-Parameter auslesen =====
fach_key = st.session_state.get("fach", "").lower().strip()
ansicht = st.session_state.get("ansicht", "start").lower().strip()

fach_namen = {
    "chemie": "Chemie",
    "haematologie": "Hämatologie",
    "klinische chemie": "Klinische Chemie"
}

csv_pfade = {
    "chemie": "data/data_chemie.csv",
    "haematologie": "data/data_haematologie.csv",
    "klinische chemie": "data/data_klinische_chemie.csv"
}

ordner_pfade = {
    "chemie": "word_chemie",
    "haematologie": "word_haematologie",
    "klinische chemie": "word_klinische_chemie"
}

fach = fach_namen.get(fach_key, "Unbekannt")
dateipfad = csv_pfade.get(fach_key)
fach_icon = icons.get(fach_key)

username = st.session_state.get("username", None)
if not username:
    st.error("Kein Benutzername gefunden.")
    st.stop()

basis_ordner = ordner_pfade.get(fach_key)
ordner = os.path.join(basis_ordner, username)

# ===== Fachüberschrift mit Bild-Icon =====
st.markdown(f"""
<h1 style='display: flex; align-items: center; gap: 20px; font-size: 36px;'>
    {fach}
    <img src="data:image/png;base64,{fach_icon}" width="42">
</h1>
""", unsafe_allow_html=True)

# ===== Navigation =====
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Start"):
        st.switch_page("Start.py")

with col2:
    if st.button("📝 Neuer Eintrag"):
        if fach_key == "haematologie":
            st.switch_page("pages/02_Haematologie.py")
        elif fach_key == "klinische chemie":
            st.switch_page("pages/04_Klinische Chemie.py")
        elif fach_key == "chemie":
            st.switch_page("pages/03_Chemie.py")

with col3:
    if fach_key == "haematologie":
        if st.button("🧬 Zellatlas"):
            st.switch_page("pages/08_Referenz_Haematologie.py")
    elif fach_key == "klinische chemie":
        if st.button("📊 Referenzwerte"):
            st.switch_page("pages/07_Referenzwerte.py")

st.markdown("### Finde deine Einträge und passe sie bei Bedarf an oder lade sie herunter.")

# ===== Dateien auflisten (WebDAV-kompatibel) =====
from utils.data_manager import DataManager
data_manager = DataManager()
dh = data_manager._get_data_handler(f"{basis_ordner}/{username}")
st.write("🔍 Gesuchter Ordner:", dh.root_path)

try:
    raw_files = dh.filesystem.ls(dh.root_path)
    dateien = [f["name"] for f in raw_files if isinstance(f, dict) and f.get("name", "").endswith(".docx")]
except Exception as e:
    st.error(f"Fehler beim Lesen des Ordners: {e}")
    dateien = []

if dateien:
    suchbegriff = st.text_input("🔎 Suche nach Titel oder Datum").lower()

    anzeigen = []
    for datei in sorted(dateien):
        pfad = os.path.join(ordner, os.path.basename(datei))
        try:
            rohdatum = os.path.basename(datei).split("_")[0]
            datum_formatiert = pd.to_datetime(rohdatum, format="%Y%m%d%H%M%S").strftime("%d.%m.%Y")
            titel = os.path.basename(datei).split("_")[1].replace(".docx", "").replace("-", " ")
        except Exception:
            continue  # Überspringe fehlerhafte Dateinamen

        anzeigen.append({
            "pfad": pfad,
            "dateiname": os.path.basename(datei),
            "rohdatum": rohdatum,
            "datum_formatiert": datum_formatiert,
            "titel": titel
        })

    gefiltert = [e for e in anzeigen if suchbegriff in e["datum_formatiert"].lower() or suchbegriff in e["rohdatum"] or suchbegriff in e["titel"].lower()]

    if gefiltert:
        for eintrag in gefiltert:
            col1, col2 = st.columns([6, 2])
            with col1:
                st.markdown(f"📅 **{eintrag['datum_formatiert']}** – 📄 *{eintrag['titel']}*")
            with col2:
                file_data = dh.read_binary(eintrag["dateiname"])
                st.download_button(
                    label="📂 Öffnen und Bearbeiten",
                    data=file_data,
                    file_name=eintrag["dateiname"],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"open_edit_{eintrag['dateiname']}"
                )
    else:
        st.info("🔍 Keine passenden Einträge gefunden.")
else:
    st.info("Keine gespeicherten Word-Dateien gefunden.")

# ===== Zurück-Button =====
if st.button("🔙 Zurück zur Übersicht"):
    st.session_state.ansicht = "start"
    st.switch_page("/")
