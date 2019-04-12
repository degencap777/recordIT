# -*- coding: utf-8 -*-

from flask_babel import lazy_gettext as _l
from flask_ckeditor import CKEditorField
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import (DataRequired, EqualTo, InputRequired, Length,
                                Optional, Regexp)

from recordit.models import User


class EditStudenteForm(FlaskForm):
    username = StringField(
        _l('Number'),
        validators=[DataRequired(), InputRequired(), Length(12),
                    Regexp('^[0-9]*$', message=_l('The username should only contain 0-9.'))],
        render_kw={'disabled': 'disabled'}
    )
    name = StringField(
        _l('Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 20)],
        render_kw={'disabled': 'disabled'}
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
                    Regexp('^[0-9]*$', message=_l('The username should only contain 0-9.'))],
        render_kw={'disabled': 'disabled'}
    )
    name = StringField(
        _l('Name'),
        validators=[DataRequired(), InputRequired(), Length(1, 20)],
        render_kw={'disabled': 'disabled'}
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
    old_password = PasswordField(
        _l('Old Password'), validators=[DataRequired(), InputRequired()])
    password = PasswordField(
        _l('New Password'),
        validators=[InputRequired(), DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField(
        _l('Confirm Password'),
        validators=[DataRequired(), InputRequired()])

    submit = SubmitField(_l('Change'))
