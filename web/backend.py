import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent


def search_youglish(word):
    # Thiết lập Chrome options
    ua = UserAgent()
    user_agent = ua.random

    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')  # Tắt GPU acceleration
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(f'user-agent={user_agent}')
    word = ('%20').join(word.split(' ')).replace('(','').replace(')','').split('/')[0]
    browser = webdriver.Chrome(options=chrome_options)
    print(word)
    browser.get(f"https://youglish.com/pronounce/{word}/english")

    # Đợi và click nút View All
    time.sleep(random.uniform(5, 10))
    button_viewall = browser.find_element(By.CLASS_NAME, "togglecaps")
    button_viewall.click()
    time.sleep(random.uniform(10, 13))
    source_code = browser.page_source
    soup = BeautifulSoup(source_code, 'html.parser')
    video_info = soup.find('iframe', id='player')
    video_id = video_info.get('src').split('?')[0].split('/')[-1]
    video_title = video_info.get('title')

    # Lấy caption và xử lý highlight
    caption = soup.find('div', id='r_caption')
    if caption:
        caption1 = (' ').join([cap.get_text() for cap in caption.findAll('span', class_='marker lg_0')])
        caption_raw = caption.get_text()
        if caption1 in caption_raw:
            print(caption1)
            cloze_sentence = caption.get_text().replace(caption1, f'<b>{caption1}</b>')
            # print(cloze_sentence)
        else:
            for cap in caption.findAll('span', class_='marker lg_0'):
                cap = cap.get_text()
                cloze_sentence = caption_raw.replace(cap, f'<b>{cap}</b>')
                caption_raw = cloze_sentence

    ac_current_cap = soup.find('li', class_='ac_current_cap')
    if ac_current_cap:
        id_current = int(ac_current_cap.get('id').split('_')[-1])
        start_second = soup.find('li', id=f'ac_{id_current}').get('data-start')
        next_cap = soup.find('li', id=f'ac_{str(id_current + 1)}')
        end_second = next_cap.get('data-start') if next_cap else None
    browser.quit()

    return {
        'video_id': video_id,
        'video_title': video_title,
        'cloze_sentence': cloze_sentence,
        'start_second': start_second,
        'end_second': end_second
    }
def process_txt_file(content, num_fields):
        
    entries = [line.strip().strip('"').strip('"').split('\t') for line in content.split("\n") if line and not line.startswith('#')]

    # Khởi tạo danh sách để lưu trữ dữ liệu
    formatted_data = []
    for entry in entries:
        if entry[0].strip()[0].isalpha():
            entry_1 = []
            entry_1.extend([x.strip().strip('"').replace('""', '"') for x in entry])
        else:
            entry_1.extend([x.strip().strip('"') for x in entry])
        formatted_data.append(entry_1)

    # Sử dụng zip để kết hợp các mục từ và định nghĩa
    # for entry in zip(entries[::2], entries[1::2]):
    #     entry_1 = []
    #     entry_1.extend([x.strip().strip('"') for x in entry[0]])
    #     entry_1.extend([x.strip().strip('"') for x in entry[1]])  # Lấy cặp mục từ và định nghĩa
    #     formatted_data.append(entry_1)

        # Tạo DataFrame
    columns = [f'Field {i+1}' for i in range(num_fields)]
    df = pd.DataFrame(formatted_data, columns=columns)
    df = add_style(df)
    return df


def process_txt_file_B1(content, num_fields):
    entries = [line.strip('"').strip('"').split('\t') for line in content.split("\n") if line and not line.startswith('#')]

    formatted_data = []
    # for entry in entries:
    #     print((len(entry)))
    # Sử dụng zip để kết hợp các mục từ và định nghĩa
    for entry in entries:
        if entry[0].strip().startswith('Destination B1'):
            entry_1 = []
            entry_1.extend([x.strip().strip('"').replace('""', '"') for x in entry])
        else:
            entry_1.extend([x.strip().strip('"') for x in entry])
        formatted_data.append(entry_1)

    # Tạo DataFrame
    columns = ['Deck', 'word']
    columns.extend(f'Field {i + 1}' for i in range(num_fields - 2))
    df = pd.DataFrame(formatted_data, columns=columns).drop_duplicates()
    df = add_style(df)
    return df

def add_style(df, style = None):
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
    if style:
        stl = style
    for field in df.columns:
        if df[field].str.startswith("<span").any():
            df[f'{field}'] = stl + df[f'{field}']
    return df
