# -*- coding: utf-8 -*-

from functools import wraps

from flask import Markup, abort, flash, redirect, url_for
from flask_login import current_user


def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission_name):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.whoami(role):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator
