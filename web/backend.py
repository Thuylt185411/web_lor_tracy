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

def clean_word(word: str) -> str:
    """
    Clean and format a word string by removing HTML tags and special characters.
    
    Args:
        word: Input string that may contain HTML tags and special characters
        
    Returns:
        Cleaned string with HTML tags and special characters removed
    """
    # Define regex pattern to match:
    # - HTML tags like <div>, </div>, <br>, </br>, <span>, </span>
    # - Parentheses and quotation marks
    html_and_special_chars = re.compile(r'</?(?:div|br/?|span)>|\(|\)|"')
    
    # Remove matched patterns and trim whitespace
    cleaned_word = html_and_special_chars.sub('', word).strip()
    return cleaned_word

def convert_results_to_csv(results: pd.DataFrame) -> str:
    """Convert results to CSV format."""
    # Chọn và sắp xếp lại các cột cho CSV
    csv_df = results[[
        'word', 'video_title', 'caption', 
        'start_second', 'end_second', 'video_id'
    ]]
    return csv_df.to_csv(index=False).encode('utf-8')


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
    """Create regex pattern for word boundary search.
    
    This function takes a phrase and creates a regex pattern that matches the exact phrase
    with word boundaries. It handles both single words and multi-word phrases.
    
    The \b in regex is a word boundary anchor that matches positions where one side is a word character 
    (like a letter, digit, or underscore) and the other side is not a word character (like whitespace, 
    punctuation, or start/end of string).
    
    For example:
    - "cat" with \b will match "cat" in "the cat sits" but not in "category"
    - Without \b, "cat" would match both "cat" and "category"
    
    Args:
        phrase (str): The word or phrase to create a pattern for
        
    Returns:
        str: A regex pattern string that will match the exact phrase with word boundaries
        
    Examples:
        >>> create_search_pattern("hello")
        '\\bhello\\b'  # Matches "hello" but not "hello123" or "ahello"
        >>> create_search_pattern("hello world") 
        '\\bhello\\s+world\\b'  # Matches "hello world" but not "helloworld"
    """
    # Split the phrase into individual words
    # phrase = max((p.strip() for p in phrase.strip().split('/')), key=len)
    words = phrase.split()
    
    
    # If phrase contains multiple words
    if len(words) > 1:
        # Create pattern that matches words separated by whitespace
        # \b = word boundary (matches between word char and non-word char)
        # \s+ = one or more whitespace characters
        # re.escape() escapes special regex characters in the words
        return r'\b' + r'\s+'.join(map(re.escape, words)) + r'\b'
        
    # For single words, just add word boundaries at start and end
    # This ensures we match the whole word, not parts of larger words
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


def process_txt_file_B1(content, num_fields = 10):
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


import pandas as pd
import re


def convert_time_to_srt_format(time_str):
    """
    Convert time formats like '0s', 'MM:SS', or 'HH:MM:SS' to 'HH:MM:SS,SSS'.
    Supports milliseconds if included in the input.
    """
    match_seconds = re.match(r"^(\d+)s$", time_str)
    match_milliseconds = re.match(r"^(\d+):(\d+):(\d+)\.(\d+)$", time_str)

    if match_seconds:
        seconds = int(match_seconds.group(1))
        hours, minutes = divmod(seconds, 3600)
        minutes, seconds = divmod(minutes, 60)
        milliseconds = 0
    elif match_milliseconds:
        hours, minutes, seconds, milliseconds = map(int, match_milliseconds.groups())
    else:
        time_parts = list(map(int, re.split("[:.]", time_str)))
        if len(time_parts) == 2:  # MM:SS
            minutes, seconds = time_parts
            hours, milliseconds = 0, 0
        elif len(time_parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = time_parts
            milliseconds = 0
        elif len(time_parts) == 4:  # HH:MM:SS.mmm
            hours, minutes, seconds, milliseconds = time_parts
        else:
            raise ValueError(f"Invalid time format: {time_str}")

    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def excel_to_bilingual_srt(uploaded_file):
    """
    Xử lý file Excel/CSV và chuyển thành phụ đề SRT
    """
    file_name = uploaded_file.name
    if file_name.endswith(".xlsx"):
        data = pd.read_excel(uploaded_file)
    elif file_name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        raise ValueError("File không đúng định dạng .xlsx hoặc .csv")

    # Ensure necessary columns are present
    required_columns = {"Time", "Subtitle", "Machine Translation"}
    if not required_columns.issubset(data.columns):
        raise ValueError(f"Excel file must have columns: {required_columns}")

    # Clean the data
    data = data[["Time", "Subtitle", "Machine Translation"]].dropna()

    # Convert times to SRT format
    try:
        data["Start Time"] = data["Time"].apply(convert_time_to_srt_format)
    except ValueError as e:
        raise ValueError(f"Error in time conversion: {e}")

    # Calculate End Times
    duration = 2  # Default duration in seconds
    end_times = []
    for i in range(len(data)):
        start_time = data["Start Time"].iloc[i]
        if i < len(data) - 1:
            end_time = data["Start Time"].iloc[i + 1]
        else:
            # Add a fixed duration for the last subtitle
            h, m, s, ms = map(int, re.split(r"[:.,]", start_time))
            end_seconds = (h * 3600 + m * 60 + s + duration) * 1000 + ms
            h, remainder = divmod(end_seconds, 3600000)
            m, remainder = divmod(remainder, 60000)
            s, ms = divmod(remainder, 1000)
            end_time = f"{h:02}:{m:02}:{s:02},{ms:03}"
        end_times.append(end_time)

    data["End Time"] = end_times

    # Write to SRT file
    srt_content = ""
    for i, row in data.iterrows():
        srt_content += f"{i + 1}\n"
        srt_content += f"{row['Start Time']} --> {row['End Time']}\n"
        srt_content += f"{row['Subtitle']}\n"
        # srt_content += f"{row['Machine Translation']}\n\n"

    return srt_content







