import requests
import time





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
import logging

logging.getLogger("scrapy").propagate = False


class Paper_Spider(scrapy.Spider):
    name = "Mr.Spider"

    def __init__(self, url_list, phrase_list):
        super().__init__()
        self.start_urls = url_list
        self.key_phrases = phrase_list

    def parse(self, response):
        # //div//a/@href gets the link for an href in an <a> tag
        for sub_link in response.xpath("//div//a/@href").extract():
            #self.logger.info(sub_link)
            if sub_link.endswith(".pdf"):
                yield response.follow(sub_link, callback=self.parse_pdf)
            else:
                yield response.follow(sub_link, callback=self.parse)

    def parse_pdf(self, response):
        # used to check if the pdf contains one of the key_phrases
        path = response.url.split("/")[-1]
        #self.logger.info("Saving PDF %s", path)
        print("response = ", response)
        print("WOULD WRITE HERE")
        #with open("papers/" + path, "wb") as f:
        #    f.write(response.body)

        # IDEA: Maybe use pdfminer instead?
        reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
        text = u""
        if reader.getDocumentInfo().title:
            text += reader.getDocumentInfo().title
            for page in reader.pages:
                text += page.extractText()
        return None

    @staticmethod
    def contains_keywords(url, keywords):
        import requests
        start = time.time()
        response = requests.get(url)
        print("response url = ", response.url)
        print("time taken to get the url = ", time.time()-start)
        reader = PyPDF2.PdfFileReader(io.BytesIO(response.content))

        #print("response.content")
        text = u""
        if reader.getDocumentInfo().title:
            text += reader.getDocumentInfo().title.lower()
            if keywords[0] in text:
                print("Found keyword")
                #return True
        start = time.time()
        for page in reader.pages:
            pg = page.extractText().lower()
            text += pg
            if keywords[0] in pg:
                print("Found keyword")
                #return True
        print("time to check all pages = ", time.time()-start)

        start = time.time()
        import re
        keywords = re.findall(r'[a-zA-Z]\w+', text)
        print("time to get all keywords = ", time.time()-start)
        print("len(keywords = ", len(keywords))
        import shelve

        if keywords[0] in text:
            print("Found keyword")
            return True
        else:
            print("Did not find keyword")
            return False

def start_neurips_spider():
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
    process.crawl(spdr, url_list=["https://papers.nips.cc/paper/2020"], phrase_list=[args.key_phrase])
    process.start()

    print()

    print("args.link = ", args.link)
    print("args.key_phrase = ", args.key_phrase)

def test_pdf_checker():
    #no_rl_link = "https://proceedings.neurips.cc/paper/2019/file/02f063c236c7eef66324b432b748d15d-Paper.pdf"
    #rl_link = "https://proceedings.neurips.cc/paper/2019/file/02ed812220b0705fabb868ddbf17ea20-Paper.pdf"
    rl_link = "https://proceedings.neurips.cc/paper/2019/hash/02ed812220b0705fabb868ddbf17ea20-Abstract.html"
    no_rl_link = "https://proceedings.neurips.cc/paper/2019/hash/02f063c236c7eef66324b432b748d15d-Abstract.html"
    spdr = Paper_Spider
    process = CrawlerProcess()
    process.crawl(spdr, url_list=[no_rl_link], phrase_list=["reinforcement learning"])
    process.start()


if __name__ == "__main__":
    start = time.time()
    Paper_Spider.contains_keywords("https://proceedings.neurips.cc/paper/2019/file/02ed812220b0705fabb868ddbf17ea20-Paper.pdf", ["reinforcement learning"])
    print("Time taken = {:.2f} seconds".format(time.time()-start))
    start = time.time()
    Paper_Spider.contains_keywords("https://proceedings.neurips.cc/paper/2019/file/02f063c236c7eef66324b432b748d15d-Paper.pdf", ["reinforcement learning"])
    print("Time taken = {:.2f} seconds".format(time.time()-start))
    #test_pdf_checker()
    #start_neurips_spider()