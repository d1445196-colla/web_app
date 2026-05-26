"""
WhisperClient — OpenAI Whisper API 呼叫封裝

負責與 OpenAI Whisper API 的串接，包含在地化 prompt 提示詞、
API 呼叫、回應解析與錯誤處理。

使用 verbose_json 格式取得每句的起止時間戳。
"""

import os
import requests
from flask import current_app

# Whisper API 端點
WHISPER_API_URL = 'https://api.openai.com/v1/audio/transcriptions'

# API 請求逾時秒數
API_TIMEOUT = 120

# 台灣在地化提示詞 — 提升國台語混雜場景的辨識精準度
LOCALIZED_PROMPT = (
    "以下是一段台灣的訪談錄音，內容可能包含國語與台語混雜的口語表達。"
    "常見的台語語助詞包括：齁、喔、啦、嘛、吼、蛤、厚、欸。"
    "可能出現的台灣地名：台北、新北、桃園、台中、台南、高雄。"
    "台灣慣用語：沒有啦、對啊、就是說、然後、基本上、所以說。"
)


class WhisperError(Exception):
    """Whisper API 呼叫時發生的錯誤。"""

    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def transcribe(audio_path, custom_prompt=None):
    """
    呼叫 OpenAI Whisper API 進行語音轉文字。

    Args:
        audio_path (str): 音訊檔案的完整路徑
        custom_prompt (str | None): 自訂提示詞，若為 None 則使用預設的在地化提示詞

    Returns:
        dict: 轉寫結果，包含：
            - text (str): 完整轉寫文字
            - segments (list[dict]): 每個段落含 segment_index, start_time, end_time, text
            - language (str): 偵測到的語言代碼
            - duration (float): 音訊總時長 (秒)

    Raises:
        WhisperError: API 呼叫失敗時拋出，含對應的 HTTP 狀態碼
    """
    api_key = current_app.config.get('OPENAI_API_KEY', '')
    if not api_key:
        raise WhisperError('未設定 OpenAI API 金鑰，請在 .env 檔案中設定 OPENAI_API_KEY', 401)

    prompt = custom_prompt or LOCALIZED_PROMPT

    try:
        with open(audio_path, 'rb') as audio_file:
            response = requests.post(
                WHISPER_API_URL,
                headers={
                    'Authorization': f'Bearer {api_key}',
                },
                files={
                    'file': (os.path.basename(audio_path), audio_file),
                },
                data={
                    'model': 'whisper-1',
                    'response_format': 'verbose_json',
                    'prompt': prompt,
                    'language': 'zh',
                },
                timeout=API_TIMEOUT,
            )
    except requests.exceptions.Timeout:
        raise WhisperError('語音辨識服務回應逾時，請稍後再試或上傳較短的音訊', 504)
    except requests.exceptions.ConnectionError:
        raise WhisperError('無法連線至語音辨識服務，請檢查網路連線', 503)
    except requests.exceptions.RequestException as e:
        raise WhisperError(f'API 請求發生未預期的錯誤：{e}', 500)

    # 處理 API 回應狀態碼
    if response.status_code == 401:
        raise WhisperError('API 金鑰無效或已過期，請確認 OPENAI_API_KEY 設定', 401)
    elif response.status_code == 429:
        raise WhisperError('API 額度不足或請求過於頻繁，請稍後再試', 429)
    elif response.status_code == 503:
        raise WhisperError('語音辨識服務暫時不可用，請稍後再試', 503)
    elif response.status_code != 200:
        error_detail = ''
        try:
            error_detail = response.json().get('error', {}).get('message', '')
        except Exception:
            error_detail = response.text[:200]
        raise WhisperError(f'語音辨識失敗 (HTTP {response.status_code})：{error_detail}', response.status_code)

    # 解析成功回應
    result = response.json()
    return _parse_response(result)


def _parse_response(api_response):
    """
    解析 Whisper API 的 verbose_json 回應。

    Args:
        api_response (dict): API 原始回應 JSON

    Returns:
        dict: 結構化的轉寫結果
    """
    segments = []
    raw_segments = api_response.get('segments', [])

    for idx, seg in enumerate(raw_segments):
        segments.append({
            'segment_index': idx,
            'start_time': round(seg.get('start', 0), 2),
            'end_time': round(seg.get('end', 0), 2),
            'text': seg.get('text', '').strip(),
        })

    # 計算音訊總時長（取最後一個 segment 的 end_time）
    duration = segments[-1]['end_time'] if segments else 0

    return {
        'text': api_response.get('text', ''),
        'segments': segments,
        'language': api_response.get('language', 'zh'),
        'duration': duration,
    }
