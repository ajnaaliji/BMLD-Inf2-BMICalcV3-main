import streamlit as st
import pandas as pd
import os
import io
import base64
from datetime import datetime
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
from PIL import Image
from docx.shared import Inches
import uuid

# ==== Benutzername und DataManager vorbereiten ====
username = st.session_state.get("username", "anonymous")
from utils.data_manager import DataManager
data_manager = DataManager()

# === Benutzer-Ordner für Word, Bilder, Anhänge ===
word_ordner = f"word_klinische_chemie/{username}"
image_folder = f"bilder_klinische_chemie/{username}"
anhang_ordner = f"anhang_klinische_chemie/{username}"
dateipfad = f"data/data_klinische_chemie_{username}.csv"

# === DataHandler initialisieren ===
dh = data_manager._get_data_handler(word_ordner)
dh_img = data_manager._get_data_handler(image_folder)
dh_docs = data_manager._get_data_handler(anhang_ordner)

# === Ordner ggf. erstellen ===
if not dh.filesystem.exists(dh.root_path):
    dh.filesystem.makedirs(dh.root_path)
if not dh_img.filesystem.exists(dh_img.root_path):
    dh_img.filesystem.makedirs(dh_img.root_path)
if not dh_docs.filesystem.exists(dh_docs.root_path):
    dh_docs.filesystem.makedirs(dh_docs.root_path)

# === Leere CSV-Datei anlegen, falls nicht vorhanden ===
os.makedirs(os.path.dirname(dateipfad), exist_ok=True)
if not os.path.exists(dateipfad):
    pd.DataFrame().to_csv(dateipfad, index=False)

# ==== Icon laden ====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

img_clinic = load_icon_base64("assets/clinical_chemistry.png")

# ==== UI Header ====
st.set_page_config(page_title="Klinische Chemie", page_icon="🧪")
st.markdown(f"""
<h1 style='display: flex; align-items: center; gap: 24px;'>
    Klinische Chemie
    <img src='data:image/png;base64,{img_clinic}' width='50'>
</h1>
""", unsafe_allow_html=True)

# ==== Formularfelder ====
col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Patientenname")
    geburtstag = st.text_input("Geburtstag/Alter")
    geschlecht = st.selectbox("Geschlecht", ["", "weiblich", "männlich", "divers"])
with col2:
    groesse = st.text_input("Größe (cm)")
    gewicht = st.text_input("Gewicht (kg)")

# Weitere Textfelder
textfelder = {
    "vorbefunde": st.text_area("Vorbefunde", height=100),
    "probenmaterial": st.text_input("Probenmaterial"),
    "makro": st.text_area("Makroskopische Beurteilung", height=100),
    "reagenzien": st.text_area("Reagenzien (Name/LOT/Verfall)", height=100),
    "qc": st.text_area("Qualitätskontrolle (Name/LOT/Verfall)", height=100),
    "methode": st.text_input("Methode/Gerät"),
    "validation": st.text_area("Technische Validation der QC", height=100),
    "bio_val": st.text_area("Biomedizinische Validation", height=100),
    "transversal": st.text_area("Transversalbeurteilung", height=100),
    "plausi": st.text_area("Plausibilitätskontrolle", height=100),
    "extremwerte": st.text_area("Extremwerte", height=100),
    "trend": st.text_area("Trend zu Vorbefunden", height=100),
    "konstellation": st.text_area("Konstellationskontrolle", height=100)
}

