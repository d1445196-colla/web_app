# 路由設計文件：語音轉寫與 API 整合系統

本文件根據 PRD、系統架構、流程圖與資料庫設計文件，規劃系統的所有 Flask 路由（Routes），包含 URL 路徑、HTTP 方法、輸入輸出與對應的 Jinja2 模板。

---

## 1. 路由總覽表格

系統路由分為兩組 Blueprint：**upload**（音訊上傳）與 **transcription**（轉寫結果）。

| # | 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|:---:|---|:---:|---|---|---|
| 1 | 首頁 / 上傳頁面 | `GET` | `/` | `transcriptions/upload.html` | 顯示音訊上傳表單與使用說明 |
| 2 | 提交音訊上傳 | `POST` | `/upload` | *(JSON 回應)* | 接收音訊檔案與 Markers，觸發轉寫流程 |
| 3 | 查詢轉寫狀態 | `GET` | `/transcriptions/<id>/status` | *(JSON 回應)* | 供前端輪詢，回傳處理狀態 |
| 4 | 查看轉寫結果 | `GET` | `/transcriptions/<id>` | `transcriptions/result.html` | 顯示逐字稿、時間軸與標記對齊結果 |
| 5 | 轉寫歷史紀錄 | `GET` | `/transcriptions` | `transcriptions/history.html` | 列出所有錄音紀錄與處理狀態 |
| 6 | 刪除錄音紀錄 | `POST` | `/transcriptions/<id>/delete` | *(重導向)* | 刪除紀錄後重導向回歷史列表 |

---

## 2. 每個路由的詳細說明

### 路由 1：首頁 / 上傳頁面

| 項目 | 說明 |
|---|---|
| **URL** | `GET /` |
| **功能** | 顯示音訊上傳表單頁面 |
| **輸入** | 無 |
| **處理邏輯** | 直接渲染上傳頁面模板 |
| **輸出** | 渲染 `transcriptions/upload.html` |
| **錯誤處理** | 無 |

---

### 路由 2：提交音訊上傳

| 項目 | 說明 |
|---|---|
| **URL** | `POST /upload` |
| **功能** | 接收音訊檔案與即時標記資料，進行驗證後觸發 Whisper 轉寫流程 |
| **輸入** | `multipart/form-data`：`audio_file`（音訊檔案）、`markers`（JSON 字串，標記陣列） |
| **處理邏輯** | 1. 呼叫 `FileValidator.validate()` 驗證檔案（大小、副檔名、MIME）<br>2. 以 UUID 重新命名後儲存至 `instance/uploads/`<br>3. 呼叫 `Recording.create()` 建立紀錄（status=pending）<br>4. 更新狀態為 `processing`<br>5. 呼叫 `WhisperClient.transcribe()` 串接 API<br>6. 呼叫 `Segment.bulk_create()` 儲存轉寫段落<br>7. 呼叫 `TimelineAlign.align()` 對齊 Markers<br>8. 呼叫 `Marker.bulk_create()` 儲存對齊結果<br>9. 更新狀態為 `completed` |
| **輸出** | 成功：`202 Accepted`，回傳 `{"recording_id": <id>, "status": "processing"}`<br>轉寫完成後狀態由輪詢取得 |
| **錯誤處理** | 未上傳檔案 → `400`（缺少音訊檔案）<br>檔案驗證失敗 → `400`（具體錯誤訊息）<br>Whisper API 金鑰無效 → `401`<br>API 額度不足 → `429`<br>API 逾時 → `504`<br>API 不可用 → `503` |

---

### 路由 3：查詢轉寫狀態

| 項目 | 說明 |
|---|---|
| **URL** | `GET /transcriptions/<id>/status` |
| **功能** | 供前端 JavaScript 輪詢轉寫處理進度 |
| **輸入** | URL 參數 `id`（錄音紀錄 ID） |
| **處理邏輯** | 呼叫 `Recording.get_by_id(id)` 查詢紀錄狀態 |
| **輸出** | `200 OK`，回傳 JSON：<br>`{"status": "processing"}` 或<br>`{"status": "completed"}` 或<br>`{"status": "failed", "error": "錯誤訊息"}` |
| **錯誤處理** | 紀錄不存在 → `404`（找不到此錄音紀錄） |

