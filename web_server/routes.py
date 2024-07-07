from flask import (
    Blueprint,
    request,
    g
)
from sqlalchemy.orm import Query

from common.db.models import DiagramFileMetaData
from web_server.forms import DiagramsQueryFilter


diagrams = Blueprint("diagrams", __name__)


@diagrams.get("scraping/diagrams")
def get_diagrams():
    query_form = DiagramsQueryFilter(request.args)
    metadata_query: Query = g.db.query(DiagramFileMetaData)

    if query_form.validate():
        to_date = query_form.to_date.data
        from_date = query_form.from_date.data
        diagrams_about = query_form.diagrams_about.data

        if to_date:
            metadata_query = metadata_query.filter(
                DiagramFileMetaData.created_at <= to_date
            )

        if from_date:
            metadata_query = metadata_query.filter(
                DiagramFileMetaData.created_at >= from_date
            )

        if diagrams_about:
            pass
