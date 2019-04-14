
# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import os

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user

from recordit.extensions import db
from recordit.models import Log


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


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            name = getattr(form, field).label.text
            flash(_("Error in the %(name)s field - %(error)s.", name=name, error=error), 'dark')


def log_user(content):
    log = Log(
        user_id=current_user.id,
        ip=request.remote_addr,
        content=content
    )

    db.session.add(log)
    db.session.commit()


def packitup(input_path, output_path):
    from zipfile import ZipFile

    with ZipFile(output_path, 'w') as z:
        if os.path.isdir(input_path):
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file == '.gitkeep':
                        continue
                    z.write(os.path.join(root, file), file)

        elif os.path.isfile(input_path):
            z.write(input_path, os.path.split(input_path)[1])
        else:
            abort(404)

