from datetime import datetime
from flask import (
    Blueprint,
    request,
    g,
    render_template,
    session
)
from sqlalchemy.orm import Query
from sqlalchemy import select

from common.db.models import ScrapingResultFileMetaData
from web_server.forms import ScrapingDataQueryFilter

from analyzing.utility import concatenated_df
from analyzing.analyze_the_prt import (
    skills_by_level_of_exp,
    top_required_skills,
    top_optional_skills,
    bar_compare_column_values,
    compare_ua_support_values,
    get_top_locations
)
from web_server.config import Config


diagrams = Blueprint("diagrams", __name__)


def get_file_names_from_cache() -> None | list:
    """ Get scraping data file names from session """
    if "file_names" in session and "file_names_cache_time":
        cache_time = session["file_names_cache_time"].replace(tzinfo=None)
        if (
                datetime.utcnow() - cache_time
                < Config.FILES_NAME_CHOICES_CACHE_TIME
        ):
            return session["file_names"]


def set_file_names_in_cache(file_names: list) -> None:
    """ Set scraping data file names since we are creating scraped data file
    every 'SCRAPING_EVERY_NUM_DAY' there is not need to request file names for
    request
    """
    session["file_names"] = file_names
    session["file_names_cache_time"] = datetime.utcnow()


def set_query_form_file_names_choices(
        query_form: ScrapingDataQueryFilter
) -> ScrapingDataQueryFilter:
    file_names = get_file_names_from_cache()
    if file_names is None:
        # get file names from DB and cache it
        file_names = g.db.scalars(
            select(ScrapingResultFileMetaData.file_name)
        ).all()
        set_file_names_in_cache(file_names)

    query_form.files_name.choices = file_names

    return query_form


def get_diagrams_img(file_paths: list[str]) -> dict:
    df = concatenated_df(file_paths)
    return {
        "skills_by_level_of_exp_diagram": skills_by_level_of_exp(df),
        "required_skills_diagram": top_required_skills(df),
        "optional_skills_diagram": top_optional_skills(df),
        "level_of_exp_diagram": bar_compare_column_values(
            df, column="level_of_exp"
        ),
        "employment_type_diagram": bar_compare_column_values(
            df, column="employment_type"
        ),
        "contracts_diagram": bar_compare_column_values(df, column="contracts"),
        "us_support_diagram": compare_ua_support_values(df),
        "locations_diagram": get_top_locations(df),
    }


def diagrams_query_filtering(
        queryset, query_form: ScrapingDataQueryFilter
) -> Query:
    if query_form.validate():
        session["scrp_to_date"] = to_date = query_form.to_date.data
        session["scrp_from_date"] = from_date = query_form.from_date.data
        session["scrp_file_names"] = file_names = query_form.files_name.data

        if to_date:
            queryset = queryset.filter(
                ScrapingResultFileMetaData.created_at <= to_date
            )

        if from_date:
            queryset = queryset.filter(
                ScrapingResultFileMetaData.created_at >= from_date
            )

        if file_names:
            queryset = queryset.filter(
                ScrapingResultFileMetaData.file_name.in_(file_names)
            )

    return queryset


@diagrams.get("/scraping/diagrams")
def get_diagrams():
    scraping_data_form = ScrapingDataQueryFilter(
        request.args, prefix="scraping_"
    )
    # set choices for field 'file_names'
    scraping_data_form = set_query_form_file_names_choices(scraping_data_form)
    scraping_metadata = select(ScrapingResultFileMetaData.file_path)

    # query filtering
    queryset = diagrams_query_filtering(
            queryset=scraping_metadata,
            query_form=scraping_data_form
    )

    # set query form inputs with user values
    scraping_data_form.to_date.data = session.get("scrp_to_date", None)
    scraping_data_form.from_date.data = session.get("scrp_from_date", None)
    scraping_data_form.files_name.data = session.get("scrp_file_names", None)

    # get file paths to scraped data
    scraping_files_path = g.db.scalars(queryset).all()

    # start analyzing data and return dict with diagrams
    diagrams_img = (
        get_diagrams_img(scraping_files_path)
        if scraping_files_path
        else {}
    )

    return render_template(
        "diagrams.html",
        # diagram_form=diagram_form,
        scraping_data_form=scraping_data_form,
        scraping_files_path=scraping_files_path,
        **diagrams_img
    )
