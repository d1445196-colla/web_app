"""
app/routes/template.py
常用模板路由

Blueprint: template_bp
負責常用模板的新增、列表、編輯、刪除、套用。
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

template_bp = Blueprint('template', __name__)


@template_bp.route('/templates')
def list_templates():
    """
    常用模板列表

    GET /templates

    處理邏輯：呼叫 template.get_all_templates() 取得所有模板
    輸出：渲染 templates/list.html，傳入 templates
    """
    pass


@template_bp.route('/templates/new', methods=['GET', 'POST'])
def create_template():
    """
    新增常用模板

    GET  /templates/new → 顯示新增表單
    POST /templates/new → 接收表單，存入 DB

    POST 處理邏輯：
    1. 從 request.form 取得 name, type, amount, category_id, note
    2. 驗證資料
    3. 呼叫 template.create_template(name, type, amount, category_id, note)
    4. 成功 → 重導向至 /templates
    """
    pass


@template_bp.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
def edit_template(id):
    """
    編輯常用模板

    GET  /templates/<id>/edit → 顯示編輯表單（預填資料）
    POST /templates/<id>/edit → 接收表單，更新 DB

    GET 處理邏輯：
    1. 呼叫 template.get_template_by_id(id)，找不到 → 404
    2. 呼叫 category.get_all_categories() 取得分類清單
    3. 渲染 templates/form.html，傳入 categories, template

    POST 處理邏輯：
    1. 驗證表單資料
    2. 呼叫 template.update_template(id, ...)
    3. 重導向至 /templates
    """
    pass


@template_bp.route('/templates/<int:id>/delete', methods=['POST'])
def delete_template(id):
    """
    刪除常用模板

    POST /templates/<id>/delete

    處理邏輯：呼叫 template.delete_template(id)
    輸出：重導向至 /templates
    """
    pass


@template_bp.route('/templates/<int:id>/apply', methods=['POST'])
def apply_template(id):
    """
    套用常用模板（一鍵記帳）

    POST /templates/<id>/apply

    處理邏輯：
    1. 呼叫 template.get_template_by_id(id) 取得模板資料，找不到 → 404
    2. 呼叫 transaction.create_transaction(
           type=模板.type, amount=模板.amount,
           category_id=模板.category_id, date=今天, note=模板.note
       )
    3. flash 成功訊息
    輸出：重導向至 /（首頁）
    """
    pass
