import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO

# ---------------------- UI CONFIG ----------------------
st.set_page_config(
    page_title="이미지 병합기",
    page_icon="🖼️",
    layout="wide"
)

custom_css = """
<style>
    .main-title {
        font-size: 42px !important;
        font-weight: 800 !important;
        text-align: center !important;
        color: #5A5DF0 !important;
        margin-bottom: 10px !important;
    }
    .sub-text {
        text-align: center !important;
        font-size: 18px !important;
        color: #555 !important;
        margin-bottom: 30px !important;
    }
    .uploaded-img {
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 12px;
    }
    .merged-img {
        border-radius: 20px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.25);
        margin-top: 20px;
    }
    button[data-baseweb="button"] {
        border-radius: 12px !important;
        font-size: 18px !important;
        height: 48px !important;
        font-weight: 600 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------- FUNCTIONS ----------------------
def merge_images(images, direction="horizontal"):
    widths, heights = zip(*(img.size for img in images))

    if direction == "horizontal":
        total_width = sum(widths)
        max_height = max(heights)
        merged_img = Image.new("RGB", (total_width, max_height), (255, 255, 255))

        x_offset = 0
        for img in images:
            merged_img.paste(img, (x_offset, 0))
            x_offset += img.width

    else:  
        max_width = max(widths)
        total_height = sum(heights)
        merged_img = Image.new("RGB", (max_width, total_height), (255, 255, 255))

        y_offset = 0
        for img in images:
            merged_img.paste(img, (0, y_offset))
            y_offset += img.height

    return merged_img

# ---------------------- MAIN APP ----------------------
st.markdown('<div class="main-title">✨ 이미지 병합기 ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">가로/세로 원하는 방식으로 이미지를 한 번에 합쳐보세요!</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "이미지 업로드",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.subheader("📌 업로드한 이미지 미리보기")

    cols = st.columns(len(uploaded_files))
    images = []

    for i, uf in enumerate(uploaded_files):
        try:
            img = Image.open(uf)
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")

            images.append(img)
            cols[i].image(img, use_column_width=True, caption=uf.name, output_format="JPEG", clamp=True)
        except:
            st.error(f"⚠️ {uf.name}은(는) 열 수 없는 이미지입니다.")

    st.write(" ")

    # UI 개선 👉 컬럼 정렬
    left, right = st.columns([1, 1])

    with left:
        st.write("📌 병합 방향 선택")
        direction = st.radio("", ["가로", "세로"], horizontal=True)
        dir_value = "horizontal" if direction == "가로" else "vertical"

    with right:
        process = st.button("🎯 이미지 병합 실행")

    if process:
        merged_image = merge_images(images, dir_value)

        st.success("🎉 병합 성공!")
        st.image(merged_image, use_column_width=True, caption="✨ 병합된 이미지", output_format="JPEG", clamp=True)

        img_bytes = BytesIO()
        merged_image.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        st.download_button(
            label="📥 병합 이미지 다운로드",
            data=img_bytes,
            file_name="merged_image.jpg",
            mime="image/jpeg"
        )
