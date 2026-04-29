# 個人記帳簿系統 — 路由設計文件

> **版本**：v1.0  
> **建立日期**：2026-04-29  
> **前置文件**：[PRD.md](./PRD.md) ｜ [ARCHITECTURE.md](./ARCHITECTURE.md) ｜ [DB_DESIGN.md](./DB_DESIGN.md)  

---

## 1. 路由總覽表格

### 首頁（main）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|----------|----------|------|
| 首頁儀表板 | GET | `/` | `templates/index.html` | 顯示餘額統計、即將到期帳單、近期交易 |

### 交易紀錄（transaction）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|----------|----------|------|
| 交易列表 | GET | `/transactions` | `templates/transactions/list.html` | 顯示所有交易紀錄 |
| 新增交易頁面 | GET | `/transactions/new` | `templates/transactions/form.html` | 顯示新增交易表單 |
| 建立交易 | POST | `/transactions/new` | — | 接收表單，存入 DB，重導向至交易列表 |
| 編輯交易頁面 | GET | `/transactions/<id>/edit` | `templates/transactions/form.html` | 顯示編輯交易表單（預填資料） |
| 更新交易 | POST | `/transactions/<id>/edit` | — | 接收表單，更新 DB，重導向至交易列表 |
| 刪除交易 | POST | `/transactions/<id>/delete` | — | 刪除後重導向至交易列表 |

### 繳費提醒（reminder）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|----------|----------|------|
| 提醒列表 | GET | `/reminders` | `templates/reminders/list.html` | 顯示所有繳費提醒 |
| 新增提醒頁面 | GET | `/reminders/new` | `templates/reminders/form.html` | 顯示新增提醒表單 |
| 建立提醒 | POST | `/reminders/new` | — | 接收表單，存入 DB，重導向至提醒列表 |
| 編輯提醒頁面 | GET | `/reminders/<id>/edit` | `templates/reminders/form.html` | 顯示編輯提醒表單（預填資料） |
| 更新提醒 | POST | `/reminders/<id>/edit` | — | 接收表單，更新 DB，重導向至提醒列表 |
| 刪除提醒 | POST | `/reminders/<id>/delete` | — | 刪除後重導向至提醒列表 |
| 標記已繳 | POST | `/reminders/<id>/paid` | — | 標記為已繳，重導向至提醒列表 |

### 常用模板（template）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|----------|----------|------|
| 模板列表 | GET | `/templates` | `templates/templates/list.html` | 顯示所有常用模板 |
| 新增模板頁面 | GET | `/templates/new` | `templates/templates/form.html` | 顯示新增模板表單 |
| 建立模板 | POST | `/templates/new` | — | 接收表單，存入 DB，重導向至模板列表 |
| 編輯模板頁面 | GET | `/templates/<id>/edit` | `templates/templates/form.html` | 顯示編輯模板表單（預填資料） |
| 更新模板 | POST | `/templates/<id>/edit` | — | 接收表單，更新 DB，重導向至模板列表 |
| 刪除模板 | POST | `/templates/<id>/delete` | — | 刪除後重導向至模板列表 |
| 套用模板 | POST | `/templates/<id>/apply` | — | 以模板資料建立交易，重導向至首頁 |

### 統計報表（stats）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|----------|----------|------|
| 統計頁面 | GET | `/stats` | `templates/stats/index.html` | 顯示收支趨勢圖表 |

---

## 2. 每個路由的詳細說明

### 2.1 首頁儀表板

#### `GET /`

- **輸入**：無
- **處理邏輯**：
  1. 呼叫 `transaction.get_balance()` 取得總餘額
  2. 呼叫 `transaction.get_monthly_summary(year, month)` 取得本月收支
  3. 呼叫 `transaction.get_recent_transactions(5)` 取得近期 5 筆交易
  4. 呼叫 `reminder.get_upcoming_reminders(7)` 取得 7 天內到期帳單
- **輸出**：渲染 `index.html`，傳入 `balance`、`monthly`、`recent_transactions`、`upcoming_reminders`
- **錯誤處理**：資料庫連線失敗時顯示錯誤頁面

---

### 2.2 交易紀錄

#### `GET /transactions`

