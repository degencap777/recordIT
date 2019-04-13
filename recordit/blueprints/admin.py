# -*- coding: utf-8 -*-

import os
from uuid import uuid4

from flask import (Blueprint, current_app, flash, render_template, request,
                   send_file)
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from recordit.decorators import permission_required
from recordit.extensions import db
from recordit.forms.admin import (AddCourseForm, AddReportForm,
                                  ChangePasswordForm, DeleteRecordForm,
                                  DeleteReportForm, DeleteUserForm,
                                  EditAdministratorForm, EditStudenteForm,
                                  EditTeacherForm, RegisterAdministratorForm,
                                  RegisterStudentForm, RegisterTeacherForm)
from recordit.models import Course, Log, RecordTable, Report, Role, User
from recordit.utils import log_user, packitup, redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
@fresh_login_required
@login_required
def login_protect():
    pass


@admin_bp.route('/')
def index():
    log = log_user(content=render_template('logs/admin/index.html'))

    user_count = User.query.count()
    role_administrator = Role.query.filter_by(name='Administrator').first()
    admin_count = User.query.filter_by(role_id=role_administrator.id).count()
    role_teacher = Role.query.filter_by(name='Teacher').first()
    teacher_count = User.query.filter_by(role_id=role_teacher.id).count()
    role_student = Role.query.filter_by(name='Student').first()
    student_count = User.query.filter_by(role_id=role_student.id).count()

    course_count = Course.query.count()
    log_count = Log.query.count()

    return render_template(
        'admin/index.html', user_count=user_count, admin_count=admin_count,
        teacher_count=teacher_count, student_count=student_count, course_count=course_count, log_count=log_count)


@admin_bp.route('/manage/user')
@permission_required('ADMINISTER')
def manage_user():
    log = log_user(content=render_template('logs/admin/manage_user.html'))

    # 'all', 'student', 'teacher', 'administrator'
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MANAGE_USER_PER_PAGE']
    role_administrator = Role.query.filter_by(name='Administrator').first()
    role_teacher = Role.query.filter_by(name='Teacher').first()
    role_student = Role.query.filter_by(name='Student').first()

    if filter_rule == 'student':
        filtered_users = User.query.filter_by(role=role_student)
    elif filter_rule == 'teacher':
        filtered_users = User.query.filter_by(role=role_teacher)
    elif filter_rule == 'administrator':
        filtered_users = User.query.filter_by(role=role_administrator)
    else:
        filtered_users = User.query

    pagination = filtered_users.order_by(
        User.number.desc()).paginate(page, per_page)

    form = DeleteUserForm()

    return render_template('admin/manage_user.html', pagination=pagination, form=form)


@admin_bp.route('manage/user/<int:user_id>/delete', methods=['POST'])
@permission_required('ADMINISTER')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    content = render_template(
        'logs/admin/delete_user.html', username=user.username, name=user.name)
    log = log_user(content)

    db.session.delete(user)
    db.session.commit()

    flash(_('User deleted.'), 'info')
    return redirect_back()


@admin_bp.route('manage/user/<int:user_id>/edit-profile', methods=['GET', 'POST'])
@permission_required('ADMINISTER')
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        form = EditAdministratorForm()
    elif user.is_teacher:
        form = EditTeacherForm()
    else:
        form = EditStudenteForm()

    if form.validate_on_submit():
        content = render_template(
            'logs/admin/edit_profile.html',
            username_old=user.username, name_old=user.name,
            username_new=form.name.data, user_new=form.username.data)
        log = log_user(content)

        user.number = form.username.data
        user.name = form.name.data
        user.remark = form.remark.data
        db.session.commit()

        flash(_('Profile updated.'), 'success')
        redirect_back()

    form.username.data = user.number
    form.name.data = user.name
    form.remark.data = user.remark

    return render_template('admin/edit_profile.html', form=form)


@admin_bp.route('manage/user/<int:user_id>/change-password', methods=['GET', 'POST'])
@permission_required('ADMINISTER')
def change_password(user_id):
    user = User.query.get_or_404(user_id)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if user.validate_password(form.old_password.data):
            content = render_template(
                'logs/admin/change_password.html',
                username=user.username, name=user.name)
            log = log_user(content)

            user.set_password(form.password.data)
            db.session.commit()

            flash(_('Password updated.'), 'success')
            redirect_back()
        else:
            flash(_('Old password is incorrect.'), 'warning')

    return render_template('admin/change_password.html', form=form)


@admin_bp.route('manage/user/register/student', methods=['GET', 'POST'])
@permission_required('ADMINISTER')
def register_student():
    form = RegisterStudentForm()
    if form.validate_on_submit():
        content = render_template(
            'logs/admin/register_user.html',
            username=form.username.data, name=form.name.data)
        log = log_user(content)

        user = User(
            number=form.username.data,
            name=form.name.data,
            remark=form.remark.data
        )
        user.set_password(form.password.data)
        user.set_role('Student')
        db.session.add(user)

        flash(_('Register success.'), 'success')
        return redirect_back()

    return render_template('admin/register_user.html', form=form)


@admin_bp.route('manage/user/register/teacher', methods=['GET', 'POST'])
@permission_required('ADMINISTER')
def register_teacher():
    form = RegisterTeacherForm()
    if form.validate_on_submit():
        content = render_template(
            'logs/admin/register_user.html',
            username=form.username.data, name=form.name.data)
        log = log_user(content)

        user = User(
            number=form.username.data,
            name=form.name.data,
            remark=form.remark.data
        )
        user.set_password(form.password.data)
        user.set_role('Teacher')
        db.session.add(user)

        flash(_('Register success.'), 'success')
        return redirect_back()

    return render_template('admin/register_user.html', form=form)


