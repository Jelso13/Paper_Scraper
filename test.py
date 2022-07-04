import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule

from scrapy.http import Request


class crawl(scrapy.Spider):
    name = "crawl"
    # allowed_domains = ["www.nips.cc"]
    # start_urls = ["https://papers.nips.cc/paper/2018"]
    start_urls = [
        "https://papers.nips.cc/paper/2018/hash/00ac8ed3b4327bdd4ebbebcb2ba10a00-Abstract.html"
    ]

    def __init__(self):
        super().__init__()
        self.depth_limit = 3

    def parse(self, response):
        for href in response.css("div#all_results h3 a::attr(href)").extract():
            yield Request(url=response.urljoin(href), callback=self.parse_article)

    def parse_article(self, response):
        for href in response.css(
            'div.download_wrapper a[href$=".pdf"]::attr(href)'
        ).extract():
            yield Request(url=response.urljoin(href), callback=self.save_pdf)

    def save_pdf(self, response):
        path = response.url.split("/")[-1]
        self.logger.info("Saving PDF %s", path)
        # with open(path, "wb") as f:
        #    f.write(response.body)


if __name__ == "__main__":
    spdr = crawl
    process = CrawlerProcess()
    process.crawl(spdr)
    process.start()
