# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time
import os

from scrapy.http import Response
from scrapy import signals
from scrapy.spiders import Spider
from scrapy.exceptions import CloseSpider
from typing import Optional
from dotenv import load_dotenv

from config import JOB_URL

load_dotenv()


class ScrapingSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapingDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


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
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def process_spider_input(self, response: Response, spider: Spider) -> Optional[None]:
        # we do not want to cash response url which gets all vacancies
        if not self.first_vacancy_url and response.url != JOB_URL:
            # Remember the first vacancy URL
            self.first_vacancy_url = response.url

        if self.last_vacancy_url and response.url == self.last_vacancy_url:
            # Stop processing further requests if we encounter the last vacancy URL
            raise CloseSpider(
                reason=f"Encountered last vacancy URL: {self.last_vacancy_url}"
            )

    def spider_closed(self, spider: Spider) -> None:
        if self.first_vacancy_url:
            self.save_last_vc_url(self.first_vacancy_url)
