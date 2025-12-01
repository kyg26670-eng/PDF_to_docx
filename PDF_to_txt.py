import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO

st.set_page_config(
    page_title="이미지 병합기",
    page_icon="🖼️",
    layout="wide"
)

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

    else:  # vertical
        max_width = max(widths)
        total_height = sum(heights)
        merged_img = Image.new("RGB", (max_width, total_height), (255, 255, 255))

        y_offset = 0
        for img in images:
            merged_img.paste(img, (0, y_offset))
            y_offset += img.height

    return merged_img

def main():
    st.title("🧩 이미지 병합기 (가로/세로)")

    uploaded_files = st.file_uploader(
        "이미지를 업로드하세요 (여러 개 선택 가능)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write("📌 업로드한 이미지 미리보기:")

        cols = st.columns(len(uploaded_files))
        images = []

        for i, uf in enumerate(uploaded_files):
            try:
                img = Image.open(uf)

                # ⭐ EXIF 회전 자동 보정
                img = ImageOps.exif_transpose(img)
                img = img.convert("RGB")

                images.append(img)
                cols[i].image(
                    img,
                    caption=uf.name,
                    use_column_width=True
                )
            except Exception as e:
                st.error(f"❌ {uf.name} 이미지 로드 실패: {e}")

        st.write("합치는 방향을 선택하세요👇")
        direction = st.radio("방향 선택", ["가로", "세로"], horizontal=True)
        dir_value = "horizontal" if direction == "가로" else "vertical"

        if st.button("✨ 이미지 병합"):
            merged_image = merge_images(images, dir_value)

            st.success("🎉 병합 완료!")
            st.image(merged_image, caption="합쳐진 이미지", use_column_width=True)

            img_bytes = BytesIO()
            merged_image.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            st.download_button(
                label="📥 병합 이미지 다운로드",
                data=img_bytes,
                file_name="merged_image.jpg",
                mime="image/jpeg"
            )

if __name__ == "__main__":
    main()
