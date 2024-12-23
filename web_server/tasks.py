from celery import shared_task

from analyzing.analyze_the_prt import (
    skills_by_level_of_exp,
    top_required_skills,
    top_optional_skills,
    bar_compare_column_values,
    compare_ua_support_values,
    get_top_locations
)
from analyzing.utility import concatenated_df


@shared_task(queue="web_server_queue")
def get_diagrams_img(file_paths: list[str]) -> dict:
    """Concatenating files with data to one DataFrame and
        analyzing/visualizing.
    """
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
