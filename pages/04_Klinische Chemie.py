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
import uuid  # für eindeutige Dateinamen

# ==== Benutzername und DataManager vorbereiten ====
username = st.session_state.get("username", "anonymous")
from utils.data_manager import DataManager
data_manager = DataManager()
dh = data_manager._get_data_handler(f"word_klinische_chemie/{username}")

# ==== CSV definieren ====
dateipfad = f"data/data_klinische_chemie_{username}.csv"
os.makedirs(os.path.dirname(dateipfad), exist_ok=True)

# ==== Icon laden ====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

img_clinic = load_icon_base64("assets/clinical_chemistry.png")

# ==== Start ====
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

vorbefunde = st.text_area("Vorbefunde", height=100)
probenmaterial = st.text_input("Probenmaterial")
makro = st.text_area("Makroskopische Beurteilung", height=100)
reagenzien = st.text_area("Reagenzien (Name/LOT/Verfall)", height=100)
qc = st.text_area("Qualitätskontrolle (Name/LOT/Verfall)", height=100)
methode = st.text_input("Methode/Gerät")
validation = st.text_area("Technische Validation der QC", height=100)
bio_val = st.text_area("Biomedizinische Validation", height=100)
transversal = st.text_area("Transversalbeurteilung", height=100)
plausi = st.text_area("Plausibilitätskontrolle", height=100)
extremwerte = st.text_area("Extremwerte", height=100)
trend = st.text_area("Trend zu Vorbefunden", height=100)
konstellation = st.text_area("Konstellationskontrolle", height=100)

# ==== Bild-Upload ====
st.markdown("### 📷 Mikroskopiebilder oder Befundfotos hochladen")
uploaded_images = st.file_uploader("Wähle ein oder mehrere Bilder", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

image_folder = f"bilder_klinische_chemie/{username}"
dh_img = data_manager._get_data_handler(image_folder)
os.makedirs(dh_img.root_path, exist_ok=True)
if uploaded_images:
    st.markdown("**Vorschau:**")
    for img in uploaded_images:
        st.image(img, use_container_width=True)
        # Speichern mit eindeutigen Namen
        image_bytes = img.getvalue()
        unique_id = uuid.uuid4().hex
        clean_name = img.name.replace(" ", "_").replace("ä", "ae").replace("ü", "ue").replace("ö", "oe")
        filename = f"{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}_{unique_id}_{clean_name}"
        dh_img = data_manager._get_data_handler(image_folder)
        dh_img.save(filename, image_bytes)

# ==== Speichern & Exportieren ====
if st.button("💾 Speichern und Exportieren"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    neuer_eintrag = {
        "id": f"CC_{timestamp}",
        "patient_name": patient_name,
        "geburtstag": geburtstag,
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

    # Speichern in CSV
    if os.path.exists(dateipfad):
        df = pd.read_csv(dateipfad)
        df = pd.concat([df, pd.DataFrame([neuer_eintrag])], ignore_index=True)
    else:
        df = pd.DataFrame([neuer_eintrag])
    df.to_csv(dateipfad, index=False)

    # === Word erstellen ===
    doc = Document()
    doc.add_heading("Klinische Chemie Bericht", 0)
    for k, v in neuer_eintrag.items():
        if k not in ["id", "zeit"]:
            doc.add_heading(k.replace("_", " ").capitalize(), level=2)
            doc.add_paragraph(str(v))

    if uploaded_images:
        doc.add_page_break()
        doc.add_heading("Mikroskopiebilder / Befundfotos", level=2)
        for img in uploaded_images:
            try:
                image_pil = Image.open(img)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                    image_pil.save(tmp_img.name)
                    doc.add_picture(tmp_img.name, width=Inches(4.5))
            except Exception as e:
                st.warning(f"⚠️ Bild konnte nicht eingefügt werden: {img.name} ({e})")

    # Word speichern
    buffer_word = io.BytesIO()
    doc.save(buffer_word)
    buffer_word.seek(0)
    titel_speichern = patient_name.strip().replace(" ", "-").replace(".", "").replace(",", "")
    filename_word = f"{timestamp}_{titel_speichern}.docx"
    dh.save(filename_word, buffer_word.getvalue())

    # Download Word
    st.download_button(
        label="⬇️ Word herunterladen",
        data=buffer_word,
        file_name=filename_word,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # === PDF erstellen ===
    buffer_pdf = io.BytesIO()
    c = canvas.Canvas(buffer_pdf, pagesize=A4)
    width, height = A4
    x = 2 * cm
    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Klinische Chemie Bericht")
    y -= 1.5 * cm

    c.setFont("Helvetica", 12)
    for k, v in neuer_eintrag.items():
        if k not in ["id", "zeit"]:
            c.drawString(x, y, f"{k.replace('_', ' ').capitalize()}: {v}")
            y -= 0.7 * cm
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
    c.save()
    buffer_pdf.seek(0)

    st.download_button(
        label="⬇️ PDF herunterladen",
        data=buffer_pdf,
        file_name=f"{timestamp}_Klinische_Chemie.pdf",
        mime="application/pdf"
    )

    st.success("✅ Eintrag gespeichert!")

# ==== Zurück-Button ====
if st.button("🔙 Zurück zur Übersicht"):
    st.switch_page("pages/01_Datei.py")