- **輸入**：無
- **處理邏輯**：呼叫 `transaction.get_all_transactions()` 取得所有交易
- **輸出**：渲染 `transactions/list.html`，傳入 `transactions`
- **錯誤處理**：無特殊處理

#### `GET /transactions/new`

- **輸入**：無
- **處理邏輯**：呼叫 `category.get_all_categories()` 取得分類清單
- **輸出**：渲染 `transactions/form.html`，傳入 `categories`、`transaction=None`
- **錯誤處理**：無特殊處理

#### `POST /transactions/new`

- **輸入**：表單欄位 `type`、`amount`、`category_id`、`date`、`note`
- **處理邏輯**：
  1. 驗證表單資料（type 必須是 income/expense、amount 必須為正數、date 必須有效）
  2. 呼叫 `transaction.create_transaction(type, amount, category_id, date, note)`
- **輸出**：成功 → 重導向至 `/transactions`；失敗 → 重新渲染表單並顯示錯誤
- **錯誤處理**：驗證失敗時用 `flash()` 顯示錯誤訊息

#### `GET /transactions/<id>/edit`

- **輸入**：URL 參數 `id`
- **處理邏輯**：
  1. 呼叫 `transaction.get_transaction_by_id(id)` 取得該筆交易
  2. 呼叫 `category.get_all_categories()` 取得分類清單
- **輸出**：渲染 `transactions/form.html`，傳入 `categories`、`transaction`
- **錯誤處理**：找不到交易 → 404

#### `POST /transactions/<id>/edit`

- **輸入**：URL 參數 `id`、表單欄位同新增
- **處理邏輯**：
  1. 驗證表單資料
  2. 呼叫 `transaction.update_transaction(id, type, amount, category_id, date, note)`
- **輸出**：成功 → 重導向至 `/transactions`；失敗 → 重新渲染表單
- **錯誤處理**：驗證失敗時用 `flash()` 顯示錯誤訊息

#### `POST /transactions/<id>/delete`

- **輸入**：URL 參數 `id`
- **處理邏輯**：呼叫 `transaction.delete_transaction(id)`
- **輸出**：重導向至 `/transactions`
- **錯誤處理**：找不到交易 → 404

---

### 2.3 繳費提醒

#### `GET /reminders`

- **輸入**：無
- **處理邏輯**：呼叫 `reminder.get_all_reminders()` 取得所有提醒
- **輸出**：渲染 `reminders/list.html`，傳入 `reminders`

#### `GET /reminders/new`

- **輸入**：無
- **處理邏輯**：無
- **輸出**：渲染 `reminders/form.html`，傳入 `reminder=None`

#### `POST /reminders/new`

- **輸入**：表單欄位 `name`、`amount`、`due_day`、`note`
- **處理邏輯**：
  1. 驗證資料（amount 正數、due_day 在 1–31 之間）
  2. 呼叫 `reminder.create_reminder(name, amount, due_day, note)`
- **輸出**：成功 → 重導向至 `/reminders`
- **錯誤處理**：驗證失敗時顯示錯誤訊息

#### `GET /reminders/<id>/edit`

- **輸入**：URL 參數 `id`
- **處理邏輯**：呼叫 `reminder.get_reminder_by_id(id)`
- **輸出**：渲染 `reminders/form.html`，傳入 `reminder`
- **錯誤處理**：找不到 → 404

#### `POST /reminders/<id>/edit`

- **輸入**：URL 參數 `id`、表單欄位同新增
- **處理邏輯**：驗證後呼叫 `reminder.update_reminder(id, name, amount, due_day, note)`
- **輸出**：成功 → 重導向至 `/reminders`

#### `POST /reminders/<id>/delete`

- **輸入**：URL 參數 `id`
- **處理邏輯**：呼叫 `reminder.delete_reminder(id)`
- **輸出**：重導向至 `/reminders`

#### `POST /reminders/<id>/paid`

- **輸入**：URL 參數 `id`
- **處理邏輯**：呼叫 `reminder.mark_as_paid(id)`
- **輸出**：重導向至 `/reminders`

---

### 2.4 常用模板

#### `GET /templates`

