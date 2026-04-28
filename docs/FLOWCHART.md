# 個人記帳簿系統 — 流程圖文件

> **版本**：v1.0  
> **建立日期**：2026-04-29  
> **前置文件**：[PRD.md](./PRD.md) ｜ [ARCHITECTURE.md](./ARCHITECTURE.md)  

---

## 1. 使用者流程圖（User Flow）

### 1.1 主流程總覽

從使用者進入網站開始，涵蓋所有主要功能的操作路徑。

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B["首頁 - 儀表板"]

    B --> C{要執行什麼操作？}

    C -->|記帳| D["新增交易頁面"]
    C -->|查看紀錄| E["交易紀錄列表"]
    C -->|繳費提醒| F["繳費提醒列表"]
    C -->|常用模板| G["常用模板列表"]
    C -->|統計報表| H["統計報表頁面"]

    D --> D1["選擇類型：收入/支出"]
    D1 --> D2["填寫金額、分類、日期、備註"]
    D2 --> D3["送出表單"]
    D3 --> B

    E --> E1{要做什麼？}
    E1 -->|查看| E2["瀏覽交易明細"]
    E1 -->|編輯| E3["編輯交易表單"]
    E1 -->|刪除| E4["確認刪除"]
    E2 --> E
    E3 --> E5["儲存修改"]
    E5 --> E
    E4 --> E

    F --> F1{要做什麼？}
    F1 -->|新增提醒| F2["填寫帳單名稱、金額、到期日"]
    F1 -->|標記已繳| F3["標記為已繳費"]
    F1 -->|編輯| F4["編輯提醒"]
    F1 -->|刪除| F5["刪除提醒"]
    F2 --> F
    F3 --> F
    F4 --> F
    F5 --> F

    G --> G1{要做什麼？}
    G1 -->|新增模板| G2["填寫模板名稱、類型、金額、分類"]
    G1 -->|套用模板| G3["一鍵建立交易紀錄"]
    G1 -->|編輯| G4["編輯模板"]
    G1 -->|刪除| G5["刪除模板"]
    G2 --> G
    G3 --> B
    G4 --> G
    G5 --> G

    H --> H1["查看收支趨勢圖表"]
    H1 --> B
```

### 1.2 新增交易流程（詳細版）

```mermaid
flowchart LR
    START([使用者點擊「新增交易」]) --> TYPE{"選擇交易類型"}

    TYPE -->|收入| INC["顯示收入分類選單"]
    TYPE -->|支出| EXP["顯示支出分類選單"]

    INC --> FORM["填寫表單"]
    EXP --> FORM

    FORM --> FILL["輸入金額、選擇分類、<br>選擇日期、填寫備註"]
    FILL --> SUBMIT["點擊送出"]

    SUBMIT --> VALID{表單驗證}
    VALID -->|通過| SAVE["儲存至資料庫"]
    VALID -->|失敗| ERR["顯示錯誤訊息"]
    ERR --> FILL

    SAVE --> SUCCESS["顯示成功訊息"]
    SUCCESS --> REDIRECT["重導向至首頁"]
```

### 1.3 使用常用模板記帳流程

```mermaid
flowchart LR
    START([使用者進入常用模板頁]) --> LIST["顯示模板清單"]
    LIST --> SELECT["選擇一個模板"]
    SELECT --> APPLY["點擊「套用」按鈕"]
    APPLY --> CONFIRM["確認金額與日期"]
    CONFIRM --> SAVE["自動建立交易紀錄"]
    SAVE --> DONE["重導向至首頁<br>顯示成功訊息"]
```

### 1.4 繳費提醒流程

```mermaid
flowchart LR
    START([使用者進入首頁]) --> CHECK["系統檢查即將到期帳單"]
    CHECK --> SHOW{"有到期帳單？"}
    SHOW -->|有| ALERT["首頁顯示提醒卡片"]
    SHOW -->|沒有| NORMAL["正常顯示儀表板"]
    ALERT --> ACTION{使用者操作}
    ACTION -->|去繳費| PAY["標記為已繳"]
    ACTION -->|稍後再說| DISMISS["略過"]
    PAY --> DONE["更新狀態，提醒消失"]
```

---

## 2. 系統序列圖（Sequence Diagram）

### 2.1 新增交易紀錄

描述「使用者填寫表單」到「資料存入資料庫」的完整流程。

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br>(transaction.py)
    participant Model as Model<br>(transaction.py)
    participant DB as SQLite

    User->>Browser: 點擊「新增交易」
    Browser->>Route: GET /transaction/new
    Route->>Model: get_all_categories()
    Model->>DB: SELECT * FROM categories
    DB-->>Model: 分類清單
    Model-->>Route: 分類資料
    Route-->>Browser: 渲染 form.html（含分類選單）

    User->>Browser: 填寫表單並送出
    Browser->>Route: POST /transaction/new
    Route->>Route: 驗證表單資料
    Route->>Model: create_transaction(data)
    Model->>DB: INSERT INTO transactions
    DB-->>Model: 成功
    Model-->>Route: 新交易 ID
    Route-->>Browser: 重導向至首頁 (302)
    Browser->>Route: GET /
    Route-->>Browser: 渲染首頁（含更新餘額）
```

