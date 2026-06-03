# app/routes/template.py
# 常用模板路由

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from datetime import date

from app.models import template
from app.models import category
from app.models import transaction

template_bp = Blueprint('template', __name__)


@template_bp.route('/templates')
def list_templates():
    """
    常用模板列表
    """
    templates = template.get_all_templates()
    return render_template('templates/list.html', templates=templates)


@template_bp.route('/templates/new', methods=['GET', 'POST'])
def create_template():
    """
    新增常用模板
    """
    categories = category.get_all_categories()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        tx_type = request.form.get('type', '').strip()
        amount_str = request.form.get('amount', '0')
        category_id_str = request.form.get('category_id', '0')
        note = request.form.get('note', '').strip()

        # 驗證資料
        if not name:
            flash('[ERROR] 模板名稱不可為空', 'danger')
            return render_template('templates/form.html', categories=categories, template=None)
            
        if tx_type not in ['income', 'expense']:
            flash('[ERROR] 交易類型錯誤', 'danger')
            return render_template('templates/form.html', categories=categories, template=None)

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('[ERROR] 金額必須是正數', 'danger')
            return render_template('templates/form.html', categories=categories, template=None)

        try:
            category_id = int(category_id_str)
        except ValueError:
            flash('[ERROR] 請選擇一個分類', 'danger')
            return render_template('templates/form.html', categories=categories, template=None)

        template.create_template(name, tx_type, amount, category_id, note)
        flash('[OK] 常用模板已建立', 'success')
        return redirect(url_for('template.list_templates'))

    return render_template('templates/form.html', categories=categories, template=None)


@template_bp.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
def edit_template(id):
    """
    編輯常用模板
    """
    tmpl = template.get_template_by_id(id)
    if tmpl is None:
        abort(404)

    categories = category.get_all_categories()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        tx_type = request.form.get('type', '').strip()
        amount_str = request.form.get('amount', '0')
        category_id_str = request.form.get('category_id', '0')
        note = request.form.get('note', '').strip()

        # 驗證資料
        if not name:
            flash('[ERROR] 模板名稱不可為空', 'danger')
            return render_template('templates/form.html', categories=categories, template=tmpl)
            
        if tx_type not in ['income', 'expense']:
            flash('[ERROR] 交易類型錯誤', 'danger')
            return render_template('templates/form.html', categories=categories, template=tmpl)

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('[ERROR] 金額必須是正數', 'danger')
            return render_template('templates/form.html', categories=categories, template=tmpl)

        try:
            category_id = int(category_id_str)
        except ValueError:
            flash('[ERROR] 請選擇一個分類', 'danger')
            return render_template('templates/form.html', categories=categories, template=tmpl)

        template.update_template(id, name, tx_type, amount, category_id, note)
        flash('[OK] 常用模板已更新', 'success')
        return redirect(url_for('template.list_templates'))

    return render_template('templates/form.html', categories=categories, template=tmpl)


@template_bp.route('/templates/<int:id>/delete', methods=['POST'])
def delete_template(id):
    """
    刪除常用模板
    """
    tmpl = template.get_template_by_id(id)
    if tmpl is None:
        abort(404)

    template.delete_template(id)
    flash('[OK] 常用模板已刪除', 'success')
    return redirect(url_for('template.list_templates'))


@template_bp.route('/templates/<int:id>/apply', methods=['POST'])
def apply_template(id):
    """
    套用常用模板（一鍵記帳）
    """
    tmpl = template.get_template_by_id(id)
    if tmpl is None:
        abort(404)

    today = date.today().strftime('%Y-%m-%d')
    transaction.create_transaction(
        type=tmpl['type'],
        amount=tmpl['amount'],
        category_id=tmpl['category_id'],
        date=today,
        note=tmpl['note']
    )
    flash(f"[OK] 已套用模板「{tmpl['name']}」，一鍵記帳成功！", 'success')
    return redirect(url_for('transaction.list_transactions'))
