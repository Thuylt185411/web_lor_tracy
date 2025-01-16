import pandas as pd
import redis
import re
import streamlit as st
import os

    # Redis Cloud connection
# redis_client = redis.Redis(
#     host='redis-11993.c228.us-central1-1.gce.redns.redis-cloud.com',
#     port=11993,
#     password=st.secrets["redis"]["REDIS_PASSWORD"],
#     decode_responses=True,
#     ssl=True
# )
# # redis_client.ping()


# print(redis_client.ping())
# def get_df_from_redis(key: str, redis_client: redis.Redis) -> pd.DataFrame | None:
#     """
#     Retrieve DataFrame from Redis by key.
    
#     Args:
#         key: Redis key to retrieve data
#         redis_client: Redis client instance
    
#     Returns:
#         DataFrame if data exists, None otherwise
#     """
    
#     json_data = redis_client.get(key)
#     if json_data is not None:
#         return pd.read_json(json_data, orient='records')
#     return None
    
# df = get_df_from_redis('youglish_data', redis_client)

current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct path to data file
data_path = os.path.join(current_dir, 'data', 'youglish_data.csv')

try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    df = pd.DataFrame()  # Create empty DataFrame if file not found
    print(f"Warning: Could not find {data_path}")


def search_words_in_df(phrases: str | list, df: pd.DataFrame) -> pd.DataFrame:
    """
    Search phrases in DataFrame and return one random result for each phrase.
    
    Args:
        phrases: Single phrase or list of phrases to search
        df: DataFrame containing the captions
    
    Returns:
        DataFrame with random matches including search words
    """
    if df is None or df.empty:
        return pd.DataFrame()
        
    if not isinstance(phrases, list):
        phrases = [phrases]
        
    results = []
    for phrase in phrases:
        pattern = create_search_pattern(phrase)
        matches = df[df['caption'].str.contains(
            pattern, 
            case=False, 
            na=False, 
            regex=True
        )]
        
        if not matches.empty:
            random_match = matches.sample(n=1)[
                ['video_id', 'video_title', 'start_second', 'end_second', 'caption']
            ]
            random_match['word'] = phrase
            results.append(random_match)
    
    return pd.concat(results).reset_index(drop=True) if results else pd.DataFrame()

def create_search_pattern(phrase: str) -> str:
    """Create regex pattern for word boundary search."""
    words = phrase.split()
    if len(words) > 1:
        return r'\b' + r'\s+'.join(map(re.escape, words)) + r'\b'
    return fr'\b{re.escape(phrase)}\b'



def find_id(words: str | list, dataframe: pd.DataFrame = None) -> pd.DataFrame:
    """
    Find IDs in the provided dataframe based on words.
    
    Args:
        words: String or list of words to search
        dataframe: DataFrame to search in
    
    Returns:
        pd.DataFrame: Filtered results
    """
    if dataframe is None:
        dataframe = df  # Use global df if no dataframe is provided
    
    return search_words_in_df(words, df=dataframe)

def process_txt_file(content, num_fields):
        
    entries = [line.strip().strip('"').strip('"').split('\t') for line in content.split("\n") if line and not line.startswith('#')]
    entry_1 = []
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
    entry_1 = []
    for entry in entries:
        if '::' in entry[0].strip():
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







