import streamlit as st
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


# --------------------------------------
# 디자인 옵션
# --------------------------------------
st.set_page_config(
    page_title="PDF Merge & TOC App",
    page_icon="📚",
    layout="wide"
)

primary_color = "#4A6CF7"
accent_color = "#3BD16F"

st.markdown(
    f"""
    <style>
    .main {{
        background-color: #F8F9FB;
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border-radius: 12px;
        padding: 12px 20px;
        font-size: 16px;
        border: none;
    }}
    .stDownloadButton>button {{
        background-color: {accent_color};
        color: black;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px 18px;
        border: none;
        font-size: 16px;
    }}
    .stFileUploader {{
        border: 2px dashed #D0D5DD !important;
        background: white !important;
        padding: 20px;
        border-radius: 14px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------
# 목차 PDF 생성
# --------------------------------------
def create_toc_page(entries):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 22)
    c.drawString(72, height - 72, "📑 Table of Contents")

    c.setFont("Helvetica", 13)
    y = height - 110

    link_positions = []
    for i, entry in enumerate(entries, start=1):
        line = f"{i}. {entry['title']}  →  p.{entry['start_page']}"
        c.drawString(85, y, line)
        link_positions.append(y)
        y -= 22

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue(), link_positions, width


# --------------------------------------
# PDF 병합 함수
# --------------------------------------
def merge_pdfs_with_toc(uploaded_files):
    pdf_infos, current_page, entries = [], 1, []

    for f in uploaded_files:
        r = PdfReader(f)
        pdf_infos.append({"name": f.name, "reader": r, "num_pages": len(r.pages)})

    for info in pdf_infos:
        entries.append({"title": info["name"], "start_page": current_page + 1})
        current_page += info["num_pages"]

    toc_bytes, link_positions, toc_width = create_toc_page(entries)
    toc_reader = PdfReader(BytesIO(toc_bytes))

    writer = PdfWriter()
    for p in toc_reader.pages: writer.add_page(p)

    start_indices = []
    for info in pdf_infos:
        idx = len(writer.pages)
        start_indices.append(idx)
        for page in info["reader"].pages:
            writer.add_page(page)

    for info, idx in zip(pdf_infos, start_indices):
        writer.add_outline_item(info["name"], idx)

    for i, y in enumerate(link_positions):
        rect = (72, y - 5, toc_width - 72, y + 10)
        writer.add_annotation(0, Link(rect=rect, target_page_index=start_indices[i]))

    out = BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()


# --------------------------------------
# GUI 구성
# --------------------------------------
st.markdown("<h1 style='text-align:center;'>📚 PDF Merge + Clickable TOC</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Upload PDFs → Merge → Download!</p>", unsafe_allow_html=True)
st.write("")

with st.container():
    st.subheader("📂 Upload Your PDFs")
    uploaded_files = st.file_uploader(
        "Upload 2 or more PDF files",
        type=["pdf"], accept_multiple_files=True
    )

if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda f: f.name)

    with st.expander("📄 Uploaded Files"):
        for uf in uploaded_files:
            st.write("•", uf.name)

    if len(uploaded_files) >= 2:
        if st.button("🚀 Generate Merged PDF"):
            with st.spinner("⏳ Merging PDFs & Creating TOC..."):
                merged_pdf = merge_pdfs_with_toc(uploaded_files)

            st.success("🎯 Completed Successfully!")
            st.download_button(
                "📥 Download PDF",
                merged_pdf,
                "merged_with_toc.pdf",
                "application/pdf"
            )
    else:
        st.warning("⚠️ Please upload at least **2 PDFs**")


st.sidebar.success("✨ Ready to merge your documents!")


