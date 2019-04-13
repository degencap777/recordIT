# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from recordit.extensions import db
from recordit.forms.user import (ChangePasswordForm, EditAdministratorForm,
                                 EditStudenteForm, EditTeacherForm)
from recordit.utils import redirect_back, log_user

user_bp = Blueprint('user', __name__)


@login_required
def login_protect():
    pass


@user_bp.route('/')
def index():
    flash(_("Welcome~ %(name)s", name=current_user.name), 'info')
    return render_template('user/index.html')


@user_bp.route('/settings')
def settings():
    return redirect(url_for('.edit_profile'))


@user_bp.route('/settings/profile', methods=['GET', 'POST'])
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
