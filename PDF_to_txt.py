import fitz  # 🔍 PyMuPDF 추가


def extract_best_title(pdf_file):
    """
    PDF에서 가장 적절한 제목을 추출:
    1. 메타데이터 title
    2. 가장 큰 글자
    3. 파일명 fallback
    """

    try:
        doc = fitz.open(stream=pdf_file.getvalue(), filetype="pdf")

        # 1️⃣ 메타데이터 우선
        meta_title = doc.metadata.get("title")
        if meta_title and len(meta_title.strip()) >= 3:
            return meta_title.strip()

        # 2️⃣ 첫 3페이지에서 폰트 크기 기반 텍스트 스캔
        max_font_size = 0
        best_text = None

        for page_index in range(min(3, len(doc))):
            page = doc[page_index]
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            font_size = span["size"]
                            if text and font_size > max_font_size and len(text) <= 80:
                                max_font_size = font_size
                                best_text = text

        if best_text:
            return best_text.strip()

    except Exception:
        pass

    # 3️⃣ 그래도 없으면 파일명 사용
    name = pdf_file.name
    return name.rsplit(".", 1)[0]


