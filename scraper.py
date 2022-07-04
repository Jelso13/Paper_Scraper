import sys
import argparse
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import PyPDF2
import io
import re
import os
import logging
from pdfminer.high_level import extract_text

logging.propagate = False
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("pdfminer").setLevel(logging.CRITICAL)
pdflogs = [
    logging.getLogger(name)
    for name in logging.root.manager.loggerDict
    if name.startswith("pdfminer")
]
for ll in pdflogs:
    ll.setLevel(logging.WARNING)


class ContentFilter(logging.Filter):
    def filter(self, record):
        match = re.search(r"\d{3}", record.message)
        if match:
            return False


class General_Spider(scrapy.Spider):
    name = "Mr.Spider"
    allowed_domains = ["papers.nips.cc"]
    start_urls = ["https://papers.nips.cc/paper/"]
    logging.getLogger("scrapy").propagate = False
    logging.getLogger("scrapy").setLevel(logging.CRITICAL)
    rules = (
        Rule(
            LinkExtractor(allow=("\.htm")),
            callback="parse",
            follow=True,
        ),
        Rule(LinkExtractor(allow=("\.pdf")), callback="parse_pdf", follow=True),
    )

    def __init__(
        self,
        url_list,
        phrase_list,
        page_check=2,
        year_lower=2010,
        year_upper=2100,
        depth_limit=3,
    ):
        super().__init__()
        # self.start_urls = url_list
        self.start_urls = ["https://papers.nips.cc/paper/"]
        self.key_phrases = phrase_list
        self.page_check = page_check
        self.year_lower = year_lower
        self.year_upper = year_upper
        self.depth_limit = depth_limit

    def get_year(self, url):
        reg = re.search("\D((19|20)\d{2})\D", url)
        if reg:
            return reg.group(1)

    def parse(self, response):
        if response.meta["depth"] <= self.depth_limit:
            url = response.url
            year = self.get_year(url)
            # //div//a/@href gets the link for an href in an <a> tag
            page_type = list(filter(None, url.split("/")))
            # make sure the page is not a zip file or something weird
            if "." in page_type:
                if not page_type[-1].split(".")[-1] == "pdf":
                    return
            for sub_link in response.xpath("//div//a/@href").extract():
                # if the year in the url of the actual paper is different then set year to that
                if sub_link.endswith(".pdf"):
                    if self.get_year(sub_link) != year and isinstance(
                        self.get_year(sub_link), str
                    ):
                        year = self.get_year(sub_link)

                    if int(year) >= int(self.year_lower) and int(year) <= int(
                        self.year_upper
                    ):
                        callback_args = {
                            "page_check": self.page_check,
                            "year": year,
                        }
                        yield response.follow(
                            sub_link, callback=self.parse_pdf, cb_kwargs=callback_args
                        )
                elif year and isinstance(year, str):
                    if int(year) >= int(self.year_lower) and int(year) <= int(
                        self.year_upper
                    ):
                        yield response.follow(sub_link, callback=self.parse)
                else:
                    yield response.follow(sub_link, callback=self.parse)

    def parse_pdf(self, response, page_check, year):
        if response.meta["depth"] <= self.depth_limit:
            # used to check if the pdf contains one of the key_phrases
            # IDEA: Maybe use pdfminer instead?
            reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
            text = u""
            # if reader.getDocumentInfo().title:
            #    text += reader.getDocumentInfo().title
            #    for page in reader.pages:
            #        text += page.extractText()
            if reader.getDocumentInfo().title:
                text = reader.getDocumentInfo().title + extract_text(
                    io.BytesIO(response.body)
                )
            else:
                doc_body = extract_text(io.BytesIO(response.body))
                text = doc_body
                self.logger.info("doc_body type = " + str(type(doc_body)))
                # lines = doc_body.strip().split("\n")
                # top_i = 0
                # for i, line in enumerate(lines):
                #    if not len(line.strip()) == 0 and not re.search(
                #        r"technical\s+report|proceedings|preprint|to\s+appear|submission",
                #        line.lower(),
                #    ):
                #        top_i = i
                #        break
                # top_j = 0
                # for j, line in enumerate(lines[start + 1:start + max_lines + 1], start + 1):
                #    if not len(line.strip()) == 0:
                #        top_j = j
                #        break

            # determine if the pdf contains the key phrase
            phrase_found = False
            for phrase in self.key_phrases:
                if re.search(phrase, text, re.IGNORECASE):
                    phrase_found = True
                    break

            if phrase_found:
                self.logger.info("################################################")
                self.logger.info("################################################")
                self.logger.info("################################################")
                path = response.url.split("/")[-1]
                directory = "papers/" + str(year) + "/"
                if not os.path.exists(os.path.dirname(directory)):
                    try:
                        os.makedirs(os.path.dirname(directory))
                    except OSError as e:
                        self.logger.info(
                            "some thing I dont understand about a race condition?"
                        )
                directory += "/"
                self.logger.info("Doc Title = " + reader.getDocumentInfo().title)
                # ERROR: Some documents dont have title - particularly 2020
                if reader.getDocumentInfo().title:
                    self.logger.info("RESPONSE.BODY = " + str(type(response.body)))
                    with open(
                        directory + reader.getDocumentInfo().title + ".pdf", "w+"
                    ) as f:
                        f.write(response.body.decode("utf-8"))

            return text


