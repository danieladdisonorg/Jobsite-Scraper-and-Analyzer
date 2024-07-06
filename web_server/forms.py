import enum
from datetime import date
from datetime import timedelta
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import (
    DateField,
    SelectMultipleField,
    SubmitField,
    Field
)

from web_server.config import Config


class DiagramTypes(enum.Enum):
    employment_type = "Employment type"
    location = "Location"
    optional_skills = "Optional skills"
    required_skills = "Required skills"
    o_s = "OS"
    skills_by_level_of_exp = "Skills by level of experience"
    ua_support = "UA support"


class DiagramsQueryFilter(FlaskForm):
    to_date = DateField(default=date.today())
    from_date = DateField(
        default=date.today() - timedelta(days=Config.SCRAPING_EVERY_NUM_DAY)
    )
    diagrams_about = SelectMultipleField(
        choices=DiagramTypes,
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
