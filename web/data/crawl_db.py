import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import argparse


def search_youglish_full(word):
    # Thiết lập Chrome options
    ua = UserAgent()
    user_agent = ua.random

    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')  # Tắt GPU acceleration
    chrome_options.add_argument('--disable-software-rasterizer')
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(f'user-agent={user_agent}')
    list_w = ['sb', 'st', '<div', '<span', '(', ')', '<', '>']
    for w in list_w:
        word = word.replace(w, '').replace('  ',' ')
    word = ('%20').join(word.split('/')[0].split(' ')).replace('(','').replace(')','').split('/')[0]
    browser = webdriver.Chrome(options=chrome_options)
    print(word)
    browser.get(f"https://youglish.com/pronounce/{word}/english")

    # Đợi và click nút View All
    time.sleep(random.uniform(8, 10))
    button_viewall = browser.find_element(By.CLASS_NAME, "togglecaps")
    if button_viewall:
        button_viewall.click()
    else:
        time.sleep(random.uniform(5, 10))
        print("No button viewall")
        return None
    time.sleep(random.uniform(10, 13))
    source_code = browser.page_source
    soup = BeautifulSoup(source_code, 'html.parser')
    video_info = soup.find('iframe', id='player')
    video_id = video_info.get('src').split('?')[0].split('/')[-1]
    video_title = video_info.get('title')

    all_caption = soup.find('div', id='ac_data')
    list_start = []
    list_end = []
    list_caption = []
    # all_caption
    if all_caption:
        for cap in all_caption.findAll('li'):
            id_current = int(cap.get('id').split('_')[-1])
            start_second = int(soup.find('li', id=f'ac_{id_current}').get('data-start')) - 1
            next_cap = soup.find('li', id=f'ac_{str(id_current + 1)}')
            end_second = int(next_cap.get('data-start')) +2 if next_cap else None
            list_start.append(start_second)
            list_end.append(end_second)
            list_caption.append(cap.get_text())

    video_id = [video_id for i in range(0, len(list_start))]
    video_title = [video_title for i in range(0, len(list_start))]
    browser.quit()

    return {
        'video_id': video_id,
        'video_title': video_title,
        'start_second': list_start,
        'end_second': list_end,
        'caption': list_caption
    }

def main():
    """
    Main function to crawl YouGlish data for a list of words.
    
    This script takes an input CSV file containing words to search on YouGlish,
    crawls the pronunciation data for each word, and saves the results to output files.
    
    Example usage:
        python crawl_db.py --input words.csv --output results.csv --error-output errors.csv
        
    Input CSV format:
        word
        hello
        world
        example
        
    Output CSV format:
        video_id,video_title,start_second,end_second,caption
        abc123,Title 1,10,15,"Hello everyone"
        def456,Title 2,20,25,"World news today"
    
    Error output CSV format:
        word
        difficult_word1
        error_word2
    """
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Crawl YouGlish data for words')
    parser.add_argument('--input', type=str, required=True, help='Input CSV file containing words to search')
    parser.add_argument('--output', type=str, default='youglish_full.csv', help='Output CSV file for results')
    parser.add_argument('--error-output', type=str, default='error_words.csv', help='Output CSV file for error words')
    args = parser.parse_args()

    # Read input words from CSV
    df = pd.read_csv(args.input)
    words_to_search = df['word'].tolist()
    print(words_to_search)
    all_results = []
    error_words = []
    df_youglish = None

    # Process each word
    for i, word in enumerate(words_to_search):
        try:
            # Search YouGlish for the current word
            result = search_youglish_full(word)
            
            # Initialize or append to results dataframe
            if df_youglish is None:
                df_youglish = pd.DataFrame(result)
            else:
                df_youglish = pd.concat([df_youglish, pd.DataFrame(result)])
        except Exception as e:
            print(f"Error processing {word}: {e}")
            error_words.append(word)
            continue
        
        # Save intermediate results every 100 words
        if i % 100 == 0 and i != 0:
            print(f"Processed {i} words")
            # Remove entries containing applause
            df_youglish = df_youglish[~df_youglish['caption'].str.contains('\(Applause\)', case=False, na=False)]
            # Save results and error words
            df_youglish.to_csv(args.output, index=False)
            pd.DataFrame({'word': error_words}).to_csv(args.error_output, index=False)

if __name__ == '__main__':
    main()
