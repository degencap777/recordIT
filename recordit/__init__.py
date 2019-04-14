# -*- coding: utf-8 -*-

import logging
import os
from datetime import timedelta
from logging.handlers import RotatingFileHandler, SMTPHandler

import click
from flask import Flask, render_template, request, session
from flask_babel import _
from flask_wtf.csrf import CSRFError

from recordit.blueprints.auth import auth_bp
from recordit.blueprints.admin import admin_bp
from recordit.blueprints.user import user_bp
from recordit.blueprints.front import front_bp
from recordit.extensions import (babel, bootstrap, cache, ckeditor, csrf, db,
                                 login_manager, scheduler, toolbar, moment)
from recordit.settings import basedir, config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('recordit')
    app.config.from_object(config[config_name])

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)
    register_logging(app)
    register_hook(app)

    return app


def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    formatter = RequestFormatter(
        '[%(asctime)s] - %(name)s - %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    file_handler = RotatingFileHandler(
        app.config['SYSTEM_LOG_PATH'],
        maxBytes=10 * 1024 * 1024, backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=app.config['ADMIN_EMAIL'],
        subject='recordit Application Error',
        credentials=('apikey', app.config['MAIL_PASSWORD']))

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(formatter)

    if not app.debug:
        app.logger.addHandler(mail_handler)
        app.logger.addHandler(file_handler)


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app)
    cache.init_app(app)
    ckeditor.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)
    scheduler.init_app(app)
    scheduler.start()


def register_blueprints(app):
    app.register_blueprint(front_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        code = 400
        info = _('Bad Request')
        return render_template('errors.html', code=code, info=info), code

    @app.errorhandler(401)
    def unauthorized(e):
        code = 401
        info = _('Unauthorized')
        return render_template('errors.html', code=code, info=info), code

    @app.errorhandler(403)
    def forbidden(e):
        code = 403
        info = _('Forbidden')
        return render_template('errors.html', code=code, info=info), code

    @app.errorhandler(404)
    def page_not_found(e):
        code = 404
        info = _('Page Not Found')
        return render_template('errors.html', code=code, info=info), code

    @app.errorhandler(405)
    def method_not_allowed(e):
        code = 405
        info = _('Method not allowed')
        return render_template('errors.html', code=code, info=info), code

    @app.errorhandler(413)
    def too_large(e):
        code = 413
        info = _('Upload too large')
        return render_template('errors.html', code=code, info=info), code

    @app.errorhandler(500)
    def internal_server_error(e):
        code = 500
        info = _('Internal Server Error Explained')
        return render_template('errors.html', code=code, info=info), code

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        code = 400
        info = _('Handle CSRF Error')
        return render_template('errors.html', code=code, info=info), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def init(drop):
        """Initialize app."""

        from recordit.models import  Role
        from recordit.fakes import fake_admin

        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')

        click.echo('Initializing the database...')
        db.create_all()

        click.echo('Initializing the roles and permissions...')
        Role.init_role()

        click.echo('Generating the default administrator...')
        fake_admin()

        if os.system('pybabel compile -d recordit/translations'):
            raise RuntimeError('compile command failed')

        click.echo('Done.')

    @app.cli.command()
    @click.option('--teacher', default=3, help='Quantity of teachers, default is 3.')
    @click.option('--student', default=20, help='Quantity of students, default is 20.')
    @click.option('--course', default=3, help='Quantity of courses, default is 3.')
    @click.option('--report', default=5, help='Quantity of reports, default is 5.')
    @click.option('--record', default=30, help='Quantity of records, default is 30.')
    def forge(teacher, student, course, report, record):
        """Generate fake data."""

        from recordit.fakes import fake_admin, fake_teacher, fake_student, fake_course, fake_report, fake_record

        db.drop_all()
        db.create_all()

        click.echo('Initializing the roles and permissions...')
        Role.init_role()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d teachers...' % teacher)
        fake_teacher(teacher)

        click.echo('Generating %d students...' % student)
        fake_student(student, grade='2017')

        click.echo('Generating %d students...' % student)
        fake_student(student, grade='2016')

        click.echo('Generating %d courses...' % course)
        fake_course(course)

        click.echo('Generating %d reports...' % report)
        fake_report(report)

        click.echo('Generating %d records...' % record)
        fake_record(record)

        click.echo('Done.')

    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('locale')
    def init(locale):
        """Initialize a new language."""

        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system(
                'pybabel init -i messages.pot -d recordit/translations -l ' + locale):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d recordit/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d recordit/translations'):
            raise RuntimeError('compile command failed')


def register_hook(app):
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=10)
