import enum
from datetime import date
from datetime import timedelta
from flask_wtf import FlaskForm
from wtforms import ValidationError, validators, Form
from wtforms.fields import (
    DateField,
    SelectMultipleField,
    SubmitField,
)


class ScrapingDataQueryFilter(FlaskForm):
    to_date = DateField(
        validators=[validators.Optional()]
    )
    from_date = DateField(
        validators=[validators.Optional()],
    )
    files_name = SelectMultipleField(
        validators=[validators.Optional()],
    )
    submit = SubmitField()
