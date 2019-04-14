# -*- coding: utf-8 -*-

from flask_babel import lazy_gettext as _l
from flask_ckeditor import CKEditorField
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (BooleanField, FloatField, IntegerField, PasswordField,
                     RadioField, StringField, SubmitField, TextField,
                     ValidationError)
from wtforms.validators import (AnyOf, DataRequired, Email, EqualTo,
                                InputRequired, Length, Optional, Regexp)

from recordit.models import User


class RegisterStudentForm(FlaskForm):
    username = StringField(
        _l('Username'),
        validators=[DataRequired(), InputRequired(), Length(12),
                    Regexp('^[0-9]*$', message=_l('The username should only contain 0-9.'))])
    name = StringField(
        _l('Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 20)])
    password = PasswordField(
        _l('Password'),
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')]
    )
    password2 = PasswordField(
        _l('Confirm password'),
        validators=[DataRequired(), InputRequired()])

    remark = CKEditorField(_l('Remark'), validators=[Optional()])
    submit = SubmitField(_l('Register'))

    def validate_username(self, field):
        if User.query.filter_by(number=field.data).first():
            raise ValidationError(_l('The username is already in use.'))


class RegisterTeacherForm(FlaskForm):
    username = StringField(
        _l('Username'),
        validators=[DataRequired(), InputRequired(), Length(4, 12),
                    Regexp('^[0-9]*$', message=_l('The username should only contain 0-9.'))])
    name = StringField(
        _l('Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 20)])
    password = PasswordField(
        _l('Password'),
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')]
    )
    password2 = PasswordField(
        _l('Confirm password'),
        validators=[DataRequired(), InputRequired()])

    remark = CKEditorField(_l('Remark'), validators=[Optional()])
    submit = SubmitField(_l('Register'))

    def validate_username(self, field):
        if User.query.filter_by(number=field.data).first():
            raise ValidationError(_l('The username is already in use.'))


class RegisterAdministratorForm(FlaskForm):
    username = StringField(
        _l('Username'),
        validators=[DataRequired(), InputRequired(), Length(1, 12),
                    Regexp('^[a-zA-Z0-9]*$', message=_l('The username should only contain a-z, A-Z and 0-9.'))]
    )
    name = StringField(
        _l('Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 20)]
    )
    password = PasswordField(
        _l('Password'),
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')]
    )
    password2 = PasswordField(
        _l('Confirm password'),
        validators=[DataRequired(), InputRequired()])

    remark = CKEditorField(_l('Remark'), validators=[Optional()])
    submit = SubmitField(_l('Register'))

    def validate_username(self, field):
        if User.query.filter_by(number=field.data).first():
            raise ValidationError(_l('The username is already in use.'))


class EditStudenteForm(FlaskForm):
    username = StringField(
        _l('Number'),
        validators=[DataRequired(), InputRequired(), Length(12),
                    Regexp('^[0-9]*$', message=_l('The username should only contain 0-9.'))]
    )
    name = StringField(
        _l('Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 20)]
    )
    remark = CKEditorField(_l('Remark'), validators=[Optional()])

    submit = SubmitField(_l('Edit'))

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(number=field.data).first():
            raise ValidationError(_l('The username is already in use.'))


class EditTeacherForm(FlaskForm):
    username = StringField(
        _l('Number'),
        validators=[DataRequired(), InputRequired(), Length(4),
                    Regexp('^[0-9]*$', message=_l('The username should only contain 0-9.'))]
    )
    name = StringField(
        _l('Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 20)]
    )
    remark = CKEditorField(_l('Remark'), validators=[Optional()])

    submit = SubmitField(_l('Edit'))

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(number=field.data).first():
            raise ValidationError(_l('The username is already in use.'))


class EditAdministratorForm(FlaskForm):
    username = StringField(
        _l('Number'),
        validators=[DataRequired(), InputRequired(), Length(12),
                    Regexp('^[a-zA-Z0-9]*$', message=_l('The username should only contain a-z, A-Z and 0-9.'))]
    )
    name = StringField(
        _l('Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 20)]
    )
    remark = CKEditorField(_l('Remark'), validators=[Optional()])

    submit = SubmitField(_l('Edit'))

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(number=field.data).first():
            raise ValidationError(_l('The username is already in use.'))


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        _l('New Password'),
        validators=[InputRequired(), DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField(
        _l('Confirm Password'),
        validators=[DataRequired(), InputRequired()])

    submit = SubmitField(_l('Change'))


class DeleteUserForm(FlaskForm):
    delete = SubmitField(_l('Delete'))


class AddCourseAdministratorForm(FlaskForm):
    name = StringField(
        _l('Name'),
        validators=[InputRequired(), DataRequired(), Length(1, 30)]
    )
    teacher = StringField(
        _l('Teacher Number'),
        validators=[InputRequired(), DataRequired(), Length(4, 12)]
    )
    grade = StringField(
        _l('Student Grade'),
        validators=[InputRequired(), DataRequired(), Length(4)]
    )

    remark = CKEditorField(_l('Remark'), validators=[Optional()])
    submit = SubmitField(_l('Add'))

    def validate_teacher(self, field):
        user = User.query.filter_by(number=field.data).first()
        if user is None:
            raise ValidationError(_l('The user is not existed.'))
        elif user.role.name != 'Teacher':
            raise ValidationError(_l('The user is not Teacher.'))

    def validate_grade(self, field):
        grades = User.all_grade()
        if field.data not in grades:
            raise ValidationError(_l('The grade is not existed.'))


class AddCourseTeacherForm(FlaskForm):
    name = StringField(
        _l('Name'),
        validators=[InputRequired(), DataRequired(), Length(1, 30)]
    )
    grade = StringField(
        _l('Student Grade'),
        validators=[InputRequired(), DataRequired(), Length(4)]
    )

    remark = CKEditorField(_l('Remark'), validators=[Optional()])
    submit = SubmitField(_l('Add'))

    def validate_grade(self, field):
        grades = User.all_grade()
        if field.data not in grades:
            raise ValidationError(_l('The grade is not existed.'))


class DeleteReportForm(FlaskForm):
    delete = SubmitField(_l('Delete'))


class AddReportForm(FlaskForm):
    name = StringField(
        _l('Report Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 30)]
    )
    speaker = StringField(
        _l('Speaker Number'),
        validators=[InputRequired(), DataRequired(), Length(1, 12)]
    )
    remark = CKEditorField(_l('Remark'), validators=[Optional()])
    submit = SubmitField(_l('Add'))

    def validate_speaker(self, field):
        user = User.query.filter_by(number=field.data).first()
        if user is None:
            raise ValidationError(_l('The speaker is not existed.'))
        elif user.role.name != 'Student':
            raise ValidationError(_l('The speaker is not Student.'))


class DeleteRecordForm(FlaskForm):
    delete = SubmitField(_l('Delete'))

class SwitchStateForm(FlaskForm):
    switch =  SubmitField(_l('Switch'))
