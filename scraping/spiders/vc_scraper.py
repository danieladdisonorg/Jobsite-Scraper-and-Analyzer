"""
Vacancy scraper module
"""

from tqdm import tqdm  # maks loops show a smart progress meter
from typing import Any

import scrapy
from scrapy.http import Response

import config
from scraping.items import VacancyItem


# XPATH path to element(s)
DATE = ".//span[@class='mr-2 nobr']/@title"
NUM_VIEWS = ".//span[@class='nobr']/span[1]/@title"
NUM_APPLICATIONS = ".//span[@class='nobr']/span[2]/@title"
TOOLS = ".//span/@data-original-text"
YEAR_OF_EXP = ".//span[contains(text(), ' of experience')]/text()"
EMPLOYMENT_TYPE = (
    ".//span[contains(text(), 'Remote') "
    "or contains(text(), 'Office')]/text()"
)
COUNTRY = ".//span[@class='location-text']/text()"


class VacancyScraper(scrapy.Spider):
    name = "vacancies"
    start_urls = [config.JOBS_URL]

    def parse(self, response: Response, **kwargs: Any) -> VacancyItem:
        # get vacancies
        for vc in tqdm(response.xpath("//li[contains(@id, 'job-item-')]")):
            yield self.parse_vc(vc, **kwargs)

        # next page
        yield from response.follow_all(
            css=".pagination li:nth-last-child(1) a", callback=self.parse
        )

    def parse_vc(self, vc: Response, **kwargs) -> VacancyItem:
        return VacancyItem(
            **{
                "date_time": vc.xpath(DATE).get(),
                "num_views": vc.xpath(NUM_VIEWS).get(),
                "num_applications": vc.xpath(NUM_APPLICATIONS).get(),
                "tools": vc.xpath(TOOLS).get(),
                "year_of_exp": vc.xpath(YEAR_OF_EXP).get(default=0),
                "employment_type": vc.xpath(EMPLOYMENT_TYPE).get(),
                "country": vc.xpath(COUNTRY).get(),
            }
        )
