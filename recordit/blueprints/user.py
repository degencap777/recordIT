# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from recordit.extensions import db
from recordit.forms.user import ChangePasswordForm, EditProfileForm
from recordit.utils import redirect_back

user_bp = Blueprint('user', __name__)


@login_required
def login_protect():
    pass


@user_bp.route('/')
def index():
    flash(_("Welcome %(name)s", name=current_user.name), 'info')
    return render_template('user/index.html')


@user_bp.route('/settings')
def settings():
    return redirect(url_for('.edit_profile'))


@user_bp.route('/settings/profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.remark = form.remark.data
        db.session.commit()

        flash(_('Profile updated.'), 'success')
        redirect_back()

    form.number.data = current_user.number
    form.name.data = current_user.name
    form.remark.data = current_user.remark

    return render_template('user/settings/edit_profile.html', form=form)


@user_bp.route('/settings/change-password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()

            flash(_('Password updated.'), 'success')
            redirect_back()
        else:
            flash(_('Old password is incorrect.'), 'warning')

    return render_template('user/settings/change_password.html', form=form)
