# -*- coding: utf-8 -*-

from flask import (Blueprint, abort, current_app, flash, render_template,
                   request, send_file)
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from recordit.decorators import permission_required, role_required
from recordit.extensions import db
from recordit.forms.admin import (
    AddCourseAdministratorForm, AddCourseTeacherForm, AddReportBatchForm,
    AddReportForm, ChangePasswordForm, DeleteRecordForm, DeleteReportForm,
    DeleteUserForm, EditAdministratorForm, EditStudenteForm, EditTeacherForm,
    RegisterAdministratorForm, RegisterBatchForm, RegisterStudentForm,
    RegisterTeacherForm, SwitchStateForm)
from recordit.models import Course, Log, RecordTable, Report, Role, User
from recordit.utils import (flash_errors, log_user, packitup, redirect_back,
                            safe_filename)

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
@role_required(['Teacher', 'Administrator'])
@fresh_login_required
@login_required
def login_protect():
    pass


@admin_bp.route('/')
def index():
    log_user(content=render_template('logs/admin/index.html'))

    user_count = User.query.count()
    role_administrator = Role.query.filter_by(name='Administrator').one()
    admin_count = User.query.filter_by(role_id=role_administrator.id).count()
    role_teacher = Role.query.filter_by(name='Teacher').one()
    teacher_count = User.query.filter_by(role_id=role_teacher.id).count()
    role_student = Role.query.filter_by(name='Student').one()
    student_count = User.query.filter_by(role_id=role_student.id).count()
    log_count = Log.query.count()
    course_count = Course.query.count()

    if current_user.is_teacher:
        course_count = Course.query.filter_by(
            teacher_id=current_user.id).count()

    return render_template(
        'admin/index.html', user_count=user_count, admin_count=admin_count,
        teacher_count=teacher_count, student_count=student_count,
        course_count=course_count, log_count=log_count)


@admin_bp.route('/manage/user')
@permission_required('ADMINISTER')
def manage_user():
    log_user(content=render_template('logs/admin/manage_user.html'))

    # 'all', 'student', 'teacher', 'administrator'
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MANAGE_USER_PER_PAGE']
    role_administrator = Role.query.filter_by(
        name='Administrator').one()
    role_teacher = Role.query.filter_by(name='Teacher').one()
    role_student = Role.query.filter_by(name='Student').one()

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
    log_user(content)

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
        log_user(content)

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
            log_user(content)

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
        log_user(content)

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
        log_user(content)

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
        log_user(content)

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


@admin_bp.route('manage/user/register/batch', methods=['GET', 'POST'])
@permission_required('ADMINISTER')
def register_batch():
    from os import path
    from uuid import uuid4

    import pandas as pd

    form = RegisterBatchForm()
    if form.validate_on_submit():
        file = request.files.get('file')
        path = path.join(
            current_app.config['FILE_CACHE_PATH'], safe_filename(file.filename))
        file.save(path)
        df = pd.read_excel(path)

        if not set(df.columns) >= set(['number', 'name', 'role', 'remark', 'password']):
            flash(
                _("The EXCEL file columns should contain 'number', 'name', 'role', 'remark' and 'password'."), 'error')
            return redirect_back()

        for i, row in df.iterrows():
            content = render_template(
                'logs/admin/register_user.html',
                username=row['number'], name=row['name'])
            log_user(content)

            if not User.query.filter_by(number=row['number']).one_or_none():
                if row['role'] not in ['Teacher', 'Student']:
                    flash(_("%(number)s role should be 'Student' or 'Teacher'.",
                            number=row['number']), 'error')
                else:
                    user = User(
                        number=row['number'],
                        name=row['name'],
                        remark=row['remark']
                    )
                    user.set_password(row['password'])
                    user.set_role(row['role'])
                    db.session.add(user)

                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()
            else:
                flash(_("%(number)s is already existed.",
                        number=row['number']), 'error')

        flash_errors(form)
        flash(_('Register success.'), 'success')
        return redirect_back()

    return render_template('admin/register_batch.html', form=form)


