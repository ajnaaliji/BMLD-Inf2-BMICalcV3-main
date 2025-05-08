import streamlit as st
import os
import yaml
import io
from datetime import datetime
from docx import Document
from docx.shared import Inches
from PIL import Image
import tempfile
from utils.data_manager import DataManager
from zoneinfo import ZoneInfo
from os.path import basename

# === Setup ===
st.set_page_config(page_title="Zellatlas Hämatologie", page_icon="🦠")
if "username" not in st.session_state or st.session_state["authentication_status"] is not True:
    st.error("❌ Nicht eingeloggt – bitte zuerst anmelden.")
    st.stop()
username = st.session_state["username"]
data_manager = DataManager()
atlas_folder = f"zellatlas_haematologie/{username}"
dh = data_manager._get_data_handler(atlas_folder)
if not dh.filesystem.exists(dh.root_path):
    dh.filesystem.makedirs(dh.root_path)

# === Kategorien ===
bereiche = {
    "Weißes Blutbild": [
        "Myeloblast", "Promyelozyt", "Myelozyt", "Metamyelozyt",
        "Stabkerniger", "Segmentkerniger", "Eosinophiler", "Basophiler",
        "Monozyt", "Lymphozyt", "Plasmazelle", "Nicht klassifizierbar (weiß)"
    ],
    "Rotes Blutbild": [
        "Normozyt", "Mikrozyt", "Makrozyt", "Fragmentozyt",
        "Targetzelle", "Sichelzelle", "Nicht klassifizierbar (rot)"
    ],
    "Thrombozyten": [
        "Normal", "Riesenthrombozyt", "Agranulär", "Nicht klassifizierbar (thrombo)"
    ]
}

# === Eintragsliste initialisieren ===
if "zell_eintraege" not in st.session_state:
    st.session_state.zell_eintraege = [{}]

# === Eingabeformulare ===
st.title("Zellatlas Hämatologie")
st.markdown("### 🥼 Zell-Einträge erfassen")

for idx, eintrag in enumerate(st.session_state.zell_eintraege):
    st.markdown(f"## 🔍 Eintrag {idx + 1}")
    typ = st.selectbox("Zelltyp wählen", [f"{k}: {v}" for k in bereiche for v in bereiche[k]], key=f"typ_{idx}")
    beschreibung = st.text_area("Beschreibung / Merkmale", key=f"beschreibung_{idx}")
    bild = st.file_uploader("Bild hochladen (png/jpg)", type=["png", "jpg", "jpeg"], key=f"bild_{idx}")
    st.session_state.zell_eintraege[idx] = {"typ": typ, "beschreibung": beschreibung, "bild": bild}

# === Plus-Button ===
st.markdown("---")
if st.button("➕ Weiteren Eintrag hinzufügen"):
    st.session_state.zell_eintraege.append({})
    st.rerun()

# === Speichern ===
if st.button("📂 Alle Einträge speichern"):
    erfolgreich = False
    for eintrag in st.session_state.zell_eintraege:
        if eintrag.get("typ") and eintrag.get("beschreibung"):
            now = datetime.now(ZoneInfo("Europe/Zurich"))
            timestamp = now.strftime("%Y%m%dT%H%M%S")
            eintrag_data = {
                "typ": eintrag["typ"],
                "beschreibung": eintrag["beschreibung"],
                "zeit": now.isoformat()
            }
            if eintrag["bild"]:
                img_bytes = eintrag["bild"].getvalue()
                img_name = f"{timestamp}_{eintrag['bild'].name.replace(' ', '_')}"
                dh.save(img_name, img_bytes)
                eintrag_data["bild"] = img_name

            yaml_name = f"{timestamp}_{eintrag['typ'].split(':')[1].strip().lower().replace(' ', '_')}.yaml"
            dh.write_text(yaml_name, yaml.dump(eintrag_data, allow_unicode=True))
            erfolgreich = True

    if erfolgreich:
        st.success("✅ Einträge wurden gespeichert.")
        st.session_state.zell_eintraege = [{}]
    else:
        st.warning("⚠️ Keine gültigen Einträge zum Speichern gefunden.")

# === Anzeige gespeicherter Einträge ===
st.markdown("## 📘 Gespeicherte Zell-Einträge")
eintrags_liste = [
    f["name"] if isinstance(f, dict) else f
    for f in dh.filesystem.ls(dh.root_path)
    if (f["name"] if isinstance(f, dict) else f).endswith(".yaml")
]

if eintrags_liste:
    eintrags_liste.sort(reverse=True)
    for filename in eintrags_liste:
        try:
            data = yaml.safe_load(dh.read_text(basename(filename)))
            st.markdown(f"### 🔬 {data['typ']}")
            zeit_raw = data.get("zeit", "")
            try:
                zeit_formatiert = datetime.fromisoformat(zeit_raw).strftime("%d.%m.%Y, %H:%M Uhr")
                st.markdown(f"🕒 {zeit_formatiert}")
            except:
                st.markdown(f"🕒 {zeit_raw}")
            st.markdown(data.get("beschreibung", "Keine Beschreibung vorhanden."))
            if "bild" in data:
                st.image(dh.read_binary(basename(data["bild"])), width=300)

            # === Lösch-Logik mit Bestätigung ===
            if st.button(f"🗑️ Löschen: {filename}", key=f"delete_{filename}"):
                st.session_state[f"confirm_delete_{filename}"] = True

            if st.session_state.get(f"confirm_delete_{filename}", False):
                st.warning(f"Möchtest du **{data['typ']}** wirklich löschen?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Abbrechen", key=f"cancel_{filename}"):
                        st.session_state[f"confirm_delete_{filename}"] = False
                        st.rerun()
                with col2:
                    if st.button("✅ Ja, löschen", key=f"confirm_{filename}"):
                        try:
                            dh.filesystem.delete(os.path.join(dh.root_path, basename(filename)))
                            if "bild" in data:
                                bild_pfad = os.path.join(dh.root_path, basename(data["bild"]))
                                if dh.filesystem.exists(bild_pfad):
                                    dh.filesystem.delete(bild_pfad)
                            st.success("✅ Eintrag gelöscht.")
                            st.rerun()
                        except Exception as e:
                            st.warning(f"⚠️ Fehler beim Löschen von {filename}: {e}")
            st.markdown("---")
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden von {filename}: {e}")
else:
    st.info("Noch keine Einträge vorhanden.")

# === Zurück zur Übersicht ===
st.markdown("---")
if st.button("🔙 Zurück zur Übersicht"):
    st.switch_page("pages/01_Datei.py")
