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
            raise ValidationError('The username is already in use.')


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
            raise ValidationError('The username is already in use.')


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
            raise ValidationError('The username is already in use.')


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
            raise ValidationError('The username is already in use.')


class EditTeacherForm(FlaskForm):
    username = StringField(
        _l('Number'),
        validators=[DataRequired(), InputRequired(), Length(4, 12),
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
            raise ValidationError('The username is already in use.')


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
            raise ValidationError('The username is already in use.')


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
