# -*- coding: utf-8 -*-

import datetime

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from recordit.extensions import db

# relationship table
roles_permissions = db.Table(
    'roles_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
)


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship(
        'Role', secondary=roles_permissions, back_populates='permissions')


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    users = db.relationship('User', back_populates='role')
    permissions = db.relationship(
        'Permission', secondary=roles_permissions, back_populates='roles')

    @staticmethod
    def init_role():
        roles_permissions_map = {
            'Student': ['RECORD', 'UPLOAD'],
            'Teacher': ['RECORD', 'UPLOAD', 'MODERATOR_COURSE', 'MODERATOR_REPORT', 'MODERATOR_RECORD_TABLE'],
            'Administrator': ['RECORD', 'UPLOAD', 'MODERATOR_COURSE', 'MODERATOR_REPORT', 'MODERATOR_RECORD_TABLE', 'MODERATOR_LOG', 'ADMINISTER']
        }

        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)

            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(
                    name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)

        db.session.commit()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(12), unique=True, index=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128))

    remark = db.Column(db.Text)
    locale = db.Column(db.String(20), default='zh_Hans_CN')

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', back_populates='users')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.init_role()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def init_role(self):
        if self.role is None:
            if self.number == current_app.config['ADMIN_NUMBER']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(name='Student').first()
            db.session.commit()

    def set_role(self, role):
        self.role = Role.query.filter_by(name=role).first()

    @property
    def username(self):
        return self.number

    @property
    def is_admin(self):
        return self.role.name == 'Administrator'

    @property
    def is_teacher(self):
        return self.role.name == 'Teacher'

    @property
    def is_student(self):
        return self.role.name == 'Student'

    @property
    def grade(self):
        if self.is_student:
            return self.number[:4]

    @classmethod
    def all_grade(self):
        role = Role.query.filter_by(name='Student').first()
        studetns = User.query.filter_by(role_id=role.id).all()
        studetn_grades = [user.grade for user in studetns]
        return set(studetn_grades)

    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permissions

    def whoami(self, role):
        return self.role.name == role


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(30), nullable=False)
    grade = db.Column(db.Integer, nullable=False)

    active = db.Column(db.Boolean, default=True)
    date = db.Column(db.Date, index=True, default=datetime.date.today)
    remark = db.Column(db.Text)

    @property
    def is_active(self):
        return self.active

    @property
    def teacher_name(self):
        return User.query.get(self.teacher_id).name

    @property
    def teacher_number(self):
        return User.query.get(self.teacher_id).number


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(30), nullable=False)
    score = db.Column(db.Integer)

    active = db.Column(db.Boolean, default=True)
    date = db.Column(db.Date, index=True, default=datetime.date.today)
    remark = db.Column(db.Text)

    @property
    def grade(self):
        return Course.query.get(self.course_id).grade

    @property
    def course_name(self):
        return Course.query.get(self.course_id).name

    @property
    def is_active(self):
        return Course.query.get(self.course_id).is_active and self.active

    @property
    def reporter_name(self):
        return User.query.get(self.reporter_id).name

    @property
    def reporter_number(self):
        return User.query.get(self.reporter_id).number

    @property
    def teacher_name(self):
        return Course.query.get(self.course_id).teacher_name

    @property
    def teacher_number(self):
        return Course.query.get(self.course_id).teacher_number


class RecordTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer, nullable=False)

    time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    remark = db.Column(db.Text)

    @property
    def is_active(self):
        return Report.query.get(self.report_id).is_active

    @property
    def report_name(self):
        return Report.query.get(self.report_id).name

    @property
    def reviewer_name(self):
        return User.query.get(self.user_id).name

    @property
    def reviewer_number(self):
        return User.query.get(self.user_id).number


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    ip = db.Column(db.String(128))
    time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    content = db.Column(db.String(50))
