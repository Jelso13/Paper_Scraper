import scrapy
from scrapy.selector import Selector
import logging
import PyPDF2
import io
import os
import shelve
from contextlib import closing
import re
import time

logging.getLogger("scrapy").propagate = False
file1 = open("log_file.txt", "w")

class Paper_Spider(scrapy.Spider):
    name = "Mr.Spider"

    def __init__(self, url_list, phrase_list, ignore_endings=[".json", ".zip", ".bib", ".pdf"], paper_ending=".pdf", conference="data", directory="papers"):
        super().__init__()
        self.start_urls = url_list
        self.key_phrases = phrase_list
        self.ignore_endings = ignore_endings
        self.paper_ending = paper_ending
        self.shelf = conference+".shelf"
        self.directory = directory
        #if not os.path.exists(self.shelf):
        #    shelve.open(self.shelf)


    def parse(self, response):
        print("response depth = ", response.meta.get("depth", 0))
        for sub_link in response.xpath("//div//a/@href").extract():
            if sub_link.endswith(self.paper_ending):
                yield response.follow(sub_link, callback=self.parse_pdf)
            elif all([not sub_link.endswith(tp) for tp in self.ignore_endings]):
                yield response.follow(sub_link, callback=self.parse)

    def parse_pdf(self, response, title=None, year=None):
        # max file length { mac = 255 chars, linux =  255, windows = 260 chars}
        #file1.write(title+"\n\t"+response.url+"\n")
        print("title length = {}".format(len(title)))
        #with open("papers/" + path, "wb") as f:
        #    f.write(response.body)
        if not title:
            title = "temp"

        paper_recorded = self.paper_on_shelf(year, title)
        print("paper recorded = ", str(paper_recorded))

        # Check shelf if what I'm looking for
        #   if desired then check if downloaded
        #       if downloaded print it or something idk
        #       else:
        #           download it to folder
        # if not on shelf:
        #   process and add to shelf


        file_name = title + ".pdf"
        if paper_recorded:
            ###
            print("In Shelf")

            return None

        reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
        doc_title = reader.getDocumentInfo().title
        if title=="temp" and doc_title:
            title = doc_title
        else:
            doc_title=""

        text = u""
        text += doc_title
        for page in reader.pages:
            text += page.extractText()
        
        # find set of all words in pdf
        key_words = re.findall(r'[a-zA-Z]\w+', text)

        self.add_to_shelf(year, title, key_words, response.url)

        #self.print_shelf(year)

        if self.contains_keywords(text):
            # download the paper
            pass 
        return None

    def add_to_shelf(self, year, title, key_words, url):
        with closing(shelve.open(self.shelf)) as shelf:
            if str(year) not in shelf.keys():
                shelf[str(year)] = {}

            tmp = shelf[str(year)]
            tmp[title] = {
                #"keywords": key_words,
                "keywords": [],
                "url": url,
                "user_tags": []
            }
            shelf[str(year)] = tmp
            shelf.close()

    def print_shelf(self, year):
        import json
        with closing(shelve.open(self.shelf)) as shelf:
            print(json.dumps(dict(shelf), sort_keys=True, indent=4))


    def paper_on_shelf(self, year, title):
        if not os.path.exists(self.shelf):
            return False
        with closing(shelve.open(self.shelf)) as shelf:
            if str(year) not in shelf.keys():
                return False
            if title not in shelf[str(year)]:
                return False
        return True
        
    def contains_keywords(self, text):
        for kw in self.key_phrases:
            if kw in text:
                return True

class NeuripsSpider(Paper_Spider):
    name = "NeuripsSpider"
    custom_settings = {
        "DEPTH_LIMIT" : 3,
        "LOG_ENABLED" : False,
        "CONCURRENT_REQUESTS": 100,
        "DOWNLOAD_TIMEOUT": 100,
    }

    def __init__(self, url_list, phrase_list, ignore_endings=[".json", ".zip", ".bib", ".pdf"], paper_ending=".pdf", conference="NeurIPS", directory="papers"):
        super().__init__(url_list, phrase_list, ignore_endings=ignore_endings, paper_ending=paper_ending, conference=conference, directory=directory)

    def parse(self, response):
        #file1.write(response.url+"\n")
        for sel in response.xpath("//div[@class='col']//a"):
            title = sel.xpath('text()').extract()[0]
            sub_link = sel.xpath("@href").extract()[0]
            file1.write("\t"+sub_link+"\n")
            yield response.follow(sub_link, callback=self.parse_l2, cb_kwargs={"title":title})

    def parse_l2(self, response, title):
        reg = re.search("\D((19|20)\d{2})\D", response.url)
        if reg:
            year = reg.group(1)
        else:
            year = None
        for subsublink in response.xpath("//div//a[contains(text(), 'Paper')]/@href").extract():
            #file1.write(subsublink+"\n")
            if subsublink.endswith(".pdf"):
                yield response.follow(subsublink, callback=self.parse_pdf, cb_kwargs={"title":title, "year":year})


# num urls visited = 454
# total pdfs = 302
# total links = 303