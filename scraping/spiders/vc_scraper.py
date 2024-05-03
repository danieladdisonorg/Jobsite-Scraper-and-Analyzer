"""
Vacancy scraper module
"""
from tqdm import tqdm  # maks loops show a smart progress meter
from typing import Any

import scrapy
from scrapy.http import Response

import config
from scraping.items import VacancyItem


class VacancyScraper(scrapy.Spider):
    name = "vacancies"
    start_urls = [config.JOBS_URL]

    def parse(self, response: Response, **kwargs: Any) -> VacancyItem:
        # get vacancies
        for vc in tqdm(response.xpath("//li[contains(@id, 'job-item-')]")):
            yield self.parse_vc(vc, **kwargs)

        # next page
        yield from response.follow_all(
            css=".pagination li:nth-last-child(1) a",
            callback=self.parse
        )

    def parse_vc(self, vc: Response, **kwargs) -> VacancyItem:
        return VacancyItem(**{
            "date": vc.xpath(".//span[@class='mr-2 nobr']/@title").get(),
            "num_views": vc.xpath(".//span[@class='nobr']/span[1]/@title").get(),
            "num_applications": vc.xpath(".//span[@class='nobr']/span[2]/@title").get(),
            "tools": vc.xpath(".//span/@data-original-text").get(),
            "year_of_exp": vc.xpath(
                ".//span[contains(text(), ' of experience')]/text()"
            ).get(default=0),
            "employment_type": vc.xpath(
                ".//span[contains(text(), 'Remote')"
                " or contains(text(), 'Office')]/text()").get(),
            "country": vc.xpath(".//span[@class='location-text']/text()").get()
        })