### 2.2 查看首頁儀表板

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br>(main.py)
    participant TxnModel as Model<br>(transaction.py)
    participant RemModel as Model<br>(reminder.py)
    participant DB as SQLite

    User->>Browser: 開啟首頁
    Browser->>Route: GET /

    Route->>TxnModel: get_balance()
    TxnModel->>DB: SELECT SUM 收入 - SUM 支出
    DB-->>TxnModel: 餘額數值
    TxnModel-->>Route: 總餘額

    Route->>TxnModel: get_monthly_summary()
    TxnModel->>DB: SELECT SUM GROUP BY type WHERE 本月
    DB-->>TxnModel: 本月收支
    TxnModel-->>Route: 本月收入/支出

    Route->>TxnModel: get_recent_transactions(5)
    TxnModel->>DB: SELECT TOP 5 ORDER BY date DESC
    DB-->>TxnModel: 近期交易
    TxnModel-->>Route: 交易列表

    Route->>RemModel: get_upcoming_reminders()
    RemModel->>DB: SELECT WHERE due_date 近7天
    DB-->>RemModel: 即將到期帳單
    RemModel-->>Route: 提醒列表

    Route-->>Browser: 渲染 index.html（餘額 + 提醒 + 近期交易）
```

### 2.3 編輯交易紀錄

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br>(transaction.py)
    participant Model as Model<br>(transaction.py)
    participant DB as SQLite

    User->>Browser: 在交易列表點擊「編輯」
    Browser->>Route: GET /transaction/3/edit
    Route->>Model: get_transaction(3)
    Model->>DB: SELECT * FROM transactions WHERE id=3
    DB-->>Model: 交易資料
    Model-->>Route: 交易物件
    Route-->>Browser: 渲染 form.html（預填資料）

    User->>Browser: 修改內容並送出
    Browser->>Route: POST /transaction/3/edit
    Route->>Route: 驗證表單資料
    Route->>Model: update_transaction(3, data)
    Model->>DB: UPDATE transactions SET ... WHERE id=3
    DB-->>Model: 成功
    Model-->>Route: 更新完成
    Route-->>Browser: 重導向至交易列表 (302)
```

### 2.4 刪除交易紀錄

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br>(transaction.py)
    participant Model as Model<br>(transaction.py)
    participant DB as SQLite

    User->>Browser: 點擊「刪除」按鈕
    Browser->>Browser: 彈出確認對話框
    User->>Browser: 確認刪除
    Browser->>Route: POST /transaction/3/delete
    Route->>Model: delete_transaction(3)
    Model->>DB: DELETE FROM transactions WHERE id=3
    DB-->>Model: 成功
    Model-->>Route: 刪除完成
    Route-->>Browser: 重導向至交易列表 (302)
```

### 2.5 套用常用模板

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br>(template.py)
    participant TplModel as Model<br>(template.py)
    participant TxnModel as Model<br>(transaction.py)
    participant DB as SQLite

    User->>Browser: 點擊模板的「套用」按鈕
    Browser->>Route: POST /templates/2/apply
    Route->>TplModel: get_template(2)
    TplModel->>DB: SELECT * FROM templates WHERE id=2
    DB-->>TplModel: 模板資料
    TplModel-->>Route: 模板物件

    Route->>TxnModel: create_transaction(模板資料 + 今天日期)
    TxnModel->>DB: INSERT INTO transactions
    DB-->>TxnModel: 成功
    TxnModel-->>Route: 新交易 ID

    Route-->>Browser: 重導向至首頁 (302)
```

---

## 3. 功能清單對照表

| 功能 | 頁面 | URL 路徑 | HTTP 方法 | 說明 |
|------|------|----------|-----------|------|
| 首頁儀表板 | 儀表板 | `/` | GET | 顯示餘額、本月收支、即將到期帳單、近期交易 |
| 新增交易 | 交易表單 | `/transaction/new` | GET / POST | GET 顯示表單，POST 儲存新交易 |
| 交易列表 | 交易列表 | `/transactions` | GET | 瀏覽所有交易紀錄，支援分類篩選 |
| 編輯交易 | 交易表單 | `/transaction/<id>/edit` | GET / POST | GET 顯示預填表單，POST 更新交易 |
| 刪除交易 | — | `/transaction/<id>/delete` | POST | 刪除指定交易紀錄 |
| 繳費提醒列表 | 提醒列表 | `/reminders` | GET | 顯示所有繳費提醒 |
| 新增提醒 | 提醒表單 | `/reminder/new` | GET / POST | GET 顯示表單，POST 儲存新提醒 |
| 編輯提醒 | 提醒表單 | `/reminder/<id>/edit` | GET / POST | GET 顯示預填表單，POST 更新提醒 |
| 刪除提醒 | — | `/reminder/<id>/delete` | POST | 刪除指定提醒 |
| 標記已繳 | — | `/reminder/<id>/paid` | POST | 標記提醒為已繳費 |
| 常用模板列表 | 模板列表 | `/templates` | GET | 顯示所有常用模板 |
| 新增模板 | 模板表單 | `/template/new` | GET / POST | GET 顯示表單，POST 儲存新模板 |
| 編輯模板 | 模板表單 | `/template/<id>/edit` | GET / POST | GET 顯示預填表單，POST 更新模板 |
| 刪除模板 | — | `/template/<id>/delete` | POST | 刪除指定模板 |
| 套用模板 | — | `/template/<id>/apply` | POST | 以模板資料建立新交易紀錄 |
| 統計報表 | 統計頁面 | `/stats` | GET | 顯示收支趨勢圖表 |

---

> **下一步**：待團隊確認流程圖後，進入 DB Design（資料庫設計）階段。
