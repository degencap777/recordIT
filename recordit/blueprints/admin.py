# -*- coding: utf-8 -*-

from flask import (Blueprint, current_app, flash, render_template, request,
                   url_for)
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from recordit.decorators import permission_required
from recordit.extensions import db
from recordit.forms.admin import (ChangePasswordForm, DeleteUserForm,
                                  EditAdministratorForm, EditStudenteForm,
                                  EditTeacherForm, RegisterAdministratorForm,
                                  RegisterStudentForm, RegisterTeacherForm)
from recordit.models import Course, Log, RecordTable, Report, Role, User
from recordit.utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
@login_required
def login_protect():
    pass


@admin_bp.route('/')
def index():
    user_count = User.query.count()
    role_administrator = Role.query.filter_by(name='Administrator').first()
    admin_count = User.query.filter(
        User.role_id == role_administrator.id).count()
    role_teacher = Role.query.filter_by(name='Teacher').first()
    teacher_count = User.query.filter(User.role_id == role_teacher.id).count()
    role_student = Role.query.filter_by(name='Student').first()
    student_count = User.query.filter(User.role_id == role_student.id).count()

    course_count = Course.query.count()
    log_count = Log.query.count()

    return render_template(
        'admin/index.html', user_count=user_count, admin_count=admin_count,
        teacher_count=teacher_count, student_count=student_count, course_count=course_count, log_count=log_count)


@admin_bp.route('/manage/user')
@permission_required('ADMINISTER')
def manage_user():
    # 'all', 'student', 'teacher', 'administrator'
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MANAGE_USER_PER_PAGE']
    role_administrator = Role.query.filter_by(name='Administrator').first()
    role_teacher = Role.query.filter_by(name='Teacher').first()
    role_student = Role.query.filter_by(name='Student').first()

    delForm = DeleteUserForm()

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

    return render_template('admin/manage_user.html', pagination=pagination, page=page, delForm=delForm)


@admin_bp.route('manage/user/<int:user_id>/delete', methods=['POST'])
@permission_required('ADMINISTER')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
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
    return render_template('admin/manage_course.html')


@admin_bp.route('manage/course/add')
@permission_required('MODERATOR_COURSE')
def add_course():
    pass


@admin_bp.route('manage/report')
@permission_required('MODERATOR_REPORT')
def manage_report():
    pass


@admin_bp.route('manage/report/<int:report_id>/edit', methods=['GET', 'POST'])
@permission_required('MODERATOR_REPORT')
def edit_report():
    pass


@admin_bp.route('manage/report/add', methods=['GET', 'POST'])
@permission_required('MODERATOR_REPORT')
def add_report():
    pass


@admin_bp.route('manage/report/<int:report_id>/delete', methods=['POST'])
@permission_required('MODERATOR_REPORT')
def delete_report(user_id):
    pass
