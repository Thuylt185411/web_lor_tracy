import streamlit as st
import pandas as pd
import io
from backend import process_txt_file, add_style, search_youglish, process_txt_file_B1


# Tiêu đề ứng dụng
st.title("Chuyển đổi TXT thành CSV và Excel")

# Tạo các tab
tabs = st.tabs(["TXT to CSV/Excel","B1", "YouGlish Search", "Style Options"])
df = []
# Tab đầu tiên: TXT to CSV
with tabs[0]:
    st.header("Chuyển đổi TXT thành CSV")
    # Tải lên tệp TXT
    uploaded_file = st.file_uploader("Chọn tệp TXT", type=["txt"], key="txt_uploader")
    num_fields = st.number_input("Nhập số trường cần có (hoặc để auto)", min_value=1, value=8)
    df = pd.DataFrame({})
    # Nút Convert
    if st.button("Convert"):
        if uploaded_file is not None:
            # Đọc nội dung tệp TXT
            content = uploaded_file.read().decode("utf-8")

            try:
            # Xử lý tệp TXT và tạo DataFrame
                df = process_txt_file(content, num_fields).dropna(axis=1, how='all')

                # Hiển thị số lượng cột
                st.write(f"Dữ liệu sẽ có {len(df.columns)} cột.")

                # Hiển thị DataFrame
                st.write("Dữ liệu đã được chuyển đổi thành DataFrame:")
                st.dataframe(df)
            except ValueError as e:
                st.error(f"Đã xảy ra lỗi: {e}. Vui lòng kiểm tra số lượng cột và dữ liệu trong tệp TXT.")
            # style_new = st.text_input("Style", "Type")
            # st.write("The current style", style_new)
            # if style_new:
            #     df = add_style(df, style_new)
            #     st.dataframe(df)
            # else:
            #     df = add_style(df)
            #     st.dataframe(df)
            # drop = st.checkbox("Drop Columns with NaN")
            # if drop:
            #     df.dropna(axis=1, inplace=True)
            #     st.success("NaN columns have been removed.")
            #
            # st.subheader("Select Column to Add Custom Styling")
            # column_to_style = st.selectbox("Choose a column", df.columns)
            # if st.button("Apply Style"):
            #     df = add_style(df, column_to_style)
            #     st.success(f"Custom styling applied to column: {column_to_style}")
            # excel = df.to_excel(index=False, engine='openpyxl')
            # st.download_button("Tải về Excel", excel, "data.xlsx")
            st.download_button(
                label="Download data as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"{uploaded_file.name.split('.')[0]}.csv",
                mime="text/csv",
            )
            # st.download_button(
            #     label="Download data as excel",
            #     data=df.to_excel(index=False).encode('utf-8'),
            #     file_name=f"{uploaded_file.name}.csv",
            #     mime="text/csv",
            # )

        else:
            st.warning("Vui lòng tải lên tệp TXT trước khi nhấn Convert.")
with tabs[1]:
    st.header("B1")

    # Tải lên tệp TXT
    uploaded_file = st.file_uploader("Chọn tệp TXT", type=["txt"], key="txt_uploader_b1")
    num_fields = st.number_input("Nhập số trường cần có (hoặc để auto)", min_value=1, value=8, key="b1")

    # Nút Convert
    if st.button("Convert", key='convert_b1'):
        if uploaded_file is not None:
            # Đọc nội dung tệp TXT
            content = uploaded_file.read().decode("utf-8")
            df = []
            try:
                # Xử lý tệp TXT và tạo DataFrame
                df = process_txt_file_B1(content, num_fields)

                # Hiển thị số lượng cột
                st.write(f"Dữ liệu sẽ có {len(df.columns)} cột.")

                # Hiển thị DataFrame
                st.write("Dữ liệu đã được chuyển đổi thành DataFrame:")
                st.dataframe(df)
            except ValueError as e:
                st.error(f"Đã xảy ra lỗi: {e}. Vui lòng kiểm tra số lượng cột và dữ liệu trong tệp TXT.")

            st.download_button(
                label="Download data as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"{uploaded_file.name.split('.')[0]}.csv",
                mime="text/csv",
            )

        else:
            st.warning("Vui lòng tải lên tệp TXT trước khi nhấn Convert.")
# with tabs[2]:
#     st.header("Tìm kiếm trên YouGlish")
#
#     # Input có thể là text hoặc file CSV
#     search_type = st.radio("Chọn cách tìm kiếm:", ["Nhập từ", "Upload CSV"])
#
#     if search_type == "Nhập từ":
#         search_word = st.text_input("Nhập từ cần tìm", "")
#         words_to_search = [search_word] if search_word else []
#     else:
#         uploaded_file = st.file_uploader("Upload CSV file chứa danh sách từ", type=['csv'])
#         if uploaded_file:
#             df = pd.read_csv(uploaded_file)
#             words_to_search = df.iloc[:, 1].tolist()
#             st.write(f"Đã tải lên {len(words_to_search)} từ")
#
#     if st.button("Tìm kiếm"):
#         if words_to_search:
#             all_results = []
#
#             # Progress bar
#             progress_bar = st.progress(0)
#             for i, word in enumerate(words_to_search):
#                 try:
#                     with st.spinner(f'Đang tìm kiếm từ "{word}"...'):
#                         result = search_youglish(word)
#                         result['word'] = word
#                         all_results.append(result)
#
#                     # Update progress
#                     progress_bar.progress((i + 1) / len(words_to_search))
#
#                 except Exception as e:
#                     st.error(f"Lỗi khi tìm từ '{word}': {str(e)}")
#
#             if all_results:
#                 # Tạo DataFrame từ kết quả YouGlish
#                 df_youglish = pd.DataFrame(all_results)
#
#                 # Join với DataFrame gốc
#                 df_merged = pd.merge(
#                     df,
#                     df_youglish,
#                     on='word',
#                     how='left'
#                 )
#
#                 # Drop cột word (vì đã có trong df gốc)
#                 df_merged = df_merged.drop('word', axis=1).dropna(axis=1, how='all')
#
#                 # Hiển thị kết quả
#                 st.subheader("Kết quả sau khi join")
#                 st.dataframe(df_merged)
#
#                 # Buttons để download
#                 col1, col2 = st.columns(2)
#
#                 with col1:
#                     st.download_button(
#                         label="📥 Download CSV",
#                         data=df_merged.to_csv(index=False).encode('utf-8'),
#                         file_name="merged_results.csv",
#                         mime="text/csv",
#                     )
#
#
#                 # Preview videos
#                 st.subheader("Preview Videos")
#                 for result in all_results:
#                     video_url = f"https://youtube.com/watch?v={result['video_id']}&t={result['start_second']}"
#                     st.write(f"### Results for '{result['word']}'")
#                     st.write(f"**{result['video_title']}**")
#                     st.write(f"🎯 Câu ví dụ: {result['cloze_sentence']}")
#                     st.write(f"⏱ Thời gian: {result['start_second']}s - {result['end_second']}s")
#                     st.write(f"🔗 [Xem trên YouTube]({video_url})")
#                     st.write("---")
#
#             else:
#                 st.warning("Không tìm thấy kết quả nào.")
#         else:
#             st.warning("Vui lòng nhập từ hoặc upload file CSV.")