@admin_bp.route('manage/course')
@permission_required('MODERATOR_COURSE')
def manage_course():
    log_user(content=render_template('logs/admin/manage_course.html'))

    per_page = current_app.config['MANAGE_COURSE_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.filter_by(
        teacher_id=current_user.id).order_by(Course.date.desc()).paginate(page, per_page)
    if current_user.is_admin:
        pagination = Course.query.order_by(
            Course.date.desc()).paginate(page, per_page)

    form = SwitchStateForm()
    return render_template('admin/manage_course.html', pagination=pagination, form=form)


@admin_bp.route('manage/course/<int:course_id>/switch-state', methods=['POST'])
@permission_required('MODERATOR_COURSE')
def switch_course_state(course_id):
    course = Course.query.get_or_404(course_id)

    content = render_template(
        'logs/admin/switch_course_state.html', grade=course.grade, name=course.name)
    log_user(content)

    if current_user.is_teacher and course.teacher_id != current_user.id:
        abort(403)
    course.active = not course.active
    db.session.commit()

    for report in Report.query.filter_by(course_id=course.id).all():
        report.active = not report.active
    db.session.commit()

    flash(_('Course state switched.'), 'success')
    return redirect_back()


@admin_bp.route('manage/course/add', methods=['GET', 'POST'])
@permission_required('MODERATOR_COURSE')
def add_course():
    form = AddCourseTeacherForm()
    if current_user.is_admin:
        form = AddCourseAdministratorForm()

    if form.validate_on_submit():
        content = render_template(
            'logs/admin/add_course.html', grade=form.grade.data, name=form.name.data)
        log_user(content)

        if current_user.is_teacher:
            teacher_id = current_user.id
        else:
            teacher_id = form.teacher.data

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
    if current_user.is_teacher:
        course = Course.query.get_or_404(course_id)
        if course.teacher_id != current_user.id:
            abort(403)

    log_user(content=render_template('logs/admin/manage_report.html'))

    per_page = current_app.config['MANAGE_REPORT_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = Report.query.filter_by(course_id=course_id).order_by(
        Report.date.desc()).paginate(page, per_page)

    deleteform = DeleteReportForm()
    switchform = SwitchStateForm()
    return render_template(
        'admin/manage_report.html', pagination=pagination, deleteform=deleteform, switchform=switchform)


@admin_bp.route('manage/report/<int:course_id>/download')
@permission_required('MODERATOR_REPORT')
def download_report(course_id):
    from os import path
    from uuid import uuid4

    import pandas as pd

    course = Course.query.get(course_id)
    content = render_template(
        'logs/admin/download_report.html', course=course.name)
    log_user(content=content)

    query = RecordTable.query.join(Report).filter_by(course_id=course_id)
    df = pd.read_sql_query(query.statement, db.engine)

    df['grade'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).grade))
    df['course_name'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).course_name))
    df['report_name'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).name))
    df['speaker_name'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).speaker_name))
    df['speaker_number'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).speaker_number))
    df['reviewer_name'] = (
        df['id'].apply(lambda x: RecordTable.query.get(x).reviewer_name))
    df['reviewer_number'] = (
        df['id'].apply(lambda x: RecordTable.query.get(x).reviewer_number))
    df['teacher_name'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).teacher_name))
    df['teacher_number'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).teacher_number))

    df.drop(columns=['id', 'report_id', 'user_id'], inplace=True)

    file = path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.xlsx')
    df.to_excel(file, index=False)

    zfile = file.replace('.xlsx', '.zip')

    images = [path.join(current_app.config['UPLOAD_PATH'], rt.file)
              for report in course.reports for rt in report.recordtables if rt.file]
    packitup(file, zfile, mode='w')
    packitup(images, zfile, mode='a', diff=True)

    flash(_('The file is already downloaded.'), 'success')

    return send_file(zfile, as_attachment=True, attachment_filename='reports.zip')


