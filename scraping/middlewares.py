# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os

from scrapy.http import Response, Request
from scrapy.http.response.html import HtmlResponse
from scrapy import signals
from scrapy.spiders import Spider
from scrapy.exceptions import CloseSpider
from scrapy_selenium4 import SeleniumMiddleware, SeleniumRequest
from selenium.webdriver.support.wait import WebDriverWait
from typing import Optional
from dotenv import load_dotenv

from config import JOB_URL

load_dotenv()


class DownloadSeleniumMiddleware(SeleniumMiddleware):
    """
    Fixing the problem of request being instance of
    Request even so initiator of request was
    scrapy_selenium4.SeleniumRequest class and thus
    old SeleniumMiddleware.process_request ignores request from
    Request and not setting all meta[] dependencies like 'driver'
    that I need.
    """
    def process_request(self, request: SeleniumRequest, spider):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, Request):
            return None

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    "name": cookie_name,
                    "value": cookie_value
                }
            )
        # Only SeleniumRequest has wait_until/screenshot/execute_script
        # attributes not Request
        if isinstance(request, SeleniumRequest):
            if request.wait_until:
                WebDriverWait(
                    self.driver, request.wait_time
                ).until(request.wait_until)

            if request.screenshot:
                request.meta["screenshot"] = (
                    self.driver.get_screenshot_as_png()
                )

            if request.script:
                self.driver.execute_script(request.script)

        body = str.encode(self.driver.page_source)

        # Expose the driver via the "meta" attribute
        request.meta.update({"driver": self.driver})

        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding="utf-8",
            request=request
        )


class CacheUrlMiddleware:
    def __init__(self):
        # TODO: make value of cache_file to a global configurations
        self.cache_file = os.getenv("CACHE_FILE_LAST_VACANCY")
        self.last_vacancy_url = self.read_last_vc_url()
        self.first_vacancy_url: Optional[str] = None

    def read_last_vc_url(self) -> str:
        try:
            with open(self.cache_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    def save_last_vc_url(self, vc_url: str) -> None:
        with open(self.cache_file, "w") as f:
            f.write(vc_url)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(
            middleware.spider_closed, signal=signals.spider_closed
        )
        return middleware

    def process_spider_input(
            self,
            response: Response,
            spider: Spider
    ) -> Optional[None]:
        # we do not want to cash response url which gets all vacancies
        if not self.first_vacancy_url and response.url != JOB_URL:
            # Remember the first vacancy URL
            self.first_vacancy_url = response.url

        if self.last_vacancy_url and response.url == self.last_vacancy_url:
            # Stop processing further requests if we
            # encounter the last vacancy URL
            raise CloseSpider(
                reason=f"Encountered last vacancy URL: {self.last_vacancy_url}"
            )

    def spider_closed(self, spider: Spider) -> None:
        if self.first_vacancy_url:
            self.save_last_vc_url(self.first_vacancy_url)
