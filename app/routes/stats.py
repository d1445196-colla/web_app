"""
app/routes/stats.py
統計報表與 AI 摘要路由

Blueprint: stats_bp
負責收支趨勢圖表、統計資料與訪談摘要。
"""

import json
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify

# 導入 SQLAlchemy db（由 app/__init__.py 提供）
from flask import current_app

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/stats')
def index():
    """
    統計報表頁面

    GET /stats

    處理邏輯：
    1. 取得最近 6 個月的月份列表
    2. 對每個月呼叫 transaction.get_monthly_summary(year, month)
    3. 組合成圖表所需的資料格式（月份標籤、收入陣列、支出陣列）

    輸出：渲染 stats/index.html，傳入 monthly_data
    """
    pass


# ============================================================================
# F-03 AI摘要與報告產出 — 訪談逐字稿 AI 摘要服務
# ============================================================================

@stats_bp.route('/summary', methods=['POST'])
def generate_interview_summary():
    """
    POST /stats/summary
    
    F-03 功能路由：接收訪談逐字稿，透過 LLM 進行結構化摘要，並儲存回資料庫。
    
    【輸入】JSON 格式：
    {
        "interview_id": 1,
        "transcript": "訪談逐字稿文本..."
    }
    
    【處理流程】
    1. 驗證輸入（interview_id、transcript）
    2. 呼叫 LLM API 進行結構化分析
    3. 解析 LLM 回應，提取「訪談重點」、「核心結論」、「後續行動指南」
    4. 將摘要結果儲存回資料庫的 recording 表
    5. 回傳 JSON 格式的成功訊息與摘要內容
    
    【輸出】JSON 格式（成功時）：
    {
        "success": true,
        "message": "摘要已生成並儲存",
        "interview_id": 1,
        "summary": "整體摘要文本",
        "key_points": [...],
        "core_conclusion": "核心結論",
        "action_items": [...]
    }
    
    【輸出】JSON 格式（失敗時）：
    {
        "success": false,
        "error": "詳細錯誤訊息"
    }
    """
    try:
        # 1. 驗證輸入
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "未提供 JSON 資料"
            }), 400
        
        interview_id = data.get('interview_id')
        transcript = data.get('transcript', '').strip()
        
        # 驗證必填欄位
        if not interview_id:
            return jsonify({
                "success": False,
                "error": "缺少 interview_id"
            }), 400
        
        if not transcript:
            return jsonify({
                "success": False,
                "error": "逐字稿文本不能為空"
            }), 400
        
        # 2. 呼叫 LLM API 進行摘要
        ai_summary = _call_llm_for_summary(transcript)
        if not ai_summary:
            return jsonify({
                "success": False,
                "error": "LLM API 回應失敗，請稍後重試"
            }), 500
        
        # 3. 解析 LLM 回應
        structured_result = _parse_llm_summary(ai_summary)
        
        # 4. 儲存結果回資料庫
        try:
            _save_summary_to_database(interview_id, transcript, structured_result)
        except Exception as db_error:
            return jsonify({
                "success": False,
                "error": f"資料庫儲存失敗：{str(db_error)}"
            }), 500
        
        # 5. 回傳成功訊息
        return jsonify({
            "success": True,
            "message": "摘要已生成並儲存",
            "interview_id": interview_id,
            "summary": structured_result.get('summary', ''),
            "key_points": structured_result.get('key_points', []),
            "core_conclusion": structured_result.get('core_conclusion', ''),
            "action_items": structured_result.get('action_items', [])
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"伺服器錯誤：{str(e)}"
        }), 500


