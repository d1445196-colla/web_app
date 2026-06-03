"""
app/routes/reminder.py
繳費提醒路由

Blueprint: reminder_bp
負責繳費提醒的新增、列表、編輯、刪除、標記已繳。
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

reminder_bp = Blueprint('reminder', __name__)


@reminder_bp.route('/reminders')
def list_reminders():
    """
    繳費提醒列表

    GET /reminders

    處理邏輯：呼叫 reminder.get_all_reminders() 取得所有提醒
    輸出：渲染 reminders/list.html，傳入 reminders
    """
    pass


@reminder_bp.route('/reminders/new', methods=['GET', 'POST'])
def create_reminder():
    """
    新增繳費提醒

    GET  /reminders/new → 顯示新增表單
    POST /reminders/new → 接收表單，存入 DB

    POST 處理邏輯：
    1. 從 request.form 取得 name, amount, due_day, note
    2. 驗證資料（amount 為正數、due_day 在 1–31 之間）
    3. 呼叫 reminder.create_reminder(name, amount, due_day, note)
    4. 成功 → 重導向至 /reminders
    5. 失敗 → flash 錯誤訊息，重新渲染表單
    """
    pass


@reminder_bp.route('/reminders/<int:id>/edit', methods=['GET', 'POST'])
def edit_reminder(id):
    """
    編輯繳費提醒

    GET  /reminders/<id>/edit → 顯示編輯表單（預填資料）
    POST /reminders/<id>/edit → 接收表單，更新 DB

    GET 處理邏輯：
    1. 呼叫 reminder.get_reminder_by_id(id)，找不到 → 404
    2. 渲染 reminders/form.html，傳入 reminder

    POST 處理邏輯：
    1. 驗證表單資料
    2. 呼叫 reminder.update_reminder(id, name, amount, due_day, note)
    3. 重導向至 /reminders
    """
    pass


@reminder_bp.route('/reminders/<int:id>/delete', methods=['POST'])
def delete_reminder(id):
    """
    刪除繳費提醒

    POST /reminders/<id>/delete

    處理邏輯：呼叫 reminder.delete_reminder(id)
    輸出：重導向至 /reminders
    """
    pass


@reminder_bp.route('/reminders/<int:id>/paid', methods=['POST'])
def mark_paid(id):
    """
    標記為已繳費

    POST /reminders/<id>/paid

    處理邏輯：呼叫 reminder.mark_as_paid(id)
    輸出：重導向至 /reminders
    """
    pass
