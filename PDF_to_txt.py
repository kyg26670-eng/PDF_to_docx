import streamlit as st
from PIL import Image
from io import BytesIO

def merge_images(images, mode="horizontal"):
    # images: PIL Image 객체들의 리스트
    # mode: "horizontal" or "vertical"
    if not images:
        return None

    # 모두 같은 너비 또는 높이에 맞추기: 첫 이미지 기준
    widths, heights = zip(*(img.size for img in images))

    if mode == "horizontal":
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new('RGB', (total_width, max_height), (255,255,255))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
    else:  # vertical
        max_width = max(widths)
        total_height = sum(heights)
        new_im = Image.new('RGB', (max_width, total_height), (255,255,255))
        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]

    return new_im

def main():
    st.set_page_config(page_title="Image Merger", page_icon="🖼️")

    st.title("🖼️ 이미지 병합 앱")
    st.write("여러 이미지를 업로드하면, 하나의 이미지로 합쳐줍니다.")

    uploaded_files = st.file_uploader(
        "이미지 파일을 여러 개 선택하세요.",
        type=["png","jpg","jpeg","bmp"],
        accept_multiple_files=True
    )

    mode = st.radio("합치는 방향 선택", ("가로", "세로"))

    if uploaded_files:
        images = []
        for uf in uploaded_files:
            try:
                img = Image.open(uf)
                images.append(img.convert("RGB"))
            except Exception as e:
                st.error(f"⚠️ {uf.name} 파일을 이미지로 열 수 없습니다.")

        if images:
            if st.button("🧩 이미지 병합"):
                with st.spinner("합치는 중..."):
                    merged = merge_images(images, mode="horizontal" if mode=="가로" else "vertical")
                    if merged:
                        buf = BytesIO()
                        merged.save(buf, format="JPEG")
                        buf.seek(0)
                        st.image(merged, caption="✅ 병합된 이미지", use_column_width=True)
                        st.download_button(
                            label="📥 병합 이미지 다운로드",
                            data=buf,
                            file_name="merged_image.jpg",
                            mime="image/jpeg"
                        )
                    else:
                        st.error("이미지 병합에 실패했습니다.")

if __name__ == "__main__":
    main()


