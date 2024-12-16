import pandas as pd

def process_txt_file(content, num_fields):
        
    entries = [line.strip().strip('"').strip('"').split('\t') for line in content.split("\n") if line and not line.startswith('#')]

    # Khởi tạo danh sách để lưu trữ dữ liệu
    formatted_data = []

    # Sử dụng zip để kết hợp các mục từ và định nghĩa
    for entry in zip(entries[::2], entries[1::2]):
        entry_1 = []
        entry_1.extend(entry[0])  # Mục từ
        entry_1.extend(entry[1])  # Mục định nghĩa
        formatted_data.append(entry_1)  # Thêm vào danh sách kết quả

    # Tạo DataFrame
    columns = [f'Field {i+1}' for i in range(num_fields)]
    df = pd.DataFrame(formatted_data, columns=columns)
    df = add_style(df)
    return df

def add_style(df):
    stl = '''<style>
                div.phrasehead{margin: 2px 0;font-weight: bold;}
                span.star {color: #FFBB00;}
                span.pos, span.word-level, span.usage-info  {text-transform:lowercase; font-size:0.9em; margin-right:5px; padding:2px 4px; color:white; border-radius:8px;}
                span.pos {background-color:#0d47a1;}
                span.word-level {background-color: #1d2956; text-transform: uppercase;}
                span.usage-info {background-color: #f4d03f; color: #000;}
                span.tran {margin:0; padding:0;}
                span.eng_tran {margin-right:3px; padding:0;}
                ul.sents {font-size:0.8em; list-style:square inside; margin:3px 0;padding:5px;background:rgba(13, 175, 160, 0.1); border-radius:8px;}
                li.sent  {margin:0; padding:0;}
                span.eng_sent {margin-right:5px;}
            </style>'''
    for field in df.columns:
        if df[field].str.startswith("<span").any():
            df[f'{field}'] = stl + df[f'{field}']
    return df
