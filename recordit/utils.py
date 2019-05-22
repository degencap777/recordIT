
# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from os import path

from flask import abort, current_app, flash, redirect, request, url_for
from flask_babel import _
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
            flash(_("Error in the %(name)s field - %(error)s.",
                    name=name, error=error), 'dark')


def log_user(content):
    log = Log(
        user_id=current_user.id,
        ip=request.remote_addr,
        content=content
    )

    db.session.add(log)
    db.session.commit()


def packitup(input_paths, output_path, diff=False, names=None, mode='w'):
    from os import listdir, sep, walk
    from zipfile import ZipFile

    with ZipFile(output_path, mode) as z:
        if diff:
            if names:
                for input_path, name in zip(input_paths, names):
                    z.write(input_path, name)
            else:
                for input_path in input_paths:
                    name = path.join(*input_path.split(sep)[-2:])
                    z.write(input_path, name)
        else:
            if path.isdir(input_paths):
                partent = input_paths.split(sep)[-1]
                for file in listdir(input_paths):
                    if file == '.gitkeep':
                        continue
                    z.write(path.join(input_paths, file), path.join(partent, file))
            elif path.isfile(input_paths):
                name = names if names is not None else path.split(input_paths)[-1]
                z.write(input_paths, name)
            else:
                abort(404)


def safe_filename(filename):
    from pypinyin import lazy_pinyin
    from werkzeug.utils import secure_filename

    filename = secure_filename(''.join(lazy_pinyin(filename)))

    return filename


def gen_uuid(filename):
    from uuid import uuid1

    return uuid1().hex + path.splitext(filename)[-1]


def allowed_file(filename):

    return ('.' in filename
            and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])
