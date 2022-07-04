import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
import re
import PyPDF2
import io
import os
from pdfminer.high_level import extract_text

#################################
# Remove
import logging

#################################
# TEXTRACT_EXTENSIONS = [".pdf", ""]
TEXTRACT_EXTENSIONS = ["", "html"]


class CustomLinkExtractor(LinkExtractor):
    def __init__(self, *args, **kwargs):
        super(CustomLinkExtractor, self).__init__(*args, **kwargs)
        # Keep the default values in "deny_extensions" *except* for those types we want.
        self.deny_extensions = [
            ext for ext in self.deny_extensions if ext not in TEXTRACT_EXTENSIONS
        ]


x = CustomLinkExtractor()
# print(x.deny_extensions)


# class MySpider(CrawlSpider):
class MySpider(scrapy.Spider):
    name = "Mr.Spider"
    allowed_domains = ["papers.nips.cc"]
    start_urls = ["https://papers.nips.cc/paper/"]
    logging.getLogger("scrapy").propagate = False
    logging.getLogger("scrapy").setLevel(logging.CRITICAL)

    rules = (
        # Rule(CustomLinkExtractor(), follow=True, callback="parse"),
        Rule(
            LinkExtractor(allow=(), deny=("\.zip", "\.pdf")),
            callback="parse",
            follow=True,
        ),
        # Rule(LinkExtractor(allow=("\.pdf")), callback="parse_pdf", follow=True),
    )

    def __init__(self):
        super().__init__()
        self.depth_limit = 3
        self.base_url = "https://papers.nips.cc/paper/"
        self.folder = "NeuIPS"
        self.lower_year = 2019
        self.upper_year = 2500
        self.disallowed = ["zip", "pdf", "son", "bib"]

    def get_year(self, url):
        reg = re.search("\D((19|20)\d{2})\D", url)
        if reg:
            return reg.group(1)

    def parse(self, response):
        print("\tRESPONSE = ", response.url)
        # if the depth has been hit
        if response.meta["depth"] > self.depth_limit:
            return

        temp_year = self.get_year(response.url)
        if response.url.endswith("Abstract.html"):
            for sublink in response.xpath(
                "//a[contains(text(),'Paper')]/@href"
            ).extract():
                if self.eval_year(response.url) == "valid" and response.url.endswith(
                    ".pdf"
                ):
                    sublink = self.base_url + sublink[7:]
                    yield Request(sublink, callback=self.parse_pdf)
        for sublink in response.xpath("//a/@href").extract():
            if (
                self.eval_year(sublink) in ["valid", "none"]
                and sublink[-3:] not in self.disallowed
            ):
                print("SUBLINK", sublink)
                yield response.follow(sublink, callback=self.parse)

        # if response.url.endswith("Abstract.html"):
        #    for sublink in response.xpath(
        #        "//a[contains(text(),'Paper')]/@href"
        #    ).extract():
        #        if temp_year:

        #            if (
        #                int(temp_year) >= self.lower_year
        #                and int(temp_year) <= self.upper_year
        #                and response.url.endswith(".pdf")
        #            ):
        #                sublink = self.base_url + sublink[7:]
        #                yield Request(sublink, callback=self.parse_pdf)

        # if temp_year:
        #    if int(temp_year) >= self.lower_year and int(temp_year) <= self.upper_year:
        #        for sublink in response.xpath("//a").extract():
        #            sublink_year = self.get_year(sublink)
        #            print("SUBLINK YEAR = ", sublink_year)
        #            yield response.follow(sublink, callback=self.parse)
        # else:
        #    for sublink in response.xpath("//a/@href").extract():
        #        sublink_year = self.get_year(sublink)
        #        print("SUBLINK YEAR = ", sublink_year)
        #        if sublink_year:
        #            if (
        #                int(sublink_year) >= self.lower_year
        #                and int(sublink_year) <= self.upper_year
        #            ):
        #                yield response.follow(sublink, callback=self.parse)

    def eval_year(self, link):
        year = self.get_year(link)
        if year:
            if int(year) >= self.lower_year and int(year) <= self.upper_year:
                return "valid"
            else:
                return "invalid"
        return "none"

    def parse_pdf(self, response):
        reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
        text = u""
        title = self.get_title(reader, response)
        print("TITLE - ", title)

    def handle_pdf(self, response, year):
        print("HANDLING ", response.url)
        reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
        text = u""
        title = self.get_title(reader, response)

    def get_title(self, reader, response):
        temp_title = reader.getDocumentInfo().title
        if temp_title:
            return temp_title
        else:
            body = extract_text(io.BytesIO(response.body))
            # with open("body_temp.pdf", "w+") as f:
            #    f.write(body)


if __name__ == "__main__":
    spdr = MySpider
    process = CrawlerProcess()
    process.crawl(spdr)
    process.start()