class NIPS_Spider(scrapy.Spider):
    name = "NIPS Spider"
    allowed_domains = ["papers.nips.cc"]
    start_urls = ["https://papers.nips.cc/paper/"]
    logging.getLogger("scrapy").propagate = False
    logging.getLogger("scrapy").setLevel(logging.CRITICAL)
    rules = (
        Rule(
            LinkExtractor(allow=("\.htm")),
            callback="parse",
            follow=True,
        ),
        Rule(LinkExtractor(allow=("\.pdf")), callback="parse_pdf", follow=True),
    )

    def __init__(
        self,
        url_list,
        phrase_list,
        page_check=2,
        year_lower=2010,
        year_upper=2100,
        depth_limit=4,
    ):
        super().__init__()
        # self.start_urls = url_list
        self.start_urls = ["https://papers.nips.cc/paper/"]
        self.key_phrases = phrase_list
        self.page_check = page_check
        self.year_lower = year_lower
        self.year_upper = year_upper
        self.depth_limit = depth_limit

    def get_year(self, url):
        reg = re.search("\D((19|20)\d{2})\D", url)
        if reg:
            return reg.group(1)

    def parse(self, response):
        if response.meta["depth"] <= self.depth_limit:
            url = response.url
            year = self.get_year(url)
            # //div//a/@href gets the link for an href in an <a> tag
            page_type = list(filter(None, url.split("/")))
            # make sure the page is not a zip file or something weird
            if "." in page_type:
                if not page_type[-1].split(".")[-1] == "pdf":
                    return
            for sub_link in response.xpath("//div//a/@href").extract():
                # if the year in the url of the actual paper is different then set year to that
                if sub_link.endswith(".pdf"):
                    if self.get_year(sub_link) != year and isinstance(
                        self.get_year(sub_link), str
                    ):
                        year = self.get_year(sub_link)

                    if int(year) >= int(self.year_lower) and int(year) <= int(
                        self.year_upper
                    ):
                        callback_args = {
                            "page_check": self.page_check,
                            "year": year,
                        }
                        yield response.follow(
                            sub_link, callback=self.parse_pdf, cb_kwargs=callback_args
                        )
                elif year and isinstance(year, str):
                    if int(year) >= int(self.year_lower) and int(year) <= int(
                        self.year_upper
                    ):
                        yield response.follow(sub_link, callback=self.parse)
                else:
                    yield response.follow(sub_link, callback=self.parse)

    def parse_pdf(self, response, page_check, year):
        if response.meta["depth"] <= self.depth_limit:
            # used to check if the pdf contains one of the key_phrases
            # IDEA: Maybe use pdfminer instead?
            reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
            text = u""
            # if reader.getDocumentInfo().title:
            #    text += reader.getDocumentInfo().title
            #    for page in reader.pages:
            #        text += page.extractText()
            if reader.getDocumentInfo().title:
                text = reader.getDocumentInfo().title + extract_text(
                    io.BytesIO(response.body)
                )
            else:
                doc_body = extract_text(io.BytesIO(response.body))
                text = doc_body
                self.logger.info("doc_body type = " + str(type(doc_body)))
                # lines = doc_body.strip().split("\n")
                # top_i = 0
                # for i, line in enumerate(lines):
                #    if not len(line.strip()) == 0 and not re.search(
                #        r"technical\s+report|proceedings|preprint|to\s+appear|submission",
                #        line.lower(),
                #    ):
                #        top_i = i
                #        break
                # top_j = 0
                # for j, line in enumerate(lines[start + 1:start + max_lines + 1], start + 1):
                #    if not len(line.strip()) == 0:
                #        top_j = j
                #        break

            # determine if the pdf contains the key phrase
            phrase_found = False
            for phrase in self.key_phrases:
                if re.search(phrase, text, re.IGNORECASE):
                    phrase_found = True
                    break

            if phrase_found:
                self.logger.info("################################################")
                self.logger.info("################################################")
                self.logger.info("################################################")
                path = response.url.split("/")[-1]
                directory = "papers/" + str(year) + "/"
                if not os.path.exists(os.path.dirname(directory)):
                    try:
                        os.makedirs(os.path.dirname(directory))
                    except OSError as e:
                        self.logger.info(
                            "some thing I dont understand about a race condition?"
                        )
                directory += "/"
                self.logger.info("Doc Title = " + reader.getDocumentInfo().title)
                # ERROR: Some documents dont have title - particularly 2020
                if reader.getDocumentInfo().title:
                    self.logger.info("RESPONSE.BODY = " + str(type(response.body)))
                    with open(
                        directory + reader.getDocumentInfo().title + ".pdf", "w+"
                    ) as f:
                        f.write(response.body.decode("utf-8"))

            return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Please enter a link")
    parser.add_argument(
        "--link",
        "-l",
        help="set the root link for paper collection",
        default="https://papers.nips.cc/paper/",
        # default="https://papers.nips.cc/paper/2020/hash/ff42b03a06a1bed4e936f0e04958e168-Abstract.html",
    )
    parser.add_argument(
        "--key_phrase",
        "-k",
        help="set the keyphrase to look for in the papers",
        default="reinforcement learning",
    )
    parser.add_argument(
        "--year_lower",
        help="Set the lower bound for the desired years",
        default=2010,
    )
    parser.add_argument(
        "--year_upper",
        help="Set the upper bound for the desired years",
        default=2100,
    )
    parser.add_argument(
        "--depth_limit",
        help="Sets the crawlers depth limit - increase to obtain sources further from root url",
        default=3,
    )
    args = parser.parse_args()

    crawler_type = ""
    while crawler_type.lower() not in ["i", "n", "g"]:
        crawler_type = input(
            "*Note: You may have to provide a more specific URL for a general URL\nChoose a crawler - (I) ICML\t(N) NeurIPS\t(G) general\n"
        ).lower()

    if crawler_type == "g":
        site = ""
        while site == "":
            site = input("enter site url")
        spdr = General_Spider
    elif crawler_type == "n":
        spdr = NIPS_Spider
    # elif crawler_type == "i":

    process = CrawlerProcess()
    process.crawl(
        spdr,
        url_list=[args.link],
        phrase_list=[args.key_phrase],
        year_lower=args.year_lower,
        year_upper=args.year_upper,
        depth_limit=args.depth_limit,
    )
    process.start()

    print()

    print("args.link = ", args.link)
    print("args.key_phrase = ", args.key_phrase)
