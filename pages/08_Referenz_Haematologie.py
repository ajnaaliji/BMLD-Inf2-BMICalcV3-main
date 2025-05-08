import streamlit as st
import os
import yaml
import io
from datetime import datetime
import base64
from docx import Document
from docx.shared import Inches
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import tempfile
from utils.data_manager import DataManager

# === Setup ===
st.set_page_config(page_title="Zellatlas Hämatologie", page_icon="🦢")
username = st.session_state.get("username", "anonymous")
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

# === Eingabeformulare anzeigen ===
st.title("🦢 Zellatlas Hämatologie")
st.markdown("### 🧬 Zell-Einträge eingeben")

for idx, eintrag in enumerate(st.session_state.zell_eintraege):
    st.markdown(f"## 🧾 Eintrag {idx + 1}")
    typ = st.selectbox("Kategorie und Zelltyp wählen", [f"{k}: {v}" for k in bereiche for v in bereiche[k]],
                       key=f"typ_{idx}")
    beschreibung = st.text_area("Beschreibung / Merkmale", key=f"beschreibung_{idx}")
    bild = st.file_uploader("Bild hochladen (png/jpg)", type=["png", "jpg", "jpeg"], key=f"bild_{idx}")
    st.session_state.zell_eintraege[idx] = {"typ": typ, "beschreibung": beschreibung, "bild": bild}

# === Plus-Button unten anzeigen ===
st.markdown("---")
if st.button("➕ Weiteren Eintrag hinzufügen"):
    st.session_state.zell_eintraege.append({})
    st.rerun()

# === Speichern ===
if st.button("💾 Alle Einträge speichern"):
    erfolgreich = False
    for eintrag in st.session_state.zell_eintraege:
        if eintrag.get("typ") and eintrag.get("beschreibung"):
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            eintrag_data = {
                "typ": eintrag["typ"],
                "beschreibung": eintrag["beschreibung"],
                "zeit": datetime.now().isoformat()
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
        st.success("✅ Alle Einträge wurden gespeichert.")
        st.session_state.zell_eintraege = [{}]
    else:
        st.warning("⚠️ Keine gültigen Einträge zum Speichern gefunden.")

# === Gespeicherte Einträge anzeigen ===
st.markdown("## 📚 Gespeicherte Einträge")
eintrags_liste = [
    f["name"] if isinstance(f, dict) else f
    for f in dh.filesystem.ls(dh.root_path)
    if (f["name"] if isinstance(f, dict) else f).endswith(".yaml")
]

if eintrags_liste:
    eintrags_liste.sort(reverse=True)
    for filename in eintrags_liste:
        try:
            data = yaml.safe_load(dh.read_text(os.path.basename(filename)))
            st.markdown(f"### 🔬 {data['typ']}")
            st.markdown(f"🕒 {data.get('zeit', '')}")
            st.markdown(data.get("beschreibung", "Keine Beschreibung vorhanden."))
            if "bild" in data:
                st.image(dh.read_binary(os.path.basename(data["bild"])), width=300)
            st.markdown("---")
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden von {filename}: {e}")
else:
    st.info("Noch keine Einträge vorhanden.")

# === Exportfunktion ===
if st.button("⬇️ Gesamten Zellatlas als Word & PDF exportieren"):
    # Word
    doc = Document()
    doc.add_heading("Zellatlas Hämatologie", 0)
    for filename in eintrags_liste:
        data = yaml.safe_load(dh.read_text(os.path.basename(filename)))
        doc.add_heading(data["typ"], level=2)
        doc.add_paragraph(data.get("beschreibung", ""))
        if "bild" in data:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                img_data = dh.read_binary(os.path.basename(data["bild"]))
                image = Image.open(io.BytesIO(img_data)).convert("RGB")
                image.save(tmp_img.name, format="PNG", dpi=(96, 96))
                doc.add_picture(tmp_img.name, width=Inches(4.5))

    buffer_word = io.BytesIO()
    doc.save(buffer_word)
    buffer_word.seek(0)
    st.download_button("⬇️ Word herunterladen", data=buffer_word,
                       file_name="Zellatlas_Haematologie.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    # PDF
    buffer_pdf = io.BytesIO()
    c = canvas.Canvas(buffer_pdf, pagesize=A4)
    width, height = A4
    x, y = 2 * cm, height - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Zellatlas Hämatologie")
    y -= 2 * cm
    for filename in eintrags_liste:
        data = yaml.safe_load(dh.read_text(os.path.basename(filename)))
        if y < 4 * cm:
            c.showPage()
            y = height - 2 * cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y, data["typ"])
        y -= 0.8 * cm
        c.setFont("Helvetica", 12)

        for line in data.get("beschreibung", "").splitlines():
            c.drawString(x, y, line.strip())
            y -= 0.6 * cm
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
        if "bild" in data:
            try:
                img_data = dh.read_binary(os.path.basename(data["bild"]))
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                    image = Image.open(io.BytesIO(img_data)).convert("RGB")
                    image.save(tmp_img.name, format="PNG")
                    img_width = 6 * cm
                    img_height = 6 * cm
                    if y - img_height < 2 * cm:
                        c.showPage()
                        y = height - 2 * cm
                    c.drawImage(tmp_img.name, x, y - img_height, width=img_width, height=img_height)
                    y -= (img_height + 1 * cm)
            except Exception as e:
                c.drawString(x, y, f"[Fehler beim Einfügen des Bildes: {e}]")
                y -= 1 * cm
    c.save()
    buffer_pdf.seek(0)
    st.download_button("⬇️ PDF herunterladen", data=buffer_pdf,
                       file_name="Zellatlas_Haematologie.pdf", mime="application/pdf")

# === Zurück ===
st.markdown("---")
if st.button("🔙 Zurück zur Übersicht"):
    st.switch_page("pages/01_Datei.py")
