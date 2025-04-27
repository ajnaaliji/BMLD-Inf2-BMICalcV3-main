import streamlit as st
import pandas as pd
import os
import base64

# ===== Login-Schutz =====
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("Start")

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

fach = fach_namen.get(fach_key, "Unbekannt")
dateipfad = csv_pfade.get(fach_key)
fach_icon = icons.get(fach_key)
ordner_pfade = {
    "chemie": "data/word_chemie",
    "haematologie": "data/word_haematologie",
    "klinische chemie": "data/word_klinische_chemie"
}

ordner = ordner_pfade.get(fach_key)

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

# ==== Dateien auflisten ====
# ==== Dateien auflisten ====
# ==== Dateien auflisten ====
# ==== Dateien auflisten ====
if ordner and os.path.exists(ordner):
    dateien = [f for f in os.listdir(ordner) if f.endswith(".docx")]
    if dateien:
        suchbegriff = st.text_input("🔎 Suche nach Titel oder Datum").lower()

        # ALLE Einträge vorbereiten
        anzeigen = []
        for datei in sorted(dateien):
            pfad = os.path.join(ordner, datei)
            rohdatum = datei.split("_")[0]
            datum_formatiert = pd.to_datetime(rohdatum, format="%Y%m%d%H%M%S").strftime("%d.%m.%Y")
            titel = datei.split("_")[1].replace(".docx", "").replace("-", " ")

            anzeigen.append({
                "pfad": pfad,
                "dateiname": datei,
                "rohdatum": rohdatum,  # ← original Timestamp
                "datum_formatiert": datum_formatiert,  # ← für die Anzeige
                "titel": titel
            })

        # FILTER
        gefiltert = []
        for eintrag in anzeigen:
            # Suche muss auf ALLES möglich sein
            if (
                suchbegriff in eintrag["datum_formatiert"].lower() or
                suchbegriff in eintrag["rohdatum"] or
                suchbegriff in eintrag["titel"].lower()
            ):
                gefiltert.append(eintrag)

        # Ausgabe
        if gefiltert:
            for eintrag in gefiltert:
                col1, col2 = st.columns([6, 2])
                with col1:
                    st.markdown(f"📅 **{eintrag['datum_formatiert']}** – 📄 *{eintrag['titel']}*")
                with col2:
                    with open(eintrag["pfad"], "rb") as f:
                        file_data = f.read()
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
else:
    st.error("Ordner für gespeicherte Dateien existiert nicht.")

# ===== Zurück-Button =====
if st.button("🔙 Zurück zur Übersicht"):
    st.session_state.ansicht = "start"
    st.switch_page("pages/01_Datei.py")
