import streamlit as st
import pandas as pd
import os
import base64
import time
from utils.data_manager import DataManager
import ast

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

ordner_pfade = {
    "chemie": "word_chemie",
    "haematologie": "word_haematologie",
    "klinische chemie": "word_klinische_chemie"
}

fach = fach_namen.get(fach_key, "Unbekannt")
fach_icon = icons.get(fach_key)

username = st.session_state.get("username", None)
if not username:
    st.error("Kein Benutzername gefunden.")
    st.stop()

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

# ===== DataManager initialisieren =====
data_manager = DataManager()
dh = data_manager._get_data_handler(f"{ordner_pfade.get(fach_key)}/{username}")

if fach_key == "chemie":
    dh_anhang = data_manager._get_data_handler(f"anhang_chemie/{username}")
    data_manager.load_user_data("chemie_eintraege", "data_chemie.csv", initial_value=[])
    eintrags_df = pd.DataFrame(st.session_state["chemie_eintraege"])

elif fach_key == "klinische chemie":
    dh_anhang = data_manager._get_data_handler(f"anhang_klinische_chemie/{username}")
    data_manager.load_user_data("klinische_eintraege", f"data_klinische_chemie_{username}.csv", initial_value=[])
    eintrags_df = pd.DataFrame(st.session_state["klinische_eintraege"])

elif fach_key == "haematologie":
    dh_anhang = data_manager._get_data_handler(f"anhang_haematologie/{username}")
    data_manager.load_user_data("haematologie_eintraege", f"data_haematologie_{username}.csv", initial_value=[])
    eintrags_df = pd.DataFrame(st.session_state["haematologie_eintraege"])

pass  # nichts weiter nötig – alles wurde bereits oben geladen

if eintrags_df.empty or "titel" not in eintrags_df.columns:
    st.info("Noch keine gültigen Einträge vorhanden.")
    st.stop()

if not dh.filesystem.exists(dh.root_path):
    dh.filesystem.makedirs(dh.root_path)

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
        try:
            teile = os.path.basename(datei).replace(".docx", "").split("_", 2)
            rohdatum = teile[0]
            datum_formatiert = pd.to_datetime(rohdatum, format="%Y%m%d%H%M%S").strftime("%d.%m.%Y")
            titel = teile[2].replace("-", " ") if len(teile) > 2 else teile[-1].replace("-", " ")
            anzeigen.append({"dateiname": datei, "rohdatum": rohdatum, "datum_formatiert": datum_formatiert, "titel": titel})
        except Exception:
            continue

    gefiltert = [e for e in anzeigen if suchbegriff in e["datum_formatiert"].lower() or suchbegriff in e["titel"].lower()]

    for eintrag in gefiltert:
        col1, col2 = st.columns([6, 2])
        with col1:
            st.markdown(f"📅 **{eintrag['datum_formatiert']}** – 📄 *{eintrag['titel']}*")
        with col2:
            file_data = dh.read_binary(os.path.basename(eintrag["dateiname"]))
            st.download_button(
                label="📂 Öffnen und Bearbeiten",
                data=file_data,
                file_name=eintrag["dateiname"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"open_edit_{eintrag['dateiname']}"
            )

        if not eintrags_df.empty:
            vergleichsspalte = "titel"
            datum_spalte = "datum" if "datum" in eintrags_df.columns else "zeit"
            match = eintrags_df[(eintrags_df[vergleichsspalte].str.strip().str.lower() == eintrag["titel"].strip().lower()) &
                                (eintrags_df[datum_spalte].str.startswith(pd.to_datetime(eintrag["datum_formatiert"], format="%d.%m.%Y").strftime("%Y-%m-%d")))]

            if not match.empty:
                try:
                    anhaenge = ast.literal_eval(match.iloc[0].get("anhaenge", "[]"))
                except:
                    anhaenge = []
                if anhaenge:
                    st.markdown("📎 Zugehörige Anhänge:")
                    for anhang in list(dict.fromkeys(anhaenge)):
                        file_data = None
                        for _ in range(3):
                            try:
                                file_data = dh_anhang.read_binary(os.path.basename(anhang))
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
    st.info("Keine gespeicherten Word-Dateien gefunden.")

if st.button("🔙 Zurück zur Übersicht"):
    st.session_state.ansicht = "start"
    st.switch_page("/")

    file_data