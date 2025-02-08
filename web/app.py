"""
Streamlit application for file processing and conversion.
Includes TXT to CSV, B1 processing, YouGlish search, and PDF tools.
"""

import io
from typing import List, Dict, Optional

import streamlit as st
import pandas as pd
import PyPDF2

from backend import (
    process_txt_file,
    add_style,
    process_txt_file_B1,
    find_id,
    clean_word,
    convert_results_to_csv,
    excel_to_bilingual_srt
)

def main():
    """Main function for the Streamlit application."""
    st.title("TXT to CSV/Excel Converter")
    tabs = st.tabs(["TXT to CSV/Excel",
                    "B1",
                    "YouGlish Search",
                    "PDF Tools",
                    "excel_to_srt"
                    ])
    
    df = None

    with tabs[0]:
        handle_txt_to_csv_tab()

    with tabs[1]:
        handle_b1_tab()

    with tabs[2]:
        handle_youglish_tab()

    with tabs[3]:
        handle_pdf_tab()

    with tabs[4]:
        excel_to_srt()

def handle_txt_to_csv_tab():
    """Handle the TXT to CSV conversion tab."""
    st.header("Convert TXT to CSV")
    uploaded_file = st.file_uploader(
        "Choose TXT file",
        type=["txt"],
        key="txt_uploader"
    )
    num_fields = st.number_input(
        "Enter number of fields (or auto)",
        min_value=1,
        value=8
    )
    
    if st.button("Convert"):
        process_txt_file_upload(uploaded_file, num_fields)

def process_txt_file_upload(uploaded_file, num_fields):
    """Process uploaded TXT file and convert to DataFrame."""
    if uploaded_file is None:
        st.warning("Please upload a TXT file before converting.")
        return

    try:
        content = uploaded_file.read().decode("utf-8")
        df = process_txt_file(content, num_fields).dropna(axis=1, how='all')
        
        st.write(f"Data will have {len(df.columns)} columns.")
        st.dataframe(df)
        
        create_download_button(df, uploaded_file.name)
    except ValueError as e:
        st.error(f"Error occurred: {e}. Please check the column count and data.")

def create_download_button(df, original_filename):
    """Create a download button for the DataFrame."""
    st.download_button(
        label="Download data as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"{original_filename.split('.')[0]}.csv",
        mime="text/csv",
    )

