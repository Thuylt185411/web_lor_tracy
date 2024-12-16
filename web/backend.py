import pandas as pd

def process_txt_file(content, num_fields):
        
    entries = [line.strip().split('\t') for line in content.split("\n") if line and not line.startswith('#')]

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
    return df
