import requests





"""
Think better to use a crawler rather than a web scraper
as need finer control over the files retrieved given
the pdfs need to be searched.
"""

"""
Have a file with processed urls sorted by conference.
The file will involve json dumps - supposedly faster 
    and human readable
Each file has a list of associated tags ripped from 
    the front page or some other heuristic.
When evaluating a link
    determine if the link is already in the dictionary
If in the dictionary
    check the tags for the required tag
Else
    process the pdf and add the information to the file
"""

"Links anchor text gives the name of the paper"



#####
"""
Possibilities for storage

- Pickle
- JSON

Requirements:
    - appendable (updating the data structure)

Estimated Data Size
    2000 * 
"""



#### test stuff
import sys
import argparse
import scrapy
from scrapy.crawler import CrawlerProcess
import PyPDF2
import io


class Paper_Spider(scrapy.Spider):
    name = "Mr.Spider"

    def __init__(self, url_list, phrase_list):
        super().__init__()
        self.start_urls = url_list
        self.key_phrases = phrase_list

    def parse(self, response):
        # //div//a/@href gets the link for an href in an <a> tag
        for sub_link in response.xpath("//div//a/@href").extract():
            self.logger.info(sub_link)
            if sub_link.endswith(".pdf"):
                yield response.follow(sub_link, callback=self.parse_pdf)
            else:
                yield response.follow(sub_link, callback=self.parse)

    def parse_pdf(self, response):
        # used to check if the pdf contains one of the key_phrases
        path = response.url.split("/")[-1]
        self.logger.info("Saving PDF %s", path)
        with open("papers/" + path, "wb") as f:
            f.write(response.body)

        # IDEA: Maybe use pdfminer instead?
        reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
        text = u""
        if reader.getDocumentInfo().title:
            text += reader.getDocumentInfo().title
            for page in reader.pages:
                text += page.extractText()
        return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Please enter a link")
    parser.add_argument(
        "--link",
        "-l",
        help="set the root link for paper collection",
        default="https://papers.nips.cc/paper/2020",
        # default="https://papers.nips.cc/paper/2020/hash/ff42b03a06a1bed4e936f0e04958e168-Abstract.html",
    )
    parser.add_argument(
        "--key_phrase",
        "-k",
        help="set the keyphrase to look for in the papers",
        default="reinforcement learning",
    )
    args = parser.parse_args()

    spdr = Paper_Spider
    process = CrawlerProcess()
    process.crawl(spdr, url_list=[args.link], phrase_list=[args.key_phrase])
    process.start()

    print()

    print("args.link = ", args.link)
    print("args.key_phrase = ", args.key_phrase)