---

### 路由 4：查看轉寫結果

| 項目 | 說明 |
|---|---|
| **URL** | `GET /transcriptions/<id>` |
| **功能** | 顯示完整的轉寫結果頁面，包含逐字稿、時間軸與標記對齊 |
| **輸入** | URL 參數 `id`（錄音紀錄 ID） |
| **處理邏輯** | 1. 呼叫 `Recording.get_by_id(id)` 取得錄音紀錄<br>2. 呼叫 `Segment.get_by_recording_id(id)` 取得所有段落<br>3. 呼叫 `Marker.get_by_recording_id(id)` 取得所有標記 |
| **輸出** | 渲染 `transcriptions/result.html`，傳入 `recording`、`segments`、`markers` 資料 |
| **錯誤處理** | 紀錄不存在 → `404` 頁面<br>狀態為 `processing` → 重導向至上傳頁面並提示仍在處理中<br>狀態為 `failed` → 顯示錯誤訊息 |

---

### 路由 5：轉寫歷史紀錄

| 項目 | 說明 |
|---|---|
| **URL** | `GET /transcriptions` |
| **功能** | 列出所有錄音紀錄與處理狀態 |
| **輸入** | 無 |
| **處理邏輯** | 呼叫 `Recording.get_all()` 取得所有紀錄 |
| **輸出** | 渲染 `transcriptions/history.html`，傳入 `recordings` 列表 |
| **錯誤處理** | 無紀錄 → 顯示空狀態提示 |

---

### 路由 6：刪除錄音紀錄

| 項目 | 說明 |
|---|---|
| **URL** | `POST /transcriptions/<id>/delete` |
| **功能** | 刪除指定的錄音紀錄及其關聯資料（段落、標記），並刪除暫存的音訊檔案 |
| **輸入** | URL 參數 `id`（錄音紀錄 ID） |
| **處理邏輯** | 1. 呼叫 `Recording.get_by_id(id)` 確認紀錄存在<br>2. 刪除 `instance/uploads/` 中的音訊檔案<br>3. 呼叫 `Recording.delete(id)`（級聯刪除 segments 與 markers） |
| **輸出** | `302 Redirect` 至 `/transcriptions`（歷史列表頁面） |
| **錯誤處理** | 紀錄不存在 → `404` |

---

## 3. Jinja2 模板清單

所有模板都繼承 `base.html` 共用版型。

| 模板檔案 | 繼承自 | 用途說明 |
|---|---|---|
| `templates/base.html` | — | 共用版型：HTML 骨架、標題列、導覽列、CSS/JS 引入 |
| `templates/transcriptions/upload.html` | `base.html` | 音訊上傳頁面：檔案選擇器、Markers 輸入、上傳按鈕、進度指示 |
| `templates/transcriptions/result.html` | `base.html` | 轉寫結果頁面：逐字稿文字、每句時間戳、標記對齊高亮、返回按鈕 |
| `templates/transcriptions/history.html` | `base.html` | 歷史紀錄頁面：錄音列表表格（檔名、狀態、時間）、刪除按鈕 |

### 模板區塊規劃（base.html 定義的 block）

```
{% block title %}{% endblock %}      → 頁面標題
{% block content %}{% endblock %}    → 主要內容區
{% block scripts %}{% endblock %}    → 頁面專屬 JavaScript
```

---

## 4. 路由骨架程式碼

路由骨架檔案位於 `app/routes/`，每個函式只包含裝飾器、函式名稱與 docstring，不含實作邏輯。

- [`app/routes/__init__.py`](../app/routes/__init__.py) — Blueprint 註冊
- [`app/routes/upload.py`](../app/routes/upload.py) — 上傳相關路由（路由 1、2）
- [`app/routes/transcription.py`](../app/routes/transcription.py) — 轉寫結果相關路由（路由 3、4、5、6）