@admin_bp.route('manage/report/<int:report_id>/switch-state', methods=['POST'])
@permission_required('MODERATOR_REPORT')
def switch_report_state(report_id):
    report = Report.query.get_or_404(report_id)
    content = render_template(
        'logs/admin/switch_report_state.html',
        grade=report.grade, course=report.course_name, report=report.name)
    log_user(content)

    if current_user.is_teacher and report.teacher_id != current_user.id:
        abort(403)

    report.active = not report.active
    db.session.commit()
    flash(_('Report state switched.'), 'success')
    return redirect_back()


@admin_bp.route('manage/report/<int:course_id>/add', methods=['GET', 'POST'])
@permission_required('MODERATOR_REPORT')
def add_report(course_id):
    form = AddReportForm()
    if current_user.is_teacher:
        course = Course.query.get_or_404(course_id)
        if course.teacher_id != current_user.id:
            abort(403)

    if form.validate_on_submit():
        course = Course.query.get_or_404(course_id)
        user = User.query.filter_by(number=form.speaker.data).one()
        if course.grade == user.grade:
            content = render_template(
                'logs/admin/add_report.html', course=course.name, grade=course.grade,
                username=user.number, name=user.name, report=form.name.data)
            log_user(content)

            report = Report(
                course_id=course_id,
                speaker_id=user.id,
                name=form.name.data,
                remark=form.remark.data
            )
            db.session.add(report)
            db.session.commit()

            flash(_('Add Report success.'), 'success')
        else:
            flash(_('The speaker is not belong to this course.'), 'error')

        return redirect_back()

    return render_template('admin/add_report.html', form=form)


@admin_bp.route('manage/report/<int:course_id>/batch', methods=['GET', 'POST'])
@permission_required('MODERATOR_REPORT')
def add_report_batch(course_id):
    from os import path
    from uuid import uuid4

    import pandas as pd

    form = AddReportBatchForm()
    if form.validate_on_submit():
        file = request.files.get('file')
        path = path.join(
            current_app.config['FILE_CACHE_PATH'], safe_filename(file.filename))
        file.save(path)
        df = pd.read_excel(path)

        if not set(df.columns) >= set(['name', 'number', 'remark']):
            flash(
                _("The EXCEL file columns should contain 'name', 'number' and 'remark'."), 'error')
            return redirect_back()

        course = Course.query.get_or_404(course_id)
        for i, row in df.iterrows():
            number = row['number']
            if isinstance(number, (int, float)):
                number = str(int(number))

            user = User.query.filter_by(number=number).one()
            if user:
                if course.grade == user.grade:
                    content = render_template(
                        'logs/admin/add_report.html', course=course.name, grade=course.grade,
                        username=user.number, name=user.name, report=row['name'])
                    log_user(content)

                    report = Report(
                        course_id=course_id,
                        speaker_id=user.id,
                        name=row['name'],
                        remark=row['remark']
                    )
                    db.session.add(report)
                    db.session.commit()
                else:
                    flash(
                        _('The %(speaker)s is not belong to this course.', speaker=user.number), 'error')
            else:
                flash(_("%(number)s is not existed.",
                        number=number), 'error')

        flash_errors(form)
        flash(_('Add Report success.'), 'success')
        return redirect_back()

    return render_template('admin/add_report_batch.html', form=form)


@admin_bp.route('manage/report/<int:report_id>/delete', methods=['POST'])
@permission_required('MODERATOR_REPORT')
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    content = render_template(
        'logs/admin/delete_report.html',
        grade=report.grade, course=report.course_name, report=report.name)
    log_user(content)

    if current_user.is_teacher:
        if report.teacher_id != current_user.id:
            abort(403)

    db.session.delete(report)
    db.session.commit()

    flash(_('Report deleted.'), 'info')
    return redirect_back()


@admin_bp.route('manage/record-table/<int:report_id>')
@permission_required('MODERATOR_RECORD_TABLE')
def manage_record(report_id):
    log_user(content=render_template('logs/admin/manage_record.html'))
    report = Report.query.get_or_404(report_id)

    if current_user.is_teacher:
        if report.teacher_id != current_user.id:
            abort(403)

    per_page = current_app.config['MANAGE_RECORD_TABLE_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = RecordTable.query.filter_by(report_id=report_id).order_by(
        RecordTable.time.desc()).paginate(page, per_page)
    form = DeleteRecordForm()

    return render_template(
        'admin/manage_record.html', pagination=pagination, form=form)


