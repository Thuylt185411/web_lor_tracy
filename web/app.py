import streamlit as st
import pandas as pd
from backend import process_txt_file

# Tiêu đề ứng dụng
st.title("Chuyển đổi TXT thành CSV và Excel")

# Tạo các tab
tabs = st.tabs(["TXT to CSV", "Tab Khác"])  # Bạn có thể thêm nhiều tab khác ở đây

# Tab đầu tiên: TXT to CSV
with tabs[0]:
    st.header("Chuyển đổi TXT thành CSV")

    # Tải lên tệp TXT
    uploaded_file = st.file_uploader("Chọn tệp TXT", type=["txt"])
    num_fields = st.number_input("Nhập số trường cần có (hoặc để auto)", min_value=1, value=8)

    # Nút Convert
    if st.button("Convert"):
        if uploaded_file is not None:
            # Đọc nội dung tệp TXT
            content = uploaded_file.read().decode("utf-8")
            try:
            # Xử lý tệp TXT và tạo DataFrame
                df = process_txt_file(content, num_fields)
        
                # Hiển thị số lượng cột
                st.write(f"Dữ liệu sẽ có {len(df.columns)} cột.")

                # Hiển thị DataFrame
                st.write("Dữ liệu đã được chuyển đổi thành DataFrame:")
                st.dataframe(df)

                # Tùy chọn tải về
                download_format = st.selectbox("Chọn định dạng tải về", ["CSV", "Excel"])

                if st.button("Tải về"):
                    if download_format == "CSV":
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("Tải về CSV", csv, "data.csv", "text/csv")
                    elif download_format == "Excel":
                        excel = df.to_excel(index=False, engine='openpyxl')
                        st.download_button("Tải về Excel", excel, "data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except ValueError as e:
                st.error(f"Đã xảy ra lỗi: {e}. Vui lòng kiểm tra số lượng cột và dữ liệu trong tệp TXT.")
        else:
            st.warning("Vui lòng tải lên tệp TXT trước khi nhấn Convert.")

# Tab thứ hai: Tab Khác (có thể thêm chức năng khác ở đây)
with tabs[1]:
    st.header("Tab Khác")
    st.write("Bạn có thể thêm chức năng khác ở đây.")