- **輸入**：無
- **處理邏輯**：呼叫 `template.get_all_templates()`
- **輸出**：渲染 `templates/list.html`，傳入 `templates`

#### `GET /templates/new`

- **輸入**：無
- **處理邏輯**：呼叫 `category.get_all_categories()` 取得分類清單
- **輸出**：渲染 `templates/form.html`，傳入 `categories`、`template=None`

#### `POST /templates/new`

- **輸入**：表單欄位 `name`、`type`、`amount`、`category_id`、`note`
- **處理邏輯**：驗證後呼叫 `template.create_template(name, type, amount, category_id, note)`
- **輸出**：成功 → 重導向至 `/templates`

#### `GET /templates/<id>/edit`

- **輸入**：URL 參數 `id`
- **處理邏輯**：取得模板資料與分類清單
- **輸出**：渲染 `templates/form.html`，傳入 `categories`、`template`
- **錯誤處理**：找不到 → 404

#### `POST /templates/<id>/edit`

- **輸入**：URL 參數 `id`、表單欄位同新增
- **處理邏輯**：驗證後呼叫 `template.update_template(...)`
- **輸出**：成功 → 重導向至 `/templates`

#### `POST /templates/<id>/delete`

- **輸入**：URL 參數 `id`
- **處理邏輯**：呼叫 `template.delete_template(id)`
- **輸出**：重導向至 `/templates`

#### `POST /templates/<id>/apply`

- **輸入**：URL 參數 `id`
- **處理邏輯**：
  1. 呼叫 `template.get_template_by_id(id)` 取得模板資料
  2. 呼叫 `transaction.create_transaction(...)` 以模板資料 + 今天日期建立交易
- **輸出**：重導向至 `/`（首頁）
- **錯誤處理**：找不到模板 → 404

---

### 2.5 統計報表

#### `GET /stats`

- **輸入**：無
- **處理邏輯**：
  1. 取得最近 6 個月的月份列表
  2. 對每個月呼叫 `transaction.get_monthly_summary(year, month)`
  3. 組合成圖表資料
- **輸出**：渲染 `stats/index.html`，傳入 `monthly_data`
- **錯誤處理**：無特殊處理

---

## 3. Jinja2 模板清單

所有模板皆繼承 `base.html`，使用 `{% extends "base.html" %}` 與 `{% block content %}`。

| 模板檔案 | 繼承 | 說明 |
|----------|------|------|
| `base.html` | — | 共用版面：導覽列、頁尾、CSS/JS 引入、flash 訊息 |
| `index.html` | `base.html` | 首頁儀表板：餘額卡片、本月收支、到期提醒、近期交易 |
| `transactions/list.html` | `base.html` | 交易紀錄列表，含編輯/刪除按鈕 |
| `transactions/form.html` | `base.html` | 新增/編輯交易表單（共用，依是否有 transaction 資料判斷模式） |
| `reminders/list.html` | `base.html` | 繳費提醒列表，含標記已繳/編輯/刪除按鈕 |
| `reminders/form.html` | `base.html` | 新增/編輯提醒表單 |
| `templates/list.html` | `base.html` | 常用模板列表，含套用/編輯/刪除按鈕 |
| `templates/form.html` | `base.html` | 新增/編輯模板表單 |
| `stats/index.html` | `base.html` | 統計報表頁面，含 Chart.js 圖表 |

---

## 4. 路由骨架程式碼

路由骨架已建立在 `app/routes/` 目錄中，每個檔案只包含函式定義與 docstring，不含實作邏輯。

| 檔案 | Blueprint 名稱 | 負責功能 |
|------|----------------|----------|
| `app/routes/__init__.py` | — | 套件初始化 |
| `app/routes/main.py` | `main_bp` | 首頁儀表板 |
| `app/routes/transaction.py` | `transaction_bp` | 交易紀錄 CRUD |
| `app/routes/reminder.py` | `reminder_bp` | 繳費提醒 CRUD |
| `app/routes/template.py` | `template_bp` | 常用模板 CRUD + 套用 |
| `app/routes/stats.py` | `stats_bp` | 統計報表 |

---

> **下一步**：待團隊確認路由設計後，進入 Implementation（程式碼實作）階段。
