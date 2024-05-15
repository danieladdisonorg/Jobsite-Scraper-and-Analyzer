# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import nltk
from nltk.corpus import stopwords

import scrapy
from scrapy import Field
from w3lib.html import remove_tags

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from config import POSITION


nltk.download("stopwords")


class VacancySkills:
    """
    Class for getting skills from text, it's just looking
    for capitalizing words in the text, which is a common way.
    Plus going through filters like: removing stopwords/duplicates.
    I am not promising that it will return only skills.
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

    def get_skills(self) -> set:
        """
        There are a lot of redundant info in description like
        information about the project/company etc. We need to aim where
        skills/requirements are specified.
        """
        texts = [
            remove_tags(text)
            for text in self.text.split("\xa0")
            if text and POSITION.lower() in text.lower()
        ]
        result = set().union(*(self.filter_text(text) for text in texts))
        return result

    def filter_text(self, text: str) -> set[str]:
        """Aims for getting skills from text, by finding capitalize words"""
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
    def removing_duplicates(skills: set[str]) -> set[str]:
        """
        Removing duplicates, exp 'AI', 'AI services' - is same,
         'AI' should stay
        """
        unq_words = set()
        duplicates = set()

        for skill in sorted(list(skills), key=len):
            # Normalize "Python"
            if "python" in skill.lower():
                unq_words.add("Python")

            elif skill not in duplicates:
                matches = process.extractBests(
                    skill, skills, scorer=fuzz.ratio, score_cutoff=70
                )

                # Filter out matches that are similar to the current skill
                # REST and RESTful is same, REST should stay
                filtered_matches = {
                    match for match, score in matches
                    if match != skill and (
                        match.lower().startswith(skill.lower())
                        or score >= 90
                    )
                }

                # Add the current skill and its filtered matches to unique words
                unq_words.add(skill)
                unq_words -= filtered_matches

                # Update the set of duplicates
                duplicates |= filtered_matches

        return unq_words

    def get_clean_skills(self) -> list[str]:
        """Applying all filters to get skills for POSITION"""
        skills = self.get_skills()
        return list(self.removing_duplicates(self.removing_stopwords(skills)))


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
    skills = Field(serializer=lambda v: VacancySkills(v).get_clean_skills())
    year_of_exp = Field(serializer=first_integer)
    employment_type = Field(serializer=employment_type)
    country = Field(
        serializer=lambda v: v.strip().replace("\n   ", "").split(", ")
    )
