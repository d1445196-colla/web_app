-- ============================================
-- 個人記帳簿系統 — SQLite 資料庫建表語法
-- ============================================

-- 分類表：儲存收入與支出的分類標籤
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    type        TEXT    NOT NULL CHECK (type IN ('income', 'expense')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE(name, type)
);

-- 交易紀錄表：儲存所有收入與支出紀錄
CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT    NOT NULL CHECK (type IN ('income', 'expense')),
    amount      REAL    NOT NULL CHECK (amount > 0),
    category_id INTEGER NOT NULL,
    date        TEXT    NOT NULL,
    note        TEXT    DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 繳費提醒表：儲存每月定期帳單提醒
CREATE TABLE IF NOT EXISTS reminders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    amount      REAL    NOT NULL CHECK (amount > 0),
    due_day     INTEGER NOT NULL CHECK (due_day BETWEEN 1 AND 31),
    is_paid     TEXT    NOT NULL DEFAULT 'no' CHECK (is_paid IN ('yes', 'no')),
    paid_date   TEXT    DEFAULT NULL,
    note        TEXT    DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 常用模板表：儲存常用交易模板，用於一鍵快速記帳
CREATE TABLE IF NOT EXISTS templates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    type        TEXT    NOT NULL CHECK (type IN ('income', 'expense')),
    amount      REAL    NOT NULL CHECK (amount > 0),
    category_id INTEGER NOT NULL,
    note        TEXT    DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- ============================================
-- 預設分類資料
-- ============================================

-- 收入分類
INSERT INTO categories (name, type) VALUES ('薪資', 'income');
INSERT INTO categories (name, type) VALUES ('獎金', 'income');
INSERT INTO categories (name, type) VALUES ('兼職', 'income');
INSERT INTO categories (name, type) VALUES ('投資收益', 'income');
INSERT INTO categories (name, type) VALUES ('其他收入', 'income');

-- 支出分類
INSERT INTO categories (name, type) VALUES ('餐飲', 'expense');
INSERT INTO categories (name, type) VALUES ('交通', 'expense');
INSERT INTO categories (name, type) VALUES ('住宿', 'expense');
INSERT INTO categories (name, type) VALUES ('娛樂', 'expense');
INSERT INTO categories (name, type) VALUES ('日用品', 'expense');
INSERT INTO categories (name, type) VALUES ('醫療', 'expense');
INSERT INTO categories (name, type) VALUES ('教育', 'expense');
INSERT INTO categories (name, type) VALUES ('訂閱服務', 'expense');
INSERT INTO categories (name, type) VALUES ('其他支出', 'expense');
