"""Analyze data scraped from the.protocol job portal"""
import os
import dotenv
import pandas as pd
import matplotlib.pyplot as plt

from config import POSITION
from analyzing.utility import (
    removing_duplicates,
    get_result_diagram,
    from_column_to_data_frame,
    wedges_formatter
)

dotenv.load_dotenv()

# get directory path for saving results of scraping
scraped_data = os.path.join("..", os.getenv("SCRAPING_RESULT_DIR"))
# TODO: I can use Celery and Redis for processing intensive tasks


def count_required_skills(df: pd.DataFrame) -> dict:
    """Count the occurrence of each skill in 'required_skills' column"""

    # Make all required skills into one Series
    required_skills = pd.Series(df["required_skills"].explode().to_list())
    # required_skills = pd.Series(df.required_skills.sum())
    # optional_skills = pd.Series(df.optional_skills.dropna().sum())

    # Count the occurrences of each skill
    required_skills_counts = required_skills.value_counts()
    # optional_skills_counts = optional_skills.value_counts()

    # Remove duplicates, because we have scraped data not only
    # from set up labels on website but also we have processed text requirements
    required_skills_dict = removing_duplicates(required_skills_counts)
    # optional_skills_dict = removing_duplicates(optional_skills_counts)

    return required_skills_dict


def count_optional_skills(df: pd.DataFrame) -> dict:
    """Count the occurrence of each skill in 'required_skills' column"""

    # Make all optional skills into one Series
    optional_skills = pd.Series(df["optional_skills"].explode().to_list())

    # Count the occurrences of each skill
    optional_skills_counts = optional_skills.value_counts()

    # Remove duplicates, because we have scraped data not only
    # from set up labels on website but also we have processed text requirements
    # and update counts for optional and required skills
    optional_skills_dict = removing_duplicates(optional_skills_counts)

    return optional_skills_dict


def skills_from_dict_to_dataframe(
        skills: dict,
) -> pd.DataFrame:

    # Create DataFrames from dictionary
    skills_df = pd.DataFrame(
        {
            "skills": list(skills.keys()),
            "count": list(skills.values())
        }
    )

    # Sort DataFrame by count in descending order
    skills_df = skills_df.sort_values(by="count", ascending=False)

    return skills_df


def get_optional_skills(df: pd.DataFrame) -> pd.DataFrame:
    return skills_from_dict_to_dataframe(count_optional_skills(df=df))


def get_required_skills(df: pd.DataFrame) -> pd.DataFrame:
    return skills_from_dict_to_dataframe(count_required_skills(df=df))


