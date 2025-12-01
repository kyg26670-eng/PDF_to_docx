import streamlit as st
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


# ------------------------------------
# 목차 페이지 생성 함수
# ------------------------------------
def create_toc_page(entries):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(72, height - 72, "📑 Table of Contents")

    c.setFont("Helvetica", 12)
    y = height - 110

    link_positions = []
    for i, entry in enumerate(entries, start=1):
        line = f"{i}. {entry['title']} - p. {entry['start_page']}"
        c.drawString(80, y, line)
        link_positions.append(y)
        y -= 18
        if y < 72:
            break

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue(), link_positions, width


# ------------------------------------
# PDF 병합 함수
# ------------------------------------
def merge_pdfs_with_toc(uploaded_files):
    pdf_infos = []
    for uf in uploaded_files:
        reader = PdfReader(uf)
        pdf_infos.append({"name": uf.name, "reader": reader, "num_pages": len(reader.pages)})

    entries = []
    current_page = 1
    for info in pdf_infos:
        entries.append({"title": info["name"], "start_page": current_page + 1})
        current_page += info["num_pages"]

    toc_pdf_bytes, link_positions, toc_page_width = create_toc_page(entries)
    toc_reader = PdfReader(BytesIO(toc_pdf_bytes))

    writer = PdfWriter()

    # TOC 추가
    for page in toc_reader.pages:
        writer.add_page(page)

    start_page_indices = []
    for info in pdf_infos:
        start_index = len(writer.pages)
        start_page_indices.append(start_index)
        for page in info["reader"].pages:
            writer.add_page(page)

    # Outline (북마크)
    for info, start_idx in zip(pdf_infos, start_page_indices):
        writer.add_outline_item(info["name"], start_idx)

    # 링크 추가
    for i, (entry, y) in enumerate(zip(entries, link_positions)):
        rect = (70, y - 2, toc_page_width - 70, y + 12)
        annotation = Link(rect=rect, target_page_index=start_page_indices[i])
        writer.add_annotation(page_number=0, annotation=annotation)

    result = BytesIO()
    writer.write(result)
    result.seek(0)
    return result.getvalue()


# ------------------------------------
# Streamlit UI
# ------------------------------------
def main():
    st.set_page_config(page_title="PDF 병합 & 목차 생성 앱", page_icon="📚", layout="centered")

    st.title("📚 PDF 병합 + 클릭 목차 생성")
    st.write("여러 PDF를 합치고, 첫 페이지에서 **클릭 가능한 목차**를 자동 생성합니다.")

    st.info("👉 최소 2개 이상의 PDF를 업로드하세요.")

    uploaded_files = st.file_uploader(
        "PDF 파일을 선택하세요 (여러 개 가능)",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        uploaded_files = sorted(uploaded_files, key=lambda x: x.name)

        st.subheader("📄 업로드된 파일 목록")
        for uf in uploaded_files:
            st.write(f"• {uf.name}")

        if len(uploaded_files) < 2:
            st.warning("⚠️ PDF는 최소 2개 이상이어야 병합할 수 있습니다.")
            return

        if st.button("🚀 병합 PDF 생성"):
            with st.spinner("PDF 병합 및 목차 생성 중..."):
                merged_pdf = merge_pdfs_with_toc(uploaded_files)

            st.success("🎉 병합 완료! 아래 버튼으로 다운로드하세요.")
            st.download_button(
                label="📥 PDF 다운로드",
                data=merged_pdf,
                file_name="merged_with_toc.pdf",
                mime="application/pdf"
            )


if __name__ == "__main__":
    main()

