import io
import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from base64 import b64encode
from ast import literal_eval

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Matplotlib backend to Agg which is a non-interactive backend
# suitable for script and web application usage.
matplotlib.use("Agg")


def read_data_file(file_path: str) -> pd.DataFrame:
    df = pd.read_feather(file_path)
    return df


def concatenated_df(file_paths: list[str]) -> pd.DataFrame:
    """Concatenated multiple files of data into one DataFrame"""
    if file_paths:
        dfs = [
            read_data_file(file_path)
            for file_path in file_paths
            if os.path.isfile(file_path)
        ]
        # print(dfs, len(dfs))
        new_df = pd.concat(dfs, ignore_index=True)

        return new_df


def from_column_to_data_frame(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Making 'column' independent Data Frame"""
    # Make each values in 'df' column.
    # This approach is aligned with database normalization principles
    # which aim to reduce redundancy and improve data integrity.
    if column not in df.columns:
        raise ValueError(f"There is not column: {column}")

    explode_column = getattr(df, column).explode()
    # remove that column from original Data Frame object
    # df.drop(column, inplace=True, axis=1)
    return pd.crosstab(explode_column.index, explode_column)


def get_result_diagram() -> str:
    """
    Instead saving diagram to computer memory, we are going to save diagram in
    io.BytesIO object, and to be able to view it on HTML page we are encoding
    diagram BytesIO object to base64.b64encode and decoding to 'utf-8' text format
    as standard for all web application.
    :param diagram:
    :return:
    """
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    return b64encode(buf.read()).decode("utf-8")


def removing_duplicates(tool_counts) -> dict:
    """
    Removing duplicates, exp 'AI', 'AI services' - is same,
    'AI' should stay, and 'AI services' count value should be
    added to 'AI' count
    """
    unq_words = {}
    duplicates = set()

    # Sort tool_counts by length of keys (tool names)
    tool_counts_sorted = tool_counts.sort_index(key=lambda v: v.str.len())

    for tool, count in tool_counts_sorted.items():
        if tool not in duplicates:
            matches = process.extractBests(
                tool,
                tool_counts_sorted.index,
                scorer=lambda str1, str2: fuzz.ratio(str1.lower(), str2.lower()),
                score_cutoff=70
            )

            # Filter out matches that are similar to the current tool
            filtered_matches = {match for match, score in matches if match != tool and (
                    match.lower().startswith(tool.lower()) or score >= 85
            )}

            # Add count of similar tools to the current tool
            unq_words[tool] = count + sum(tool_counts[match] for match in filtered_matches)
            duplicates |= filtered_matches

    return unq_words


def wedges_formatter(pct, allvals):
    """Format Pie plot wedges label style"""
    absolute = int(pct / 100. * np.sum(allvals))
    return f"{pct:.1f}% ({absolute:d})"
