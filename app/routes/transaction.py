# app/routes/transaction.py
# 交易紀錄路由

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import transaction
from app.models import category

transaction_bp = Blueprint('transaction', __name__)


@transaction_bp.route('/transactions')
def list_transactions():
    """
    交易紀錄列表
    """
    txs = transaction.get_all_transactions()
    balance = transaction.get_balance()
    return render_template('transactions/list.html', transactions=txs, balance=balance)


@transaction_bp.route('/transactions/new', methods=['GET', 'POST'])
def create_transaction():
    """
    新增交易
    """
    categories = category.get_all_categories()
    
    if request.method == 'POST':
        tx_type = request.form.get('type', '').strip()
        amount_str = request.form.get('amount', '0')
        category_id_str = request.form.get('category_id', '0')
        date_str = request.form.get('date', '').strip()
        note = request.form.get('note', '').strip()

        # 驗證資料
        if tx_type not in ['income', 'expense']:
            flash('[ERROR] 交易類型錯誤', 'danger')
            return render_template('transactions/form.html', categories=categories, transaction=None)

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('[ERROR] 金額必須是正數', 'danger')
            return render_template('transactions/form.html', categories=categories, transaction=None)

        try:
            category_id = int(category_id_str)
        except ValueError:
            flash('[ERROR] 請選擇一個分類', 'danger')
            return render_template('transactions/form.html', categories=categories, transaction=None)

        if not date_str:
            flash('[ERROR] 請選擇交易日期', 'danger')
            return render_template('transactions/form.html', categories=categories, transaction=None)

        transaction.create_transaction(tx_type, amount, category_id, date_str, note)
        flash('[OK] 交易紀錄已儲存', 'success')
        return redirect(url_for('transaction.list_transactions'))

    return render_template('transactions/form.html', categories=categories, transaction=None)


@transaction_bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
def edit_transaction(id):
    """
    編輯交易
    """
    tx = transaction.get_transaction_by_id(id)
    if tx is None:
        abort(404)

    categories = category.get_all_categories()

    if request.method == 'POST':
        tx_type = request.form.get('type', '').strip()
        amount_str = request.form.get('amount', '0')
        category_id_str = request.form.get('category_id', '0')
        date_str = request.form.get('date', '').strip()
        note = request.form.get('note', '').strip()

        # 驗證資料
        if tx_type not in ['income', 'expense']:
            flash('[ERROR] 交易類型錯誤', 'danger')
            return render_template('transactions/form.html', categories=categories, transaction=tx)

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('[ERROR] 金額必須是正數', 'danger')
            return render_template('transactions/form.html', categories=categories, transaction=tx)

        try:
            category_id = int(category_id_str)
        except ValueError:
            flash('[ERROR] 請選擇一個分類', 'danger')
            return render_template('transactions/form.html', categories=categories, transaction=tx)

        if not date_str:
            flash('[ERROR] 請選擇交易日期', 'danger')
            return render_template('transactions/form.html', categories=categories, transaction=tx)

        transaction.update_transaction(id, tx_type, amount, category_id, date_str, note)
        flash('[OK] 交易紀錄已更新', 'success')
        return redirect(url_for('transaction.list_transactions'))

    return render_template('transactions/form.html', categories=categories, transaction=tx)


@transaction_bp.route('/transactions/<int:id>/delete', methods=['POST'])
def delete_transaction(id):
    """
    刪除交易
    """
    tx = transaction.get_transaction_by_id(id)
    if tx is None:
        abort(404)

    transaction.delete_transaction(id)
    flash('[OK] 交易紀錄已刪除', 'success')
    return redirect(url_for('transaction.list_transactions'))
