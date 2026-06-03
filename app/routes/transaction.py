"""
app/routes/transaction.py
交易紀錄路由

Blueprint: transaction_bp
負責交易紀錄的新增、列表、編輯、刪除。
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

transaction_bp = Blueprint('transaction', __name__)


@transaction_bp.route('/transactions')
def list_transactions():
    """
    交易紀錄列表

    GET /transactions

    處理邏輯：呼叫 transaction.get_all_transactions() 取得所有交易
    輸出：渲染 transactions/list.html，傳入 transactions
    """
    pass


@transaction_bp.route('/transactions/new', methods=['GET', 'POST'])
def create_transaction():
    """
    新增交易

    GET  /transactions/new → 顯示新增表單
    POST /transactions/new → 接收表單，存入 DB

    GET 處理邏輯：
    1. 呼叫 category.get_all_categories() 取得分類清單
    2. 渲染 transactions/form.html，傳入 categories, transaction=None

    POST 處理邏輯：
    1. 從 request.form 取得 type, amount, category_id, date, note
    2. 驗證資料（type 為 income/expense、amount 為正數、date 有效）
    3. 呼叫 transaction.create_transaction(...)
    4. 成功 → 重導向至 /transactions
    5. 失敗 → flash 錯誤訊息，重新渲染表單
    """
    pass


@transaction_bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
def edit_transaction(id):
    """
    編輯交易

    GET  /transactions/<id>/edit → 顯示編輯表單（預填資料）
    POST /transactions/<id>/edit → 接收表單，更新 DB

    GET 處理邏輯：
    1. 呼叫 transaction.get_transaction_by_id(id)，找不到 → 404
    2. 呼叫 category.get_all_categories() 取得分類清單
    3. 渲染 transactions/form.html，傳入 categories, transaction

    POST 處理邏輯：
    1. 驗證表單資料
    2. 呼叫 transaction.update_transaction(id, ...)
    3. 重導向至 /transactions
    """
    pass


@transaction_bp.route('/transactions/<int:id>/delete', methods=['POST'])
def delete_transaction(id):
    """
    刪除交易

    POST /transactions/<id>/delete

    處理邏輯：呼叫 transaction.delete_transaction(id)
    輸出：重導向至 /transactions
    錯誤處理：找不到交易 → 404
    """
    pass
