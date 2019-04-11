# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, url_for

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def index():
    return render_template('admin/index.html')
