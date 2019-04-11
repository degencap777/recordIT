# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import _
from flask_login import current_user, login_required

from recordit.utils import log_user, redirect_back

front_bp = Blueprint('front', __name__)


@front_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))

    flash(_('Welcome~'), 'info')
    return render_template('front/index.html')


@front_bp.route('/about')
def about():
    flash(_('This is about page, make you know more about us.'), 'info')
    return render_template('front/about.html')