def handle_b1_tab():
    """Handle the B1 tab functionality."""
    st.header("B1 File Processing")
    
    uploaded_file = st.file_uploader(
        "Choose TXT file",
        type=["txt"],
        key="b1_txt_uploader"
    )
    
    if st.button("Process B1", key="process_b1_button"):
        if uploaded_file is None:
            st.warning("Please upload a TXT file before processing.")
            return
            
        try:
            content = uploaded_file.read().decode("utf-8")
            df = process_txt_file_B1(content)
            
            if df is not None and not df.empty:
                st.write("Processed Data:")
                st.dataframe(df)
                
                # Tạo nút download
                st.download_button(
                    label="Download B1 data as CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"B1_{uploaded_file.name.split('.')[0]}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No data was processed. Please check your input file.")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
def handle_youglish_tab():
    """Handle YouGlish search with multiple input methods."""
    st.header("YouGlish Search & Word Lookup")
    
    # Add upload youglish data section
    st.subheader("Upload YouGlish Data")
    youglish_file = st.file_uploader(
        "Upload YouGlish data file (CSV)",
        type=['csv'],
        key="youglish_data_uploader"
    )
    df = pd.DataFrame()  # Initialize empty DataFrame
    results = pd.DataFrame()  # Initialize empty results DataFrame
    
    
    df_youglish = None
    if youglish_file:
        try:
            df_youglish = pd.read_csv(youglish_file)
        except Exception as e:
            st.error(f"Error loading YouGlish data: {str(e)}")
            return
    
    search_col, result_col = st.columns([1, 2])
    
    with search_col:
        # Chọn phương thức input
        input_method = st.radio(
            "Choose input method:",
            ["Single Word", "Multiple Words", "Upload CSV"],
            key="input_method"
        )
        
        words_to_search = []
        
        if input_method == "Single Word":
            word = st.text_input(
                "Enter a word to search:",
                key="single_word"
            )
            if word:
                words_to_search = [word.strip()]
                
        elif input_method == "Multiple Words":
            text_input = st.text_area(
                "Enter words (one per line):",
                height=150,
                key="multiple_words",
                help="Enter one word per line"
            )
            if text_input:
                words_to_search = [word.strip() for word in text_input.splitlines() if word.strip()]
                
        else:  # Upload CSV
            uploaded_file = st.file_uploader(
                "Upload CSV file",
                type=['csv'],
                key="csv_uploader",
                help="CSV file should have a column named 'words' or 'word'"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    if 'words' in df.columns:
                        # Clean words before searching
                        df['words'] = df['words'].apply(clean_word)
                        words_to_search = df['words'].dropna().tolist()
                        st.success(f"Loaded {len(words_to_search)} words from CSV")
                    elif 'word' in df.columns:
                        # Clean words before searching
                        df['word'] = df['word'].apply(clean_word)
                        words_to_search = df['word'].dropna().tolist()
                        st.success(f"Loaded {len(words_to_search)} words from CSV")
                    else:
                        st.error("CSV must contain a column named 'words' or 'word'")
                except Exception as e:
                    st.error(f"Error reading CSV: {str(e)}")
        
        # Hiển thị số lượng từ sẽ tìm kiếm
        if words_to_search:
            st.write(f"Words to search: {len(words_to_search)}")
        
        # Nút tìm kiếm
        if st.button("Search", key="search_button", disabled=not words_to_search):
            try:
                with st.spinner('Searching...'):
                    progress_bar = st.progress(0)
                    total_words = len(words_to_search)
                    
                    # Process words in batches of 10 for better performance
                    batch_size = 10
                    results = pd.DataFrame()
                    
                    for i in range(0, total_words, batch_size):
                        batch = words_to_search[i:i + batch_size]
                        batch_results = find_id(batch, df_youglish)
                        results = pd.concat([results, batch_results])
                        
                        progress = min((i + batch_size) / total_words, 1.0)
                        progress_bar.progress(progress)
                        
                    progress_bar.empty()
                
                if not results.empty:
                    st.session_state.search_results = results
                    st.success(f"Found {len(results)} results!")
                else:
                    st.warning("No matches found.")
                    st.session_state.search_results = None
                    
            except Exception as e:
                st.error(f"Error during search: {str(e)}")
                st.session_state.search_results = None
    
    with result_col:
        if 'search_results' in st.session_state and st.session_state.search_results is not None:
            results = st.session_state.search_results
            
            # Clean words in results DataFrame
            if 'word' in results.columns:
                results['word'] = results['word'].apply(clean_word)
            elif 'words' in results.columns:
                results['words'] = results['words'].apply(clean_word)
            if 'word' in df.columns:
                df['word'] = df['word'].apply(clean_word)
            elif 'words' in df.columns:
                df['words'] = df['words'].apply(clean_word)
            
            if df is not None and not df.empty:
                merge_col = 'word' if 'word' in results.columns else 'words'
                results = df.merge(results, on=merge_col, how='left')
            
            successful_searches = results.dropna(subset=['video_id'])
            failed_searches = results[results['video_id'].isna()].drop(['video_id','video_title','start_second','end_second','caption'], axis=1)#axis=1 là cột
            
            if merge_col != 'word':
                failed_searches = failed_searches.rename(columns={merge_col: 'word'})

            # Display success/failure counts
            st.info(f"Successfully found videos for {len(successful_searches)} words")
            st.warning(f"Failed to find videos for {len(failed_searches)} words")

            col1, col2, col3 = st.columns(3)
            
            with col1:
                if not results.empty:
                    csv_all = results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download All Results", 
                        data=csv_all,
                        file_name="all_results.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if not successful_searches.empty:
                    csv_success = successful_searches.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Successful", 
                        data=csv_success,
                        file_name="successful_searches.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if not failed_searches.empty:
                    csv_failed = failed_searches.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Failed", 
                        data=csv_failed,
                        file_name="failed_searches.csv",
                        mime="text/csv"
                    )
            
            
            # Display results in a dataframe
            # st.dataframe(results)
            result_tabs = st.tabs(["All Results", "Successful", "Failed"])
            
            with result_tabs[0]:
                st.dataframe(results)
            with result_tabs[1]:
                st.dataframe(successful_searches)
            with result_tabs[2]:
                st.dataframe(failed_searches)

            # Display YouTube videos for each result
            # Only show first 2 results
            for _, row in successful_searches.head(2).iterrows():
                if pd.notna(row['video_id']):
                    st.write(f"**Word:** {row['word']}")
                    st.write(f"**Caption:** {row['caption']}")
                    
                    start_second = 0 if pd.isna(row['start_second']) else int(row['start_second'])
                    end_second = 10 if pd.isna(row['end_second']) else int(row['end_second'])
                    
                    video_url = f"https://www.youtube.com/embed/{row['video_id']}?start={start_second}&end={end_second}&autoplay=1&cc_load_policy=1"
                    
                    # Add reload button for each video
                    st.components.v1.iframe(video_url, width=400, height=300)
                    st.markdown("---")
            
            
            
            # Tạo DataFrame để download
            # if st.button("Download Results as CSV"):
            #     csv = convert_results_to_csv(results)
            #     st.download_button(
            #         label="Click to Download", 
            #         data=csv,
            #         file_name="youglish_results.csv",
            #         mime="text/csv"
            #     )


        
def handle_pdf_tab():
    """Handle PDF processing functionality."""
    st.header("PDF Tools")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        key="pdf_uploader",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        try:
            # Create lists to store PDF info
            pdf_files = []
            page_counts = []
            
            # Load PDFs and get page counts
            for uploaded_file in uploaded_files:
                pdf_bytes = io.BytesIO(uploaded_file.read())
                pdf_reader = PyPDF2.PdfReader(pdf_bytes)
                pdf_files.append({
                    'name': uploaded_file.name,
                    'bytes': pdf_bytes,
                    'pages': len(pdf_reader.pages)
                })
                page_counts.append(len(pdf_reader.pages))
            
            # Display PDF order selection
            st.subheader("Arrange PDF Order")
            pdf_order = []
            for i, pdf in enumerate(pdf_files):
                order = st.number_input(
                    f"Order for {pdf['name']} ({pdf['pages']} pages)",
                    min_value=1,
                    max_value=len(pdf_files),
                    value=i+1,
                    key=f"order_{i}"
                )
                pdf_order.append((order-1, pdf))
            
            # Sort PDFs by selected order
            pdf_order.sort(key=lambda x: x[0])
            ordered_pdfs = [item[1] for item in pdf_order]
            
            if st.button("Merge PDFs"):
                # Create merger with ordered PDFs
                merger = PyPDF2.PdfMerger()
                for pdf in ordered_pdfs:
                    pdf['bytes'].seek(0)
                    merger.append(pdf['bytes'])
                
                # Create merged PDF
                merged_pdf = io.BytesIO()
                merger.write(merged_pdf)
                merged_pdf.seek(0)
                
                # Preview merged PDF
                pdf_reader = PyPDF2.PdfReader(merged_pdf)
                num_pages = len(pdf_reader.pages)
                
                st.write(f"Merged PDF - Total pages: {num_pages}")
                
                # Allow viewing merged PDF pages
                page_number = st.number_input(
                    "Select page to preview:",
                    min_value=1,
                    max_value=num_pages,
                    value=1
                )
                
                if st.button("Preview Page"):
                    page = pdf_reader.pages[page_number - 1]
                    text_content = page.extract_text()
                    st.text_area(
                        "Page Content:",
                        value=text_content,
                        height=300
                    )
                
                # Download button for merged PDF
                st.download_button(
                    "Download Merged PDF",
                    data=merged_pdf.getvalue(),
                    file_name="merged.pdf",
                    mime="application/pdf"
                )
                    
        except Exception as e:
            st.error(f"Error processing PDFs: {str(e)}")
def excel_to_srt():
    st.header("excel/csv to srt")

    uploaded_file= st.file_uploader(
        "Choose files",
        type=["xlsx", "csv"],
        key="excel_uploader",
        accept_multiple_files=False
    )

    if uploaded_file:
        srt_content = excel_to_bilingual_srt(uploaded_file)

        if srt_content:
            st.success("✅ Chuyển đổi thành công!")

            # Hiển thị nội dung SRT
            st.text_area("📄 Xem trước file SRT:", value=srt_content, height=300)

            # Tạo file tạm để tải về
            output_file = "temp/output.srt"
            os.makedirs("temp", exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(srt_content)

            # Nút tải về file SRT
            with open(output_file, "rb") as f:
                st.download_button(
                    label="⬇ Tải về SRT",
                    data=f,
                    file_name="subtitles.srt",
                    mime="text/plain"
                )


if __name__ == "__main__":
    main()

    
