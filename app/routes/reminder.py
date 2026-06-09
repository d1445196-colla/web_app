# app/routes/reminder.py
# 繳費提醒路由

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import reminder

reminder_bp = Blueprint('reminder', __name__)


@reminder_bp.route('/reminders')
def list_reminders():
    """
    繳費提醒列表
    """
    reminders = reminder.get_all_reminders()
    return render_template('reminders/list.html', reminders=reminders)


@reminder_bp.route('/reminders/new', methods=['GET', 'POST'])
def create_reminder():
    """
    新增繳費提醒
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        amount_str = request.form.get('amount', '0')
        due_day_str = request.form.get('due_day', '1')
        note = request.form.get('note', '').strip()

        # 驗證資料
        if not name:
            flash('[ERROR] 提醒名稱不可為空', 'danger')
            return render_template('reminders/form.html', reminder=None)

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('[ERROR] 金額必須是正數', 'danger')
            return render_template('reminders/form.html', reminder=None)

        try:
            due_day = int(due_day_str)
            if due_day < 1 or due_day > 31:
                raise ValueError()
        except ValueError:
            flash('[ERROR] 到期日必須介於 1 到 31 之間', 'danger')
            return render_template('reminders/form.html', reminder=None)

        reminder.create_reminder(name, amount, due_day, note)
        flash('[OK] 繳費提醒已建立', 'success')
        return redirect(url_for('reminder.list_reminders'))

    return render_template('reminders/form.html', reminder=None)


@reminder_bp.route('/reminders/<int:id>/edit', methods=['GET', 'POST'])
def edit_reminder(id):
    """
    編輯繳費提醒
    """
    rem = reminder.get_reminder_by_id(id)
    if rem is None:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        amount_str = request.form.get('amount', '0')
        due_day_str = request.form.get('due_day', '1')
        note = request.form.get('note', '').strip()

        # 驗證資料
        if not name:
            flash('[ERROR] 提醒名稱不可為空', 'danger')
            return render_template('reminders/form.html', reminder=rem)

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('[ERROR] 金額必須是正數', 'danger')
            return render_template('reminders/form.html', reminder=rem)

        try:
            due_day = int(due_day_str)
            if due_day < 1 or due_day > 31:
                raise ValueError()
        except ValueError:
            flash('[ERROR] 到期日必須介於 1 到 31 之間', 'danger')
            return render_template('reminders/form.html', reminder=rem)

        reminder.update_reminder(id, name, amount, due_day, note)
        flash('[OK] 繳費提醒已更新', 'success')
        return redirect(url_for('reminder.list_reminders'))

    return render_template('reminders/form.html', reminder=rem)


@reminder_bp.route('/reminders/<int:id>/delete', methods=['POST'])
def delete_reminder(id):
    """
    刪除繳費提醒
    """
    rem = reminder.get_reminder_by_id(id)
    if rem is None:
        abort(404)

    reminder.delete_reminder(id)
    flash('[OK] 繳費提醒已刪除', 'success')
    return redirect(url_for('reminder.list_reminders'))


@reminder_bp.route('/reminders/<int:id>/paid', methods=['POST'])
def mark_paid(id):
    """
    標記為已繳費
    """
    rem = reminder.get_reminder_by_id(id)
    if rem is None:
        abort(404)

    reminder.mark_as_paid(id)
    flash('[OK] 繳費已完成並記錄', 'success')
    return redirect(url_for('reminder.list_reminders'))
