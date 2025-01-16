# web anki

## 🌐 Live Demo
Access the application at: [Web LOR Tracy](https://weblortracy-ncdekzcpvbncguwr7z3hbj.streamlit.app/)

## 🚀 Features
- Data processing and analysis tools
- Redis database integration
- File upload and processing capabilities
- Interactive data visualization

## 🛠️ Technologies Used
- Python 3.10
- Streamlit
- Redis
- Pandas
- NumPy

## 📦 Installation
To run this project locally:

1. Clone the repository
bash
git clone https://github.com/Thuylt185411/web_lor_tracy.git
cd web_lor_tracy

2. Install dependencies
bash
pip install -r requirements.txt

3. Run the application
bash
streamlit run app.py    

## ✨ Features

### 1. TXT to CSV/Excel Converter
- Convert TXT files to CSV format
- Customizable field number
- Automatic column detection
- Download processed files in CSV format

### 2. B1 File Processing
- Specialized processing for B1 format files
- Data validation and formatting
- Export results to CSV

### 3. YouGlish Search
- Search words in YouGlish database
- Multiple input methods:
  - Single word search
  - Multiple words search
  - CSV file upload
- YouTube video integration
- View captions and video timestamps
- Export search results

### 4. PDF Tools
- Merge multiple PDF files
- Customize PDF merge order
- Preview merged PDF pages
- Extract text content
- Download merged PDFs

## 💡 Usage

### TXT to CSV Conversion
1. Upload a TXT file
2. Enter the number of fields (or use auto-detection)
3. Click "Convert"
4. Download the processed CSV file

### YouGlish Search
1. Upload YouGlish data (CSV format)
2. Choose input method:
   - Single word
   - Multiple words
   - CSV file upload
3. Click "Search"
4. View results and embedded YouTube videos
5. Download search results

### PDF Merging
1. Upload multiple PDF files
2. Arrange the merge order
3. Preview merged pages
4. Download the merged PDF



## 📁 Project Structure
- web/app.py: Main Streamlit application
- web/backend.py: Backend logic for data processing
- web/data: Directory for storing data files
- web/requirements.txt: Project dependencies
- run.ipynb: Jupyter notebook for testing and development

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