@admin_bp.route('manage/record-table/<string:file>/download')
@permission_required('MODERATOR_RECORD_TABLE')
def download_file(file):
    from os import path

    content = render_template('logs/admin/download_file.html', file=file)
    log_user(content=content)

    path = path.join(current_app.config['UPLOAD_PATH'], file)
    return send_file(path)


@admin_bp.route('manage/record-table/<int:report_id>/download')
@permission_required('MODERATOR_RECORD_TABLE')
def download_record(report_id):
    from os import path
    from uuid import uuid4

    import pandas as pd

    report = Report.query.get(report_id)
    content = render_template(
        'logs/admin/download_record.html', report=report.name, username=report.speaker_number)
    log_user(content=content)

    query = RecordTable.query.filter_by(report_id=report_id)
    df = pd.read_sql_query(query.statement, db.engine)

    df['grade'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).grade))
    df['course_name'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).course_name))
    df['report_name'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).name))
    df['reviewer_name'] = (
        df['id'].apply(lambda x: RecordTable.query.get(x).reviewer_name))
    df['reviewer_number'] = (
        df['id'].apply(lambda x: RecordTable.query.get(x).reviewer_number))
    df['speaker_name'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).speaker_name))
    df['speaker_number'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).speaker_number))
    df['teacher_name'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).teacher_name))
    df['teacher_number'] = (
        df['report_id'].apply(lambda x: Report.query.get(x).teacher_number))

    df.drop(columns=['id', 'report_id', 'user_id'], inplace=True)

    file = path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.xlsx')
    df.to_excel(file, index=False)

    zfile = file.replace('.xlsx', '.zip')
    images = [path.join(current_app.config['UPLOAD_PATH'], rt.file)
              for rt in report.recordtables if rt.file]
    packitup(file, zfile, mode='w')
    packitup(images, zfile, mode='a', diff=True)

    flash(_('The file is already downloaded.'), 'success')

    return send_file(zfile, as_attachment=True, attachment_filename='records.zip')


@admin_bp.route('manage/record-table/<int:record_id>', methods=['POST'])
@permission_required('MODERATOR_RECORD_TABLE')
def delete_record(record_id):
    record = RecordTable.query.get_or_404(record_id)

    content = render_template(
        'logs/admin/delete_record.html', username=record.reviewer_number,
        name=record.reviewer_name, report=record.report_name)
    log_user(content)

    if current_user.is_teacher:
        if record.teacher_id != current_user.id:
            abort(403)

    db.session.delete(record)
    db.session.commit()

    flash(_('Record Table deleted.'), 'info')
    return redirect_back()


@admin_bp.route('manage/logs/system')
@permission_required('ADMINISTER')
def system_log():
    from os import path
    from uuid import uuid4

    log_user(content=render_template('logs/admin/system_log.html'))

    file = path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.zip')
    packitup(current_app.config['SYSTEM_LOG_PATH'], file)

    flash(_('System logs dowdloaded.'), 'info')

    return send_file(file, as_attachment=True, attachment_filename='system logs.zip')


@admin_bp.route('manage/logs/user')
@permission_required('ADMINISTER')
def user_log():
    from os import path
    from uuid import uuid4

    import pandas as pd

    log_user(content=render_template('logs/admin/user_log.html'))

    df = pd.read_sql_query(Log.query.statement, db.engine)
    df['number'] = df['user_id'].apply(lambda x: User.query.get(x).number)
    df['role'] = df['user_id'].apply(lambda x: User.query.get(x).role.name)

    df.drop(columns=['id', 'user_id'], inplace=True)

    file = path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.xlsx')
    zfile = file.replace('.xlsx', '.zip')
    df.to_excel(file, index=False)
    packitup(file, zfile)

    flash(_('User logs dowdloaded.'), 'info')

    return send_file(zfile, as_attachment=True, attachment_filename='user logs.zip')
