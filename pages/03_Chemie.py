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

# ==== Dateipfad und Ordner definieren ====
dateipfad = "data/data_chemie.csv"
os.makedirs(os.path.dirname(dateipfad), exist_ok=True)
word_ordner = "word_chemie"
os.makedirs(word_ordner, exist_ok=True)

# ==== Icon laden ====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

img_chemie = load_icon_base64("assets/chemie.png")

# ==== Start ==== 
st.set_page_config(page_title="Chemie", page_icon="🧪")

st.markdown(f"""
<h1 style='display: flex; align-items: center; gap: 24px;'>
    Chemie
    <img src='data:image/png;base64,{img_chemie}' width='50'>
</h1>
""", unsafe_allow_html=True)

# ==== Formular Felder ====
col1, col2 = st.columns([2, 1])
with col1:
    titel = st.text_input("Titel des Praktikums")
with col2:
    datum = st.date_input("Datum", value=datetime.today())

beschreibung = st.text_area("Beschreibung des Versuchs", height=120)
col3, col4 = st.columns(2)
with col3:
    material = st.text_area("Benötigtes Material", height=100)
with col4:
    fragen = st.text_area("Vorbereitung + Fragen", height=100)

arbeitsschritte = st.text_area("Arbeitsschritte", height=120)
ziel = st.text_area("Ziel des Versuchs", height=100)

# ==== Speichern und Export ====
if st.button("💾 Speichern und Exportieren"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

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
        df = pd.concat([df, pd.DataFrame([neuer_eintrag])], ignore_index=True)
    else:
        df = pd.DataFrame([neuer_eintrag])

    df.to_csv(dateipfad, index=False)
    st.success("✅ Eintrag gespeichert!")

    # ==== Word erstellen ====
    doc = Document()
    doc.add_heading(f"Praktikum: {titel}", 0)
    doc.add_paragraph(f"Datum: {datum.strftime('%d.%m.%Y')}")
    doc.add_heading("Beschreibung", level=2)
    doc.add_paragraph(beschreibung)
    doc.add_heading("Material", level=2)
    doc.add_paragraph(material)
    doc.add_heading("Vorbereitung + Fragen", level=2)
    doc.add_paragraph(fragen)
    doc.add_heading("Arbeitsschritte", level=2)
    doc.add_paragraph(arbeitsschritte)
    doc.add_heading("Ziel", level=2)
    doc.add_paragraph(ziel)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    filename_word = f"{timestamp}_{titel.replace(' ', '-')}.docx"
    # Benutzername holen (sicherheitsgeprüft)
    username = st.session_state.get("username", "anonymous")

    # Benutzer-spezifischer Speicherordner
    user_folder = os.path.join(word_ordner, username)
    os.makedirs(user_folder, exist_ok=True)

    # Pfad zur Datei
    from utils.data_manager import DataManager
    data_manager = DataManager()
    dh = data_manager._get_data_handler(f"word_chemie/{username}")
    dh.save(filename_word, buffer.getvalue())

    st.download_button(
        label="⬇️ Word herunterladen",
        data=buffer,
        file_name=filename_word,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # ==== PDF erstellen ====
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        c = canvas.Canvas(tmp.name, pagesize=A4)
        width, height = A4
        x = 2 * cm
        y = height - 2 * cm

        c.setFont("Helvetica-Bold", 16)
        c.drawString(x, y, f"Praktikum: {titel}")
        y -= 1.5 * cm

        c.setFont("Helvetica", 12)
        c.drawString(x, y, f"Datum: {datum.strftime('%d.%m.%Y')}")
        y -= 1.5 * cm

        lines = [
            ("Beschreibung", beschreibung),
            ("Material", material),
            ("Vorbereitung + Fragen", fragen),
            ("Arbeitsschritte", arbeitsschritte),
            ("Ziel", ziel)
        ]

        for title, content in lines:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x, y, title)
            y -= 1 * cm
            c.setFont("Helvetica", 12)
            for line in content.splitlines():
                c.drawString(x, y, line.strip())
                y -= 0.6 * cm
                if y < 2 * cm:
                    c.showPage()
                    y = height - 2 * cm

        c.save()

        with open(tmp.name, "rb") as f:
            st.download_button(
                label="⬇️ PDF herunterladen",
                data=f.read(),
                file_name=f"{timestamp}_{titel.replace(' ', '-')}.pdf",
                mime="application/pdf"
            )

# ==== Zurück-Button ====
if st.button("🔙 Zurück zur Übersicht"):
    st.switch_page("pages/01_Datei.py")
