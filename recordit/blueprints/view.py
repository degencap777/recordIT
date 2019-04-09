# -*- coding: utf-8 -*-

import os

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)

view_bp = Blueprint('view', __name__)


@view_bp.route('/')
def index():
    return render_template('front/index.html')


@view_bp.route('/base')
def base():
    return render_template('base.html')


@view_bp.route('/login')
def login():
    return render_template('auth/login.html')


@view_bp.route('/about')
def about():
    return render_template('front/about.html')
