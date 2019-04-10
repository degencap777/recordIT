# -*- coding: utf-8 -*-

from flask import current_app, request
from flask_apscheduler import APScheduler
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask_bootstrap import Bootstrap
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import AnonymousUserMixin, LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
toolbar = DebugToolbarExtension()
babel = Babel()
cache = Cache()
scheduler = APScheduler()


@login_manager.user_loader
def load_user(user_id):
    from recordit.models import User
    return User.query.get(int(user_id))


login_manager.login_view = 'auth.login'
login_manager.login_message = _l('Please log in to access this page.')
login_manager.login_message_category = 'warning'
login_manager.refresh_view = 'auth.re_authenticate'
login_manager.needs_refresh_message = _l('In order to protect your account security, please log in again.')
login_manager.needs_refresh_message_category = 'warning'
login_manager.session_protection = "strong"


class Guest(AnonymousUserMixin):

    def can(self, permission_name):
        return False

    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = Guest


@babel.localeselector
def get_locale():
    if current_user.is_authenticated and current_user.locale:
        return current_user.locale

    locale = request.cookies.get('locale')
    if locale:
        return locale

    return request.accept_languages.best_match(current_app.config['MMCS_LOCALES'])