# ==== Bild-Upload ====
st.markdown("### 📷 Mikroskopiebilder oder Befundfotos hochladen")
uploaded_images = st.file_uploader("Bilder auswählen", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
temp_uploaded_images = []
bestehende_bilder = [f["name"] for f in dh_img.filesystem.ls(dh_img.root_path)]
if uploaded_images:
    st.markdown("**Vorschau:**")
    for img in uploaded_images:
        st.image(img, use_container_width=True)
        name_clean = img.name.replace(" ", "_").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        if name_clean in bestehende_bilder:
            st.info(f"⏭️ Bild bereits vorhanden: {name_clean}")
        else:
            temp_uploaded_images.append((name_clean, img.getvalue()))

# ==== Datei-Upload (PDF/Word) ====
st.markdown("### 📎 Weitere Dateien anhängen (z. B. PDF, Word)")
uploaded_docs = st.file_uploader("Dateien auswählen", type=["pdf", "docx"], accept_multiple_files=True)
temp_uploads = []
bestehende_dateien = [f["name"] for f in dh_docs.filesystem.ls(dh_docs.root_path)]

# ==== Speichern & Exportieren ====
if st.button("💾 Speichern und Exportieren"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    anhang_dateien = []

    # ==== Dateien speichern (korrekt mit Timestamp) ====
    if uploaded_docs:
        for file in uploaded_docs:
            name_clean = file.name.replace(" ", "_")
            unique = uuid.uuid4().hex[:8]
            anhang_name = f"{timestamp}_{unique}_{name_clean}"
            if anhang_name in bestehende_dateien:
                st.info(f"⏭️ Datei bereits vorhanden: {anhang_name}")
            else:
                try:
                    dh_docs.save(anhang_name, file.getvalue())
                    anhang_dateien.append(anhang_name)
                except Exception as e:
                    st.warning(f"⚠️ Datei konnte nicht gespeichert werden: {anhang_name} ({e})")

    # === Word erstellen ===
    titel = f"cc_{uuid.uuid4().hex[:6]}"
    doc = Document()
    doc.add_heading("Klinische Chemie Bericht", 0)
    for k, v in {
        "patient_name": patient_name, "geburtstag": geburtstag, "geschlecht": geschlecht,
        "groesse": groesse, "gewicht": gewicht, **textfelder
    }.items():
        doc.add_heading(k.replace("_", " ").capitalize(), level=2)
        doc.add_paragraph(str(v))

    if uploaded_images:
        doc.add_page_break()
        doc.add_heading("Mikroskopiebilder / Befundfotos", level=2)
        for img in uploaded_images:
            try:
                image = Image.open(img)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    image.save(tmp.name)
                    doc.add_picture(tmp.name, width=Inches(4.5))
            except Exception as e:
                st.warning(f"Bild konnte nicht eingefügt werden: {img.name} ({e})")

    word_buffer = io.BytesIO()
    doc.save(word_buffer)
    word_buffer.seek(0)
    word_name = f"{timestamp}_{titel}_{patient_name.strip().replace(' ', '-').lower()}.docx"

    dh_word = data_manager._get_data_handler(f"word_klinische_chemie/{username}")
    dh_word.save(word_name, word_buffer.getvalue())

    st.download_button("⬇️ Word herunterladen", word_buffer, file_name=word_name, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    # === PDF erstellen ===
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    x, y = 2 * cm, height - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Klinische Chemie Bericht")
    y -= 1.5 * cm
    c.setFont("Helvetica", 12)
    for k, v in {
        "patient_name": patient_name, "geburtstag": geburtstag, "geschlecht": geschlecht,
        "groesse": groesse, "gewicht": gewicht, **textfelder
    }.items():
        c.drawString(x, y, f"{k.replace('_', ' ').capitalize()}: {v}")
        y -= 0.7 * cm
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm
    c.save()
    pdf_buffer.seek(0)
    pdf_name = f"{timestamp}_Klinische_Chemie.pdf"
    dh_docs.save(pdf_name, pdf_buffer.getvalue())
    anhang_dateien.append(pdf_name)

    st.download_button("⬇️ PDF herunterladen", pdf_buffer, file_name=pdf_name, mime="application/pdf")

    # === CSV aktualisieren ===
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    neuer_eintrag = {
        "id": f"CC_{timestamp}",
        "titel": titel,
        "patient_name": patient_name,
        "geburtstag": geburtstag,
        "geschlecht": geschlecht,
        "groesse": groesse,
        "gewicht": gewicht,
        "datum": datetime.now().strftime("%Y-%m-%d"),
        "zeit": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "anhaenge": anhang_dateien,
        **textfelder
    }

    if os.path.exists(dateipfad):
        try:
            df = pd.read_csv(dateipfad)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame()
        df = pd.concat([df, pd.DataFrame([neuer_eintrag])], ignore_index=True)
    else:
        df = pd.DataFrame([neuer_eintrag])

    st.success("✅ Eintrag erfolgreich gespeichert!")

# ==== Zurück zur Übersicht ====
if st.button("🔙 Zurück zur Übersicht"):
    st.switch_page("pages/01_Datei.py")