@admin_bp.route('manage/user/register/administrator', methods=['GET', 'POST'])
@permission_required('ADMINISTER')
def register_administrator():
    form = RegisterAdministratorForm()
    if form.validate_on_submit():
        content = render_template(
            'logs/admin/register_user.html',
            username=form.username.data, name=form.name.data)
        log = log_user(content)

        user = User(
            number=form.username.data,
            name=form.name.data,
            remark=form.remark.data
        )
        user.set_password(form.password.data)
        user.set_role('Administrator')
        db.session.add(user)

        flash(_('Register success.'), 'success')
        return redirect_back()

    return render_template('admin/register_user.html', form=form)


@admin_bp.route('manage/course')
@permission_required('MODERATOR_COURSE')
def manage_course():
    log = log_user(content=render_template('logs/admin/manage_course.html'))

    per_page = current_app.config['MANAGE_COURSE_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.order_by(
        Course.date.desc()).paginate(page, per_page)

    return render_template('admin/manage_course.html', pagination=pagination)


@admin_bp.route('manage/course/add', methods=['GET', 'POST'])
@permission_required('MODERATOR_COURSE')
def add_course():
    form = AddCourseForm()
    if form.validate_on_submit():
        content = render_template(
            'logs/admin/add_course.html', grade=form.grade.data, name=form.name.data)
        log = log_user(content)

        course = Course(
            teacher_id=form.teacher.data,
            name=form.name.data,
            grade=form.grade.data,
            remark=form.remark.data
        )
        db.session.add(course)
        db.session.commit()

        flash(_('Add course success.'), 'success')
        return redirect_back()

    return render_template('admin/add_course.html', form=form)


@admin_bp.route('manage/report/<int:course_id>')
@permission_required('MODERATOR_REPORT')
def manage_report(course_id):
    log = log_user(content=render_template('logs/admin/manage_report.html'))

    per_page = current_app.config['MANAGE_REPORT_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = Report.query.filter_by(course_id=course_id).order_by(
        Report.date.desc()).paginate(page, per_page)

    form = DeleteReportForm()

    return render_template('admin/manage_report.html', pagination=pagination, form=form)


@admin_bp.route('manage/report/<int:course_id>/add', methods=['GET', 'POST'])
@permission_required('MODERATOR_REPORT')
def add_report(course_id):
    form = AddReportForm()
    if form.validate_on_submit():
        course = Course.query.get_or_404(course_id)
        user = User.query.get_or_404(form.reporter.data)
        if course.grade == user.grade:
            content = render_template(
                'logs/admin/add_report.html', course=course.name, grade=course.grade,
                username=user.number, name=user.name, report=form.name.data)
            log = log_user(content)

            report = Report(
                course_id=course_id,
                name=form.name.data,
                remark=form.remark.data
            )
            db.session.add(report)
            db.session.commit()

            flash(_('Add Report success.'), 'success')
        else:
            flash(_('The reporter is not belong to this course.'), 'error')

        return redirect_back()

    return render_template('admin/add_report.html', form=form)


@admin_bp.route('manage/report/<int:report_id>/delete', methods=['POST'])
@permission_required('MODERATOR_REPORT')
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)

    content = render_template(
        'logs/admin/delete_report.html',
        grade=report.grade, course=report.course_name, report=report.name)
    log = log_user(content)

    db.session.delete(report)
    db.session.commit()

    flash(_('Report deleted.'), 'info')
    return redirect_back()


@admin_bp.route('manage/record-table/<int:report_id>')
@permission_required('MODERATOR_RECORD_TABLE')
def manage_record(report_id):
    log = log_user(content=render_template('logs/admin/manage_record.html'))

    per_page = current_app.config['MANAGE_RECORD_TABLE_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = RecordTable.query.filter_by(report_id=report_id).order_by(
        RecordTable.time.desc()).paginate(page, per_page)
    form = DeleteRecordForm()

    return render_template(
        'admin/manage_record.html', pagination=pagination, form=form)


@admin_bp.route('manage/record-table/<int:record_id>', methods=['POST'])
@permission_required('MODERATOR_RECORD_TABLE')
def delete_record(record_id):
    record = RecordTable.query.get(record_id)

    content = render_template(
        'logs/admin/delete_record.html', username=record.review_number,
        name=record.review_name, report=record.report_name)
    log = log_user(content)

    db.session.delete(record)
    db.session.commit()

    flash(_('Record Table deleted.'), 'info')
    return redirect_back()


@admin_bp.route('manage/logs/system')
@permission_required('ADMINISTER')
def system_log():
    log_user(content=render_template('logs/admin/system_log.html'))

    file = os.path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.zip')
    packitup(current_app.config['SYSTEM_LOG_PATH'], file)

    flash(_('System logs dowdloaded.'), 'info')

    return send_file(file, as_attachment=True, attachment_filename='system logs.zip')


@admin_bp.route('manage/logs/user')
@permission_required('ADMINISTER')
def user_log():
    import pandas as pd

    log_user(content=render_template('logs/admin/user_log.html'))

    df = pd.read_sql_query(Log.query.statement, db.engine)
    df['number'] = df['user_id'].apply(lambda x: User.query.get(x).number)
    df['role'] = df['user_id'].apply(lambda x: User.query.get(x).role.name)

    df.drop(columns=['id', 'user_id'], inplace=True)

    file = os.path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.xlsx')
    zfile = file.replace('.xlsx', '.zip')
    df.to_excel(file, index=False)
    packitup(file, zfile)

    flash(_('User logs dowdloaded.'), 'info')

    return send_file(zfile, as_attachment=True, attachment_filename='user logs.zip')