def _call_llm_for_summary(transcript: str) -> str:
    """
    呼叫 LLM API 進行訪談摘要
    
    支援的 LLM 提供者：
    - OpenAI (GPT-4 / GPT-3.5)
    - Azure OpenAI
    - 其他相容的 LLM API
    
    環境變數要求：
    - LLM_PROVIDER: 'openai' 或 'azure'（預設 'openai'）
    - LLM_API_KEY: API 金鑰
    - LLM_API_BASE: 自訂 API 端點（可選）
    - LLM_MODEL: 模型名稱（預設 'gpt-4'）
    """
    api_key = os.getenv('LLM_API_KEY')
    if not api_key:
        raise ValueError("未設定 LLM_API_KEY 環境變數")
    
    provider = os.getenv('LLM_PROVIDER', 'openai').lower()
    model = os.getenv('LLM_MODEL', 'gpt-4')
    api_base = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1')
    
    # 構建提示詞
    prompt = _build_summary_prompt(transcript)
    
    # 呼叫 OpenAI 相容的 API
    import requests
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': model,
        'messages': [
            {
                'role': 'system',
                'content': (
                    '你是一位專業的訪談分析師。'
                    '擅長從訪談逐字稿中提取核心重點、總結關鍵結論，'
                    '並建議後續的行動項目。'
                    '請以結構化的 JSON 格式回應，確保內容清晰易懂。'
                )
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        response = requests.post(
            f'{api_base}/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            current_app.logger.error(f"LLM API 錯誤：{response.status_code} - {response.text}")
            return None
        
        result = response.json()
        if 'choices' not in result or len(result['choices']) == 0:
            current_app.logger.error("LLM API 回應格式異常")
            return None
        
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.Timeout:
        current_app.logger.error("LLM API 請求超時")
        return None
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"LLM API 連線失敗：{str(e)}")
        return None


def _build_summary_prompt(transcript: str) -> str:
    """
    構建發送給 LLM 的提示詞，指導 LLM 進行結構化分析
    """
    prompt = f"""
    請深入分析以下訪談逐字稿，提取關鍵信息並產生結構化的摘要報告。
    
    【訪談逐字稿】
    ─────────────────────────────────────
    {transcript}
    ─────────────────────────────────────
    
    【分析要求】
    請依照以下結構產生 JSON 格式的分析結果（務必是有效的 JSON，不要包含其他文字）：
    
    {{
        "summary": "（必填）整體摘要，200-300 字以內，用繁體中文，簡潔明了地概括整個訪談的核心內容",
        "key_points": [
            "（必填，列舉 3-5 個最重要的觀點或發現）",
            "（每個重點應為單一完整句子）"
        ],
        "core_conclusion": "（必填）核心結論，100-150 字以內，用繁體中文，總結訪談對象的主要立場或建議",
        "action_items": [
            "（必填，列舉所有明確提到的後續行動項目或建議）",
            "（格式：動詞 + 具體內容，例如『進行市場調研』、『安排下次會面』）"
        ],
        "themes": [
            "（選填）訪談的主要主題或關鍵詞彙，最多 3 個）"
        ],
        "quote_highlights": [
            {{
                "quote": "（選填）精彩引用文字，需要完整且有代表性）",
                "context": "（該引用出現的情境或上下文）"
            }}
        ]
    }}
    
    【分析標準】
    1. 「key_points」應涵蓋訪談中的所有重要觀點，不要遺漏
    2. 「action_items」必須明確、可執行，並按優先級排序
    3. 「quote_highlights」應選擇最能代表訪談者立場的引用
    4. 所有文字應使用繁體中文，清晰易懂
    5. 回應只能是 JSON，不要包含任何解釋或其他文字
    """
    return prompt


def _parse_llm_summary(response_text: str) -> dict:
    """
    解析 LLM 回應的 JSON，提取結構化摘要
    """
    try:
        # 嘗試提取 JSON（LLM 可能會包含額外的文字）
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            current_app.logger.warning("LLM 回應中找不到 JSON，使用備用方案")
            # 備用方案：回傳預設結構
            return {
                'summary': response_text[:300],
                'key_points': [response_text],
                'core_conclusion': response_text[:150],
                'action_items': [],
                'themes': [],
                'quote_highlights': []
            }
        
        json_str = response_text[json_start:json_end]
        result = json.loads(json_str)
        
        # 驗證並填補必要字段
        default_structure = {
            'summary': '',
            'key_points': [],
            'core_conclusion': '',
            'action_items': [],
            'themes': [],
            'quote_highlights': []
        }
        
        for key in default_structure:
            if key not in result:
                result[key] = default_structure[key]
        
        return result
        
    except json.JSONDecodeError as e:
        current_app.logger.error(f"JSON 解析失敗：{str(e)}")
        # 回傳備用結構
        return {
            'summary': response_text[:300],
            'key_points': [response_text],
            'core_conclusion': response_text[:150],
            'action_items': [],
            'themes': [],
            'quote_highlights': []
        }


def _save_summary_to_database(interview_id: int, transcript: str, summary: dict) -> None:
    """
    將訪談逐字稿與 AI 摘要結果儲存回資料庫
    
    【需要的資料庫表結構】
    在 recording 表增加以下欄位：
    - transcript (TEXT) — 訪談逐字稿
    - summary (TEXT) — AI 摘要結果（JSON 格式）
    - summarized_at (TEXT) — 摘要生成時間戳
    
    【使用 SQLAlchemy ORM 時】：
    
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy()
        
        # 在 Recording 模型中增加欄位
        transcript = db.Column(db.Text)
        summary = db.Column(db.Text)  # 儲存 JSON 字串
        summarized_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # 在此函式中使用：
        recording = Recording.query.get(interview_id)
        recording.transcript = transcript
        recording.summary = json.dumps(summary, ensure_ascii=False)
        recording.summarized_at = datetime.utcnow()
        db.session.commit()
    
    【使用原生 SQLite3 時】（當前系統使用）：
    執行 SQL UPDATE 語句
    """
    
    # 【方案 A】使用 SQLAlchemy ORM（推薦）
    try:
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy()
        from app.models.recording import Recording  # 需要更新模型
        
        # 取得 recording 記錄
        recording = Recording.query.get(interview_id)
        if not recording:
            raise ValueError(f"找不到 ID 為 {interview_id} 的訪談記錄")
        
        # 更新欄位
        recording.transcript = transcript
        recording.summary = json.dumps(summary, ensure_ascii=False, indent=2)
        recording.summarized_at = datetime.utcnow()
        
        # 提交變更
        db.session.commit()
        current_app.logger.info(f"訪談 #{interview_id} 的摘要已儲存到資料庫")
        
    except ImportError:
        # 【方案 B】使用原生 SQLite3（備用）
        current_app.logger.warning("未找到 Flask-SQLAlchemy，使用原生 SQLite3")
        _save_summary_with_sqlite3(interview_id, transcript, summary)


def _save_summary_with_sqlite3(interview_id: int, transcript: str, summary: dict) -> None:
    """
    使用原生 SQLite3 儲存摘要（備用方案）
    
    【前置條件】
    recordings 表需要增加以下欄位：
    - transcript (TEXT)
    - summary (TEXT)
    - summarized_at (TEXT)
    """
    import sqlite3
    
    try:
        # 取得資料庫連線
        from app.models.database import DATABASE_PATH
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 準備數據
        summary_json = json.dumps(summary, ensure_ascii=False, indent=2)
        summarized_at = datetime.now().isoformat()
        
        # 執行 UPDATE
        cursor.execute("""
            UPDATE recordings 
            SET transcript = ?, summary = ?, summarized_at = ?
            WHERE id = ?
        """, (transcript, summary_json, summarized_at, interview_id))
        
        conn.commit()
        conn.close()
        
        current_app.logger.info(f"訪談 #{interview_id} 的摘要已儲存到資料庫（SQLite3）")
        
    except Exception as e:
        current_app.logger.error(f"SQLite3 儲存失敗：{str(e)}")
        raise
