# -*- coding: utf-8 -*-

from flask import Blueprint, render_template


front_bp = Blueprint('front', __name__)


@front_bp.route('/')
def index():
    return render_template('front/index.html')


@front_bp.route('/about')
def about():
    return render_template('front/about.html')
