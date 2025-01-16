import streamlit as st
import pandas as pd
from backend import process_txt_file, add_style, process_txt_file_B1, find_id
import PyPDF2
import io

def main():
    """Main function for the Streamlit application."""
    st.title("TXT to CSV/Excel Converter")

    tabs = st.tabs(["TXT to CSV/Excel", "B1", "YouGlish Search", "PDF Tools"])
    
    # Khởi tạo df là None thay vì list rỗng
    df = None

    with tabs[0]:
        handle_txt_to_csv_tab()

    with tabs[1]:
        handle_b1_tab()

    with tabs[2]:
        handle_youglish_tab()

    with tabs[3]:
        handle_pdf_tab()

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
    
    if youglish_file:
        try:
            df_youglish = pd.read_csv(youglish_file)
            st.success(f"Successfully loaded YouGlish data with {len(df_youglish)} entries")
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
                        words_to_search = df['words'].dropna().tolist()
                        st.success(f"Loaded {len(words_to_search)} words from CSV")
                    elif 'word' in df.columns:
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
                    results = find_id(words_to_search, df_youglish)
                
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
            merge_col = 'word' if 'word' in results.columns else 'words'
            results = df.merge(results, on=merge_col, how='left')

            
            # Display results in a dataframe
            st.dataframe(results)
            
            # Display YouTube videos for each result
            # Only show first 2 results
            for _, row in results.head(2).iterrows():
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
            if st.button("Download Results as CSV"):
                csv = convert_results_to_csv(results)
                st.download_button(
                    label="Click to Download",
                    data=csv,
                    file_name="youglish_results.csv",
                    mime="text/csv"
                )

def convert_results_to_csv(results: pd.DataFrame) -> str:
    """Convert results to CSV format."""
    # Chọn và sắp xếp lại các cột cho CSV
    csv_df = results[[
        'word', 'video_title', 'caption', 
        'start_second', 'end_second', 'video_id'
    ]]
    return csv_df.to_csv(index=False).encode('utf-8')
        
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

if __name__ == "__main__":
    main()

    
