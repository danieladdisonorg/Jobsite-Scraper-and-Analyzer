"""
Vacancy scraper module
"""
from scrapy import Request
from tqdm import tqdm
from typing import Any

import scrapy
from scrapy.http.response.html import HtmlResponse
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

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


class VacancyScraper(scrapy.Spider):
    name = "vacancies"
    start_urls = [config.JOBS_URL]

    def parse(self, response: HtmlResponse, **kwargs: Any) -> VacancyItem:
        # get vacancies
        # yield from response.follow_all(
        #     css=".o1onjy6t .a4pzt2q", callback=self.parse_vc
        # )
        for vc in tqdm(response.css(".o1onjy6t .a4pzt2q")):
            # if not last_vc:
                # self.last_vc_url = last_vc = vc.attrib["href"]
            yield response.follow(vc, callback=self.parse_vc)

        # next page
        # yield from response.follow_all(
        #     css=".anchor-nextPage", callback=self.parse
        # )

    def parse_vc(self, vc: HtmlResponse, **kwargs) -> VacancyItem:

        # get all containers with skill labels
        skills = vc.css(".c1fj2x2p")
        # Ensure the list has exactly 3 elements, filling with '[]' if fewer
        skills = (skills + [[]] * 3)[:3]
        required_skills, optional_skills, os = [tools.css(SKILLS).getall() if tools else [] for tools in skills]

        # get vacancy description
        requirements = vc.css(REQUIREMENTS)
        req_required = self.get_required_requirements(requirements)
        req_optional = self.get_optional_requirements(requirements)

        # Fallback to using 'requirements' if no 'REQ_EXPECTED' found in html tags
        # then we take whole text from vacancy description if 'requirements' are not
        # divided as 'req_required' and 'req_optional'
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
                "level_of_exp": vc.css(LEVEL_OF_EXP).xpath(ANCESTOR_TEXT).get(),
                "employment_type": vc.css(EMPLOYMENT_TYPE).xpath(ANCESTOR_TEXT).get(),
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

    @property
    def last_vc_url(self) -> str:
        try:
            with open("last_vc_url.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    @last_vc_url.setter
    def last_vc_url(self, vc_url: str) -> None:
        with open("last_vc_id.txt", "w") as f:
            f.write(vc_url)
            self.logger.info(f"The vacancy url:{vc_url} we will stop next time")
#
#
# pr = CrawlerProcess(settings=get_project_settings())
# pr.crawl(VacancyScraper)
# pr.start()
