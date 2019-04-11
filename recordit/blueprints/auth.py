# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import _
from flask_login import (confirm_login, current_user, login_fresh,
                         login_required, login_user, logout_user)

from recordit.forms.auth import LoginForm
from recordit.models import User
from recordit.utils import log_user, redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(number=form.username.data).first()
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash(_('Login success.'), 'info')

                return redirect(url_for('user.index'))

        flash(_('Invalid email or password.'), 'warning')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Logout success.'), 'info')

    return redirect(url_for('front.index'))
