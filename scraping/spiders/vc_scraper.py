"""
Vacancy scraper module
"""
from tqdm import tqdm
from typing import Any, Iterable

import scrapy
from scrapy.http.response.html import HtmlResponse
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest

import config
from scraping.items import VacancyItem, VacancySkills


# CSS selector path to element(s)
SKILLS = ".l1sjc53z::text"
CONTRACTS_SALARY = "p[data-test='text-contractName']::text"

# vacancy info like employment type, location, ua support
VC_INFO = ".c21kfgf div::text"

SVG_PATH = ".c21kfgf div svg"
ANCESTOR_TEXT = "ancestor::div[2]//text()"
LEVEL_OF_EXP = f"{SVG_PATH} path[d*='M21.8607']"
EMPLOYMENT_TYPE = f"{SVG_PATH} path[d*='M9.00003']"
LOCATION = f"{SVG_PATH} path[d*='M13 15L12']"
UA_SUPPORT = f"{SVG_PATH} path[d*='M27.5 12C27.5']"

REQUIREMENTS = "div[data-test='section-requirements']"
# requirements text first expected and optional
REQ_EXPECTED = "ul[data-test='section-requirements-expected'] li div::text"
REQ_OPTIONAL = "ul[data-test='section-requirements-optional'] li div::text"

# next pagination button
NEXT_PAGE = (
    "nav ul li a[data-test='anchor-nextPage']"
    "[data-disabled='false']::attr(href)"
)
LAST_PAGE_NUM = "nav ul li:nth-last-child(2) a::text"


class VacancyScraper(scrapy.Spider):
    name = "vacancies"
    start_urls = [config.JOB_URL]
    page_num = 1
    # last pagination button
    last_page_num = 0

    def start_requests(self) -> Iterable[SeleniumRequest]:
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse, **kwargs: Any) -> VacancyItem:
        # get vacancies
        for vc in tqdm(response.css(".o1onjy6t .a4pzt2q")):
            yield response.follow(vc, callback=self.parse_vc)

        self.page_num += 1

        # get last pagination number at the beginning
        # because later we would not be able to get it
        if not self.last_page_num:
            self.last_page_num = int(response.css(LAST_PAGE_NUM).get())

        # checking if we are not going over self.last_page_num
        if self.page_num < self.last_page_num:
            yield SeleniumRequest(
                url=response.urljoin(f"?pageNumber={self.page_num}"),
                callback=self.parse
            )

    def parse_vc(self, vc: HtmlResponse, **kwargs) -> VacancyItem:

        # get all containers with skill labels
        skills = vc.css(".c1fj2x2p")
        # Ensure the list has exactly 3 elements, filling with '[]' if fewer
        skills = (skills + [[]] * 3)[:3]
        required_skills, optional_skills, os = \
            [tools.css(SKILLS).getall() if tools else [] for tools in skills
             ]

        # get vacancy description
        requirements = vc.css(REQUIREMENTS)
        req_required = self.get_required_requirements(requirements)
        req_optional = self.get_optional_requirements(requirements)

        # Fallback to using 'requirements' if no 'REQ_EXPECTED'
        # found in html tags then we take whole text from vacancy
        # description If 'requirements' are not divided
        # as 'req_required' and 'req_optional'
        req_required = req_required if req_required else requirements.getall()

        # vacancy information
        return VacancyItem(
            **{
                "required_skills": self.description_skills(
                    req_required
                ).union(set(required_skills)),
                "optional_skills": self.description_skills(
                    req_optional
                ).union(set(optional_skills)),
                "os": os,
                "level_of_exp": vc.css(LEVEL_OF_EXP).xpath(
                    ANCESTOR_TEXT).get(),
                "employment_type": vc.css(EMPLOYMENT_TYPE).xpath(
                    ANCESTOR_TEXT).get(),
                "contracts": vc.css(CONTRACTS_SALARY).get(),
                "location": vc.css(LOCATION).xpath(ANCESTOR_TEXT).get(),
                "ua_support": vc.css(UA_SUPPORT).xpath(ANCESTOR_TEXT).get(),
            }
        )

    @staticmethod
    def description_skills(desc: list[str]) -> set[str]:
        """
        Getting additional skills out of description that may not be
        in 'REQ_EXPECTED', 'REQ_OPTIONAL' tags.
        """
        return VacancySkills(texts=desc).get_clean_skills()

    @staticmethod
    def get_required_requirements(requirements: Selector) -> list[str]:
        """Get description about required skills."""
        # TODO: look at the result of this function
        return requirements.css(REQ_EXPECTED).getall()

    @staticmethod
    def get_optional_requirements(requirements: Selector) -> list[str]:
        """Get description about optional skills."""
        return requirements.css(REQ_OPTIONAL).getall()
