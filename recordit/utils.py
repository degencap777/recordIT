
# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import os

from flask import (Markup, abort, current_app, flash, redirect,
                   render_template_string, request, url_for)
from flask_babel import _
from flask_login import current_user


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='front.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def log_user(content):
    log = Log(
        user_id=current_user.id,
        ip=request.remote_addr,
        content=content
    )

    db.session.add(log)
    db.session.commit()
