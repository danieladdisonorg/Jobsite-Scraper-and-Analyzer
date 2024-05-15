"""
Vacancy scraper module
"""

from tqdm import tqdm  # maks loops show a smart progress meter
from typing import Any

import scrapy
from scrapy.http import Response
from scrapy.crawler import CrawlerProcess

import config
from scraping.items import VacancyItem


# XPATH path to element(s)
DATE = ".//span[@class='mr-2 nobr']/@title"
NUM_VIEWS = ".//span[@class='nobr']/span[1]/@title"
NUM_APPLICATIONS = ".//span[@class='nobr']/span[2]/@title"
SKILLS = ".//div[contains(@class, 'original-text')]"
YEAR_OF_EXP = ".//span[contains(text(), ' of experience')]/text()"
EMPLOYMENT_TYPE = (
    ".//span[contains(text(), 'Remote') "
    "or contains(text(), 'Office')]/text()"
)
COUNTRY = ".//span[@class='location-text']/text()"


class VacancyScraper(scrapy.Spider):
    name = "vacancies"
    start_urls = [config.JOBS_URL]
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    last_vc_file = "last_vc_id.txt"
    page = 1

    def start_requests(self):
        # Custom headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> VacancyItem:
        # get last vacancy we started
        last_vc_id = self.last_vc_id

        # get vacancies
        for vc in tqdm(response.xpath("//li[contains(@id, 'job-item-')]")):
            vc_id = vc.attrib["id"].split("job-item-")[1]

            # stop scraping when encounter last vacancy
            if last_vc_id == vc_id:
                self.logger.info(f"Encounter same vacancy")
                return
            # save vacancy id for next run
            if not last_vc_id:
                last_vc_id = vc_id
                self.save_last_vc_id(last_vc_id)

            yield self.parse_vc(vc, **kwargs)

        # next page
        print(response.headers)
        last_page = response.xpath("//ul[contains(@class, 'pagination')]/li/a/text()").getall()[-3].strip()
        print(last_page)
        self.page += 1
        if not self.page > int(last_page):
            query = f"?keyword={config.POSITION}&page={self.page}"
            print(response.urljoin(query))
            yield response.follow(query, callback=self.parse)

        # yield from response.follow_all(
        #     css=".pagination li:nth-last-child(1) a", callback=self.parse
        # )

    def parse_vc(self, vc: Response, **kwargs) -> VacancyItem:
        return VacancyItem(
            **{
                "date_time": vc.xpath(DATE).get(),
                "num_views": vc.xpath(NUM_VIEWS).get(),
                "num_applications": vc.xpath(NUM_APPLICATIONS).get(),
                "skills": vc.xpath(SKILLS).get(),
                "year_of_exp": vc.xpath(YEAR_OF_EXP).get(default=0),
                "employment_type": vc.xpath(EMPLOYMENT_TYPE).get(),
                "country": vc.xpath(COUNTRY).get(),
            }
        )

    @property
    def last_vc_id(self) -> str:
        try:
            with open("last_vc_id.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    def save_last_vc_id(self, vc_id: str) -> None:
        with open("last_vc_id.txt", "w") as f:
            f.write(vc_id)
            self.logger.info(f"The vacancy ID:{vc_id} we will stop next time")

#
# pr = CrawlerProcess()
# pr.crawl(VacancyScraper)
# pr.start()
