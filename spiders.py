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

class Paper_Spider(scrapy.Spider):
    name = "Mr.Spider"

    def __init__(self, url_list, phrase_list, ignore_endings=[".json", ".zip", ".bib", ".pdf"], 
            paper_ending=".pdf", conference="data", directory="papers", strict_mode=True):
        super().__init__()
        self.start_urls = url_list
        self.key_phrases = phrase_list
        self.ignore_endings = ignore_endings
        self.paper_ending = paper_ending
        self.shelf = conference+".shelf"
        self.directory = directory
        self.strict_mode = strict_mode
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
        #print("response size = ", int(response.headers['content-length']))
        print("response type = ", type(response))
        if int(response.headers['content-length']) > 33554432:
            print(title, "is bigger than download warn")
        if not title:
            title = "temp"
        paper_recorded = self.paper_on_shelf(year, title)

        #if not paper_recorded:
        if True:
            # if the paper is not on the shelf
            reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
            if title=="temp":
                doc_title = reader.getDocumentInfo().title
                if doc_title:
                    title = doc_title
            else:
                doc_title=""

            text = u""
            text += doc_title.lower()
            for page in reader.pages:
                #text += page.extractText().lower()
                text += page.extractText()
        
            #if text.count("References") > 1:
            #    print("paper with more than one reference = {} with {} references".format(title, text.count("References")))
            #if text.count("Bibliography") > 1:
            #    print("USES BIBLIOGRAPHY")

            # remove the references section - any text after last 'References'
            text = text[:text.rfind("References")]

            if self.strict_mode:
                key_words = []
            else:
                # find set of all words in pdf
                key_words = re.findall(r'[a-zA-Z]\w+', text)
            self.add_to_shelf(year, title, key_words, response.url)

        #self.print_shelf(year)
        # Stupid filename requirements because windows sucks
        file_name = title.replace(" ", "_").replace("/","_").replace(":","-") + ".pdf"
        directory = "/".join([self.directory, year])+"/"
        file_location = directory+file_name
        # if the file is not downloaded
        if not os.path.exists(file_location):
            # if the file contains desired keywords
            with closing(shelve.open(self.shelf)) as shelf:
                tmp = shelf[year]
                shelf.close()
            # if it contains the correct keywords
            #if self.contains_keywords(tmp[title]["keywords"]):
            keyword_check = self.contains_keywords(text)
            if keyword_check:
                # download the file
                if not os.path.exists(os.path.dirname(directory)):
                    try:
                        os.makedirs(os.path.dirname(directory))
                    except OSError as e:
                        self.logger.info(
                            "some thing I dont understand about a race condition?"
                        )
                with open(file_location, "wb") as f:
                    #print("downloading ", file_location)
                    f.write(response.body)
                if self.strict_mode:
                    self.mod_shelf_keywords(year, title, keyword_check)
        return None

    def mod_shelf_keywords(self, year, title, keywords):
        with closing(shelve.open(self.shelf, "w")) as shelf:
            tmp = shelf[year]
            tmp[title]["keywords"].append(keywords[0])
            shelf[year] = tmp
            shelf.close()

    def add_to_shelf(self, year, title, key_words, url):
        with closing(shelve.open(self.shelf, "c")) as shelf:
            if str(year) not in shelf.keys():
                shelf[str(year)] = {}

            tmp = shelf[str(year)]
            tmp[title] = {
                "keywords": key_words,
                #"keywords": [],
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
        
    def contains_keywords(self, text, phrase=True):
        kwds = []
        for kw in self.key_phrases:
            if phrase:
                if kw in text:
                    if self.strict_mode:
                        kwds.append(kw)
                    else:
                        return True
            else:
                for word in kw.split(" "):
                    if word in text:
                        if self.strict_mode:
                            kwds.append(word)
                        else:
                            return True
        return kwds

class NeuripsSpider(Paper_Spider):
    name = "NeuripsSpider"
    custom_settings = {
        "DEPTH_LIMIT" : 3,
        "LOG_ENABLED" : False,
        "CONCURRENT_REQUESTS": 100,
        "DOWNLOAD_TIMEOUT": 100000,
        "download_maxsize": 0,
        "DOWNLOAD_MAXSIZE": 0,
    }    
    
    #def __init__(self, **kwargs):
    #    for key in ENV_DEFAULTS.keys():
    #        if key in kwargs.keys():
    #            setattr(self, key, kwargs.get(key))
    #        else:
    #            setattr(self, key, ENV_DEFAULTS[key])

    def __init__(self, url_list, phrase_list, ignore_endings=[".json", ".zip", ".bib", ".pdf"], 
            paper_ending=".pdf", conference="NeurIPS", directory="papers", strict_mode=True):
        super().__init__(url_list, phrase_list, ignore_endings=ignore_endings, paper_ending=paper_ending, 
            conference=conference, directory=directory, strict_mode=strict_mode)

    def parse(self, response):
        for sel in response.xpath("//div[@class='col']//a"):
            title = sel.xpath('text()').extract()[0]
            sub_link = sel.xpath("@href").extract()[0]
            yield response.follow(sub_link, callback=self.parse_l2, cb_kwargs={"title":title})

    def parse_l2(self, response, title):
        reg = re.search("\D((19|20)\d{2})\D", response.url)
        if reg:
            year = reg.group(1)
        else:
            year = None
        for subsublink in response.xpath("//div//a[contains(text(), 'Paper')]/@href").extract():
            if subsublink.endswith(".pdf"):
                yield response.follow(subsublink, callback=self.parse_pdf, cb_kwargs={"title":title, "year":year})


# num urls visited = 454
# total pdfs = 302
# total links = 303