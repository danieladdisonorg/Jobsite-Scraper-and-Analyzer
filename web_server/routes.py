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
from celery.result import AsyncResult

from main_celery.celery import celery_app
from db.models import ScrapingResultFileMetaData
from web_server.forms import ScrapingDataQueryFilter
from web_server.config import Config


diagrams = Blueprint("diagrams", __name__)
DATE_TIME_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"


def get_file_names_from_cache() -> None | list:
    """ Get scraping data file names from session if
        they are not expired
    """
    if "file_names" in session and "file_names_cache_time" in session:
        cache_time = session["file_names_cache_time"].replace(tzinfo=None)
        if (
                datetime.utcnow() - cache_time
                < Config.FILES_NAME_CHOICES_CACHE_TIME
        ):
            return session["file_names"]


def set_file_names_in_cache(file_names: list) -> None:
    """ Set scraping data file names since we are creating scraped data file
    every 'SCRAPING_EVERY_DAYS' there is not need to request file names for
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


@diagrams.route("/scraping/diagrams", methods=["GET", "POST"])
def get_diagrams():
    scraping_data_form = ScrapingDataQueryFilter(prefix="scrp_")
    scraping_data_form = set_query_form_file_names_choices(scraping_data_form)

    if request.method == "POST" and scraping_data_form.validate():
        # Save form data to session
        session["scrp_to_date"] = scraping_data_form.to_date.data
        session["scrp_from_date"] = scraping_data_form.from_date.data
        session["scrp_file_names"] = scraping_data_form.files_name.data

        scraping_metadata = select(ScrapingResultFileMetaData.file_path)
        queryset = diagrams_query_filtering(
            queryset=scraping_metadata,
            query_form=scraping_data_form
        )
        scraping_files_path = g.db.scalars(queryset).all()

        if scraping_files_path:
            diagrams_task_id = celery_app.send_task(
                "web_server.tasks.get_diagrams_img",
                args=[scraping_files_path]
            ).id

            return render_template(
                "query_filtering.html",
                scraping_data_form=scraping_data_form,
                scraping_files_path=scraping_files_path,
                diagrams_task_id=diagrams_task_id,
            )

    # Load session data for GET request
    scraping_data_form.to_date.data = (
        datetime.strptime(session.get("scrp_to_date"), DATE_TIME_FORMAT).date()
        if session.get("scrp_to_date") else None
    )
    scraping_data_form.from_date.data = (
        datetime.strptime(
            session.get("scrp_from_date"),
            DATE_TIME_FORMAT).date()

        if session.get("scrp_from_date") else None
    )
    scraping_data_form.files_name.data = session.get("scrp_file_names")

    return render_template(
        "query_filtering.html",
        scraping_data_form=scraping_data_form,
    )


@diagrams.get("/scraping/diagrams/<diagrams_task_id>")
def get_diagrams_result(diagrams_task_id: str):
    """
    Get diagrams from Celery, using process task 'diagrams_id' id.
    """
    scraping_data_form = ScrapingDataQueryFilter(prefix="scrp_")

    # set query form inputs with user values
    scraping_data_form.to_date.data = (
        datetime.strptime(session.get("scrp_to_date"), DATE_TIME_FORMAT).date()
        if session.get("scrp_to_date") else None
    )
    scraping_data_form.from_date.data = (
        datetime.strptime(
            session.get("scrp_from_date"),
            DATE_TIME_FORMAT).date()

        if session.get("scrp_from_date") else None
    )
    scraping_data_form = set_query_form_file_names_choices(scraping_data_form)

    if AsyncResult(diagrams_task_id).ready():
        result_diagrams = AsyncResult(diagrams_task_id).result

        return render_template(
            "diagrams.html",
            scraping_data_form=scraping_data_form,

            **result_diagrams
        )
    return render_template(
        "diagrams.html",
        scraping_data_form=scraping_data_form,
        diagrams_task_id=diagrams_task_id,
        diagram_error=(
            "Please wait before you can click again"
        )
    )
