from flask_wtf import FlaskForm
from wtforms import validators
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
