# -*- coding: utf-8 -*-

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from recordit.decorators import permission_required
from recordit.extensions import db
from recordit.forms.user import (ChangePasswordForm, EditAdministratorForm,
                                 EditStudenteForm, EditTeacherForm, ReviewForm)
from recordit.models import Course, RecordTable, Report, User
from recordit.utils import log_user, redirect_back

user_bp = Blueprint('user', __name__)


@user_bp.before_request
@login_required
def login_protect():
    pass


@user_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    if current_user.is_admin:
        pagination = Report.query.filter_by(active=True).join(Course).filter(Course.active).order_by(
            Report.date).paginate(page, current_app.config['USER_REPORT_PER_PAGE'])
    elif current_user.is_teacher:
        pagination = Report.query.filter_by(active=True).join(Course).filter(
            Course.teacher_id == current_user.id, Course.active).order_by(
            Report.date).paginate(page, current_app.config['USER_REPORT_PER_PAGE'])
    else:
        pagination = Report.query.filter(Report.active, Report.speaker_id != current_user.id).join(Course).filter(
            Course.grade == current_user.grade, Course.active).order_by(
            Report.date).paginate(page, current_app.config['USER_REPORT_PER_PAGE'])

    flash(_("Welcome~ %(name)s", name=current_user.name), 'info')
    return render_template('user/index.html', pagination=pagination)


@user_bp.route('/review/<int:report_id>', methods=['GET', 'POST'])
@permission_required('RECORD')
@fresh_login_required
def review(report_id):
    form = ReviewForm()
    report = Report.query.get_or_404(report_id)
    if current_user.is_student and current_user.id == report.speaker_id:
        abort(403)
    elif current_user.is_teacher and current_user.id != report.teacher_id:
        abort(403)
    else:
        record = report.search_recordtabel(current_user.id)
        if form.validate_on_submit():
            content = render_template(
                'logs/user/reivew.html', course=report.course_name,
                number=report.speaker_number, name=report.speaker_name, report=report.name)
            log_user(content=content)

            upper = current_app.config['RECORD_TABLE_UPPER_LIMIT']
            lower = current_app.config['RECORD_TABLE_LOWER_LIMIT']
            if lower <= form.score.data <= upper:
                if record is None:
                    record = RecordTable(
                        report_id=report.id,
                        user_id=current_user.id,
                        score=form.score.data,
                        remark=form.remark.data
                    )
                    db.session.add(record)
                else:
                    record.score = form.score.data
                    record.remark = form.remark.data

                db.session.commit()
                flash(_('Reviewed success.'), 'success')
            else:
                flash(_('The score out of range from %(lower)s to %(upper)s.',
                        lower=lower, upper=upper), 'error')

            return redirect_back()

        if record is not None:
            form.score.data = record.score
            form.remark.data = record.remark

    return render_template('user/review.html', form=form)


@user_bp.route('/settings')
def settings():
    return redirect(url_for('.edit_profile'))


@user_bp.route('/settings/profile', methods=['GET', 'POST'])
@fresh_login_required
def edit_profile():
    if current_user.is_admin:
        form = EditAdministratorForm()
    elif current_user.is_teacher:
        form = EditTeacherForm()
    else:
        form = EditStudenteForm()

    if form.validate_on_submit():
        log_user(
            content=render_template('logs/user/settings/edit_profile.html'))

        current_user.remark = form.remark.data
        db.session.commit()

        flash(_('Profile updated.'), 'success')
        redirect_back()

    form.username.data = current_user.number
    form.name.data = current_user.name
    form.remark.data = current_user.remark

    return render_template('user/settings/edit_profile.html', form=form)


@user_bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        log_user(
            content=render_template('logs/user/settings/change_password.html'))

        current_user.set_password(form.password.data)
        db.session.commit()

        flash(_('Password updated.'), 'success')
        redirect_back()

    return render_template('user/settings/change_password.html', form=form)
