# 流程圖設計文件：語音轉寫與 API 整合系統

本文件根據產品需求文件 (PRD) 與系統架構文件，視覺化使用者在語音轉寫系統中的操作流程、系統背後的處理步驟，以及功能與路由的對照表。

## 1. 使用者流程圖（User Flow）

以下流程圖說明使用者從開啟網頁到完成音訊上傳、等待轉寫、查看結果的完整操作路徑：

```mermaid
flowchart LR
    A([使用者開啟網站]) --> B[首頁 - 上傳音訊頁面]

    B --> C{選擇欲執行的功能}

    %% 上傳音訊路線
    C -->|選擇音訊檔案並上傳| D[選擇檔案 + 附帶 Markers]
    D --> E{前端初步檢查}
    E -->|檔案過大 / 格式不符| F[顯示錯誤提示]
    F --> B
    E -->|檢查通過| G[送出上傳請求]
    G --> H{後端驗證結果}
    H -->|驗證失敗| I[顯示後端錯誤訊息]
    I --> B
    H -->|驗證通過 - 202 Accepted| J[顯示處理中狀態]
    J --> K[前端輪詢轉寫進度]
    K --> L{轉寫是否完成?}
    L -->|處理中| K
    L -->|失敗| M[顯示失敗原因與建議]
    M --> B
    L -->|完成| N[跳轉至轉寫結果頁面]

    %% 查看轉寫結果路線
    C -->|查看歷史紀錄| O[轉寫歷史紀錄列表]
    O --> P[點擊某筆紀錄]
    P --> N

    %% 轉寫結果頁面操作
    N --> Q{在結果頁中選擇操作}
    Q -->|瀏覽逐字稿與時間軸| R[檢視完整轉寫內容]
    Q -->|點擊標記快速跳轉| S[定位至標記對應段落]
    Q -->|返回首頁| B
    Q -->|返回歷史紀錄| O
```

## 2. 系統序列圖（Sequence Diagram）

### 2.1 核心流程：音訊上傳與語音轉寫

以下序列圖展示從使用者上傳音訊到 Whisper API 完成轉寫、結果存入資料庫的完整過程：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (前端)
    participant Route as Flask Route (Controller)
    participant Validator as FileValidator (Service)
    participant Model as Model (資料操作)
    participant DB as SQLite 資料庫
    participant Whisper as WhisperClient (Service)
    participant API as OpenAI Whisper API
    participant Aligner as TimelineAlign (Service)

    User->>Browser: 選擇音訊檔案並附帶 Markers JSON，點擊上傳
    Browser->>Route: POST /upload (multipart/form-data)

    Note over Route, Validator: 階段一：檔案安全驗證
    Route->>Validator: validate(file) — 檢查大小、副檔名、MIME
    Validator-->>Route: 驗證結果

    alt 驗證失敗
        Route-->>Browser: 400 Bad Request (錯誤訊息)
        Browser-->>User: 顯示具體錯誤提示
    end

    Note over Route, DB: 階段二：建立錄音紀錄
    Route->>Model: Recording.create(filename, status=processing)
    Model->>DB: INSERT INTO recordings ...
    DB-->>Model: 回傳 recording_id
    Model-->>Route: recording_id

    Route-->>Browser: 202 Accepted (recording_id)
    Browser-->>User: 顯示「轉寫處理中」狀態

    Note over Route, API: 階段三：呼叫 Whisper API
    Route->>Whisper: transcribe(audio_path, prompt)
    Whisper->>API: POST /v1/audio/transcriptions
    Note right of API: response_format=verbose_json<br/>含在地化 prompt 提示詞
    API-->>Whisper: 回傳 JSON (text + segments[])

    alt API 呼叫失敗 (401/429/503/504)
        Whisper-->>Route: 拋出對應異常
        Route->>Model: Recording.update(status=failed, error_msg)
        Model->>DB: UPDATE recordings SET status='failed'
        Note over Browser: 前端輪詢時取得失敗狀態
    end

    Whisper-->>Route: 回傳解析後的 segments 列表

    Note over Route, DB: 階段四：儲存轉寫段落
    Route->>Model: Segment.bulk_create(recording_id, segments)
    Model->>DB: INSERT INTO segments (多筆)
    DB-->>Model: 寫入成功

    Note over Route, Aligner: 階段五：時間軸對齊
    Route->>Aligner: align(markers, segments)
    Aligner-->>Route: 對齊結果 (每個 Marker 對應的 segment_id)
    Route->>Model: Marker.bulk_create(recording_id, aligned_markers)
    Model->>DB: INSERT INTO markers (多筆)

    Note over Route, DB: 階段六：更新狀態為完成
    Route->>Model: Recording.update(status=completed)
    Model->>DB: UPDATE recordings SET status='completed'

    Note over Browser: 前端輪詢取得 completed 狀態
    Browser->>Route: GET /transcriptions/<recording_id>
    Route->>Model: 查詢 Recording + Segments + Markers
    Model->>DB: SELECT 關聯查詢
    DB-->>Model: 回傳完整資料
    Model-->>Route: 結構化資料
    Route-->>Browser: 渲染 result.html (逐字稿 + 時間軸 + 標記)
    Browser-->>User: 顯示轉寫結果頁面
```

### 2.2 輔助流程：前端狀態輪詢

```mermaid
sequenceDiagram
    participant Browser as 瀏覽器 (前端 JS)
    participant Route as Flask Route
    participant Model as Model
    participant DB as SQLite

    loop 每 3 秒輪詢一次
        Browser->>Route: GET /transcriptions/<id>/status
        Route->>Model: Recording.get_status(id)
        Model->>DB: SELECT status FROM recordings WHERE id=?
        DB-->>Model: status 值
        Model-->>Route: status

        alt status = processing
            Route-->>Browser: 200 OK {"status": "processing"}
            Note over Browser: 繼續顯示載入動畫
        else status = completed
            Route-->>Browser: 200 OK {"status": "completed"}
            Note over Browser: 停止輪詢，跳轉至結果頁
        else status = failed
            Route-->>Browser: 200 OK {"status": "failed", "error": "..."}
            Note over Browser: 停止輪詢，顯示錯誤訊息
        end
    end
```

## 3. 功能清單對照表

對應上述流程與 PRD 需求，以下為系統功能對應的 URL 路徑與 HTTP 方法整理，提供後續路由設計的參考：

| 功能項目說明 | HTTP 方法 | 預計對應的 URL 路徑 | View (Jinja2) | 備註 |
| --- | :---: | --- | --- | --- |
| **首頁 / 音訊上傳頁面** | `GET` | `/` | `upload.html` | 顯示上傳表單與使用說明 |
| **提交音訊檔案上傳** | `POST` | `/upload` | *(JSON 回應)* | 接收 multipart/form-data，含音訊檔案與 Markers JSON。回傳 202 + recording_id |
| **查詢轉寫處理狀態** | `GET` | `/transcriptions/<id>/status` | *(JSON 回應)* | 供前端輪詢使用，回傳 `{"status": "processing/completed/failed"}` |
| **查看單筆轉寫結果** | `GET` | `/transcriptions/<id>` | `result.html` | 顯示完整逐字稿、每句時間戳、即時標記對齊結果 |
| **轉寫歷史紀錄列表** | `GET` | `/transcriptions` | `history.html` | 列出所有錄音紀錄，含狀態、上傳時間、檔案名稱 |
