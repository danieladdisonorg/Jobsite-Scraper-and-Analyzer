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

nltk.download("stopwords")


class VacancySkills:
    """
    Class for getting skills from text, it's just looking
    for capitalizing words in the text, which is a common way.
    Plus going through filters like: removing stopwords/duplicates.
    I am not promising that it will return only skills.
    """

    def __init__(self, texts: list[str]) -> None:
        self.texts = texts

    @property
    def re_pattern(self) -> re.Pattern:
        # regex patterns supports Ukraine, English and Russia languages
        re_lang = "[A-Z][a-zżźćńółęąś]"
        # ignore capitalize words with 'not_start' char before them
        not_start = "[-.]"
        # compile the pattern for performance optimization
        return re.compile(
            (
                r"(?<!^)"  # ignore words at the beginning of a new line
                fr"(?<!{not_start})(?<!{not_start} )\b"  # - Competitive | .Competitive
                # matching pattern
                # capturing capitalize word
                f"(?:{re_lang}*)+"
                # consecutive capitalize words with
                # special characters between them, except (/,\)
                rf"(?:[^\w](?:{re_lang}*)+)*"
                # ignore words with ":" at the end ex. 'Skills:'
                f"\b(?!(?: (?:{re_lang}*)+)*:)"
            )
        )

    pattern = re_pattern

    def get_skills(self) -> set:
        """Return set with skills"""
        return set().union(*(self.filter_text(remove_tags(text)) for text in self.texts))

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

    def get_clean_skills(self) -> set[str]:
        """Applying all filters to get skills for POSITION"""
        return self.removing_stopwords(self.get_skills())


def removing_duplicates(skills: set[str]) -> list[str]:
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

    return list(unq_words)


def get_contracts(v: str) -> list[str]:
    """Get employment contracts for example B2B or employment contract"""
    # replace values in parentheses with space like
    #  kontrakt B2B (pełny etat) ->  kontrakt B2B
    contracts = re.sub(r"( \([^)]*\))", "", v)
    return contracts.split(", ")


def split_on_dot(v: str) -> list[str]:
    return v.split(" • ")


def contracts_to_english(contracts: list[str]) -> list[str]:
    """
    Convert 'contracts' polish values to english one.
    :param contracts:
    :return:
    """
    contacts_eng = {
        "umowa o pracę": "contract of employment",
        "umowa zlecenie": "contract of mandate",
        "umowa na zastępstwo": "replacement contract",
        "kontrakt B2B": "B2B contract",
        "umowa o pracę tymczasową": "temporary employment contract",
        "umowa o dzieło": "contract for specific work",
        "umowa o staż / praktyki": "internship / apprenticeship contract",
    }
    return [contacts_eng.get(contract, contract) for contract in contracts]


def employment_to_english(employments: list[str]) -> list[str]:
    """
    Convert 'employments' polish values to english one.
    :param employments:
    :return:
    """
    employments_eng = {
        "praca stacjonarna": "full office work",
        "część etatu": "part time",
        "praca hybrydowa": "hybrid work",
        "praca zdalna": "home office work",
        "praca mobilna": "mobile work",
    }
    return [
        employments_eng.get(employment, employment)
        for employment in employments
    ]


class VacancyItem(scrapy.Item):
    # define the fields for your item here like:
    required_skills = Field(serializer=lambda v: list(v) if v else None)
    optional_skills = Field(serializer=lambda v: list(v) if v else None)
    os = Field(serializer=lambda v: v if v else None)
    level_of_exp = Field(serializer=split_on_dot)
    employment_type = Field(
        serializer=lambda v: employment_to_english(
            split_on_dot(v)
        )
    )
    contracts = Field(
        serializer=lambda v: contracts_to_english(
            get_contracts(v)
        )
    )
    location = Field(
        serializer=lambda v: v.split(", ")[0]
    )
    ua_support = Field(serializer=lambda v: bool(v))
