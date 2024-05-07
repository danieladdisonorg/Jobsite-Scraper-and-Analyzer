# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import nltk
from nltk.corpus import stopwords

import scrapy
from scrapy import Field

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from config import POSITION


nltk.download("stopwords")


class VacancyTools:
    """
    Class for getting toolkits from text, it's just looking
    for capitalizing words in the text, which is a common way.
    Plus going through filters like: removing stopwords/duplicates.
    I am not promising that it will return only toolkits.
    """

    # compile the pattern for performance optimization
    pattern = re.compile(
        (
            r"(?<!^)"  # ignore words at the beginning of a new line
            r"(?<![^\x00-\x7F])"  # '•Design'
            r"(?<![-.*+)>:])(?<![-.*+)>:] )"  # - Competitive | .Competitive
            r"(?<![^\x00-\x7F] )\b"  # '• Design' with space
            # matching pattern
            # capturing capitalize word
            r"(?:[A-Z][a-z]*)+"
            # consecutive capitalize words with
            # special characters between them, except (/,\)
            r"(?:[^\w\\\/](?:[A-Z][a-z]*)+)*"
            # ignore words with ":" at the end ex. 'Skills:'
            r"\b(?!(?: (?:[A-Z][a-z]*)+)*:)"
        )
    )

    def __init__(self, text: str) -> None:
        self.text = text

    def get_tools(self) -> set:
        """
        There are a lot of redundant info in description like
        information about the project/company etc. We need to aim where
        skills/requirements are specified.
        """
        texts = [
            text.replace("<br>", ". ")
            for text in self.text.split("<br><br>")
            if POSITION.lower() in text.lower()
        ]
        result = set().union(*(self.filter_text(text) for text in texts))
        return result

    def filter_text(self, text: str) -> set[str]:
        """Aims for getting tools from text, by finding capitalize words"""
        # we do not want to match this words
        return set(self.pattern.findall(text))

    @staticmethod
    def removing_stopwords(words: set[str]) -> set[str]:
        """Removing stopwords, using NLTK stopwords"""
        result = {
            word for word in words
            if word.lower() not in set(stopwords.words())
        }
        return result

    @staticmethod
    def removing_duplicates(tools: set[str]) -> set[str]:
        """
        Removing duplicates, exp 'AI', 'AI services' - is same,
         'AI' should stay
        """
        unq_words = set()
        duplicates = set()

        for tool in sorted(list(tools), key=len):
            # Normalize "Python" tools
            if "python" in tool.lower():
                unq_words.add("Python")

            elif tool not in duplicates:
                matches = process.extractBests(
                    tool, tools, scorer=fuzz.ratio, score_cutoff=70
                )

                # Filter out matches that are similar to the current tool
                # REST and RESTful is same, REST should stay
                filtered_matches = {
                    match for match, score in matches
                    if match != tool and (
                        match.lower().startswith(tool.lower())
                        or score >= 90
                    )
                }

                # Add the current tool and its filtered matches to unique words
                unq_words.add(tool)
                unq_words -= filtered_matches

                # Update the set of duplicates
                duplicates |= filtered_matches

        return unq_words

    def get_clean_tools(self) -> list[str]:
        """Applying all filters to get tools for POSITION"""
        tools = self.get_tools()
        return list(self.removing_duplicates(self.removing_stopwords(tools)))


def first_integer(value: str) -> int:
    return int(value.split()[0])


def employment_type(value: str) -> list[str]:
    """
    Replace 'Full Remote' ot 'Remote' and
    'Hybrid Remote' to 'Hybrid', 'Office Work' to 'Office'
    and to be left with three type 'Office' 'Remote' 'Hybrid'
    """
    value = value.replace("Full ", "")
    value = value.replace(" Work", "")
    value = value.replace("Hybrid Remote", "Hybrid")
    return value.split(" or ")


class VacancyItem(scrapy.Item):
    # define the fields for your item here like:
    date_time = Field()
    num_views = Field(serializer=first_integer)
    num_applications = Field(serializer=first_integer)
    tools = Field(serializer=lambda v: VacancyTools(v).get_clean_tools())
    year_of_exp = Field(serializer=first_integer)
    employment_type = Field(serializer=employment_type)
    country = Field(
        serializer=lambda v: v.strip().replace("\n   ", "").split(", ")
    )