def set_y_labels(data) -> None:
    """
    Dynamically changes the range of numbers on axis 'y'/
    :param data:
    :return:
    """
    max_count = data.max()
    # dynamically calculate the step which are going
    # to represent x labels
    step = (max_count // 10 + 1) * 10 // 5
    plt.yticks(range(0, max_count + step, step))


def skills_by_level_of_exp(df: pd.DataFrame) -> str:
    """Show required and optional skills base on level of experience"""

    level_of_exp = from_column_to_data_frame(df, "level_of_exp")
    df_exp = df.merge(level_of_exp, right_index=True, left_index=True)

    fig, axes = plt.subplots(len(level_of_exp.columns), 2, figsize=(20, len(level_of_exp.columns) * 5))

    for i, exp_level in enumerate(level_of_exp.columns):
        # filter 'df_exp' base on level of experience
        exp_level_df = df_exp[df_exp[exp_level] == 1]

        required_skills, optional_skills = (
            get_required_skills(exp_level_df), get_optional_skills(exp_level_df)
        )

        required_top_skills = required_skills.iloc[:30]
        optional_top_skills = optional_skills.iloc[:30]

        # get required and optional diagram
        re_axe = axes[i, 0]
        op_axe = axes[i, 1]

        # show top required skills base on exp_level
        re_axe.bar(required_top_skills["skills"], required_top_skills["count"])

        re_axe.set_title((
            f"TOP {len(required_top_skills)} Required Skills for {POSITION} Developer"
            f" with level of expirience: {exp_level}. Base on {exp_level_df.shape[0]} job descriptions"
        ))
        re_axe.set_xticks(range(len(required_top_skills["skills"])))
        re_axe.set_xticklabels(required_top_skills["skills"], rotation=45, ha="right")

        max_count = required_top_skills["count"].max()
        # dynamically calculate the step which are going
        # to represent y labels
        step = (max_count // 10 + 1) * 10 // 5
        re_axe.set_ylabel(range(0, max_count + step, step))
        re_axe.set_ylabel("Counts")

        re_axe.grid(True)

        # show top optional skills base on exp_level
        op_axe.bar(optional_top_skills["skills"], optional_top_skills["count"])

        op_axe.set_title((
            f"TOP {len(optional_top_skills)} Optional Skills for {POSITION} Developer"
            f" with level of expirience: {exp_level}. Base on {len(exp_level_df['optional_skills'].dropna())} job descriptions"
        ))
        op_axe.set_xticks(range(len(optional_top_skills["skills"])))
        op_axe.set_xticklabels(optional_top_skills["skills"], rotation=45, ha="right")
        op_axe.grid(True)

    diagram = get_result_diagram()
    plt.close()

    return diagram


def top_required_skills(df: pd.DataFrame) -> str:
    """Top 30 required skills"""

    required_skills = get_required_skills(df=df)
    top_skills = required_skills.iloc[:30, :]

    plt.figure(figsize=(15, 5))
    plt.bar(top_skills.skills, top_skills["count"])

    plt.title(
        f"TOP {top_skills.shape[0]} Required Skills for {POSITION} Developer (base on {required_skills.shape[0]} job descriptions)")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Counts")
    set_y_labels(top_skills["count"])
    plt.grid(True)

    diagram = get_result_diagram()
    plt.close()

    return diagram


def top_optional_skills(df: pd.DataFrame) -> str:
    """Top 30 optional skills"""

    optional_skills = get_optional_skills(df=df)
    top_skills = optional_skills.iloc[:30, :]

    plt.figure(figsize=(15, 5))
    plt.bar(top_skills.skills, top_skills["count"])

    plt.title(
        f"TOP {top_skills.shape[0]} Optional Skills for {POSITION} Developer (base on {optional_skills.shape[0]} job descriptions)")

    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Counts")
    set_y_labels(top_skills["count"])
    plt.grid(True)

    diagram = get_result_diagram()
    plt.close()

    return diagram


def bar_compare_column_values(df: pd.DataFrame, column: str) -> str:
    """ Using bar plot show comparison of column values """

    #  make column to data frame
    column_sum = from_column_to_data_frame(
        df=df, column=column
    ).sum().sort_values(ascending=False)

    plt.figure(figsize=(10, 5))
    plt.bar(column_sum.index, column_sum)
    plt.title(f"Comparing values in '{column}' column")

    set_y_labels(column_sum)
    plt.xticks(rotation=45, ha="right")
    plt.grid(True)

    diagram = get_result_diagram()
    plt.close()

    return diagram


def compare_ua_support_values(df: pd.DataFrame) -> str:
    """Show comparisons between values in column 'contracts'"""

    ua_support = df["ua_support"].value_counts().sort_values(ascending=False)

    plt.pie(
        ua_support,
        autopct=lambda v: wedges_formatter(v, ua_support),
        labels=("No UA Support", "UA Support"),
        textprops={"verticalalignment": "center"},
    )
    plt.title(f"How many job vacancies are open for ukraines. Base on {df.shape[0]} job descriptions")

    diagram = get_result_diagram()
    plt.close()

    return diagram


def get_top_locations(df: pd.DataFrame) -> str:
    """Get top 20 locations to work in Poland"""

    locations_values = df["location"].value_counts().sort_values(ascending=False)
    top_locations = locations_values.iloc[:10]

    fig, ax = plt.subplots(figsize=(15, 15))

    ax.pie(
        top_locations,
        autopct=lambda v: wedges_formatter(v, top_locations),
        labels=top_locations.index,
        textprops={"verticalalignment": "center"},
        pctdistance=0.9
    )
    ax.set_title(f"Location of job vacancies. Base on {df.shape[0]} job vacancies")

    diagram = get_result_diagram()
    plt.close()

    return diagram
