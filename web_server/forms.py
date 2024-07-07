import enum
from datetime import date
from datetime import timedelta
from flask_wtf import FlaskForm
from wtforms import ValidationError, validators, Form
from wtforms.fields import (
    DateField,
    SelectMultipleField,
    SubmitField,
    Field
)

from web_server.config import Config
from common.db.models import DiagramTypes


class DiagramsQueryFilter(Form):
    to_date = DateField(
        validators=[validators.Optional()]
    )
    from_date = DateField(
        validators=[validators.Optional()],
    )
    diagrams_about = SelectMultipleField(
        choices=[(field.name, field.value) for field in DiagramTypes],
        validators=[validators.Optional()]
    )
    submit = SubmitField()

    def validate_to_date(self, form: FlaskForm, field: Field):
        if (
                int((self.from_date.data - self.to_date.data).days !=
                    Config.SCRAPING_EVERY_NUM_DAY)
        ):
            raise ValidationError(
                f"The from_date must be {Config.SCRAPING_EVERY_NUM_DAY} days before to_day"
            )
