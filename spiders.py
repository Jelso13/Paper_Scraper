import scrapy
import logging
import PyPDF2
import io


logging.getLogger("scrapy").propagate = False
file1 = open("log_file.txt", "w")

class Paper_Spider(scrapy.Spider):
    name = "Mr.Spider"

    def __init__(self, url_list, phrase_list, ignore_endings=[".json", ".zip", ".bib", ".pdf"], paper_ending=".pdf"):
        super().__init__()
        self.start_urls = url_list
        self.key_phrases = phrase_list
        self.ignore_endings = ignore_endings
        self.paper_ending = paper_ending

    def parse(self, response):
        for sub_link in response.xpath("//div//a/@href").extract():
            if sub_link.endswith(self.paper_ending):
                yield response.follow(sub_link, callback=self.parse_pdf)
            elif all([not sub_link.endswith(tp) for tp in self.ignore_endings]):
                yield response.follow(sub_link, callback=self.parse)

    def parse_pdf(self, response):
        file1.write(response.url+"\n")
        print(response.url)
        #print("WOULD WRITE HERE")
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
        #print("response url = ", response.url)
        #print("time taken to get the url = ", time.time()-start)
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
        #print("time to check all pages = ", time.time()-start)

        start = time.time()
        import re
        keywords = re.findall(r'[a-zA-Z]\w+', text)
        #print("time to get all keywords = ", time.time()-start)
        #print("len(keywords = ", len(keywords))

        if keywords[0] in text:
            #print("Found keyword")
            return True
        else:
            #print("Did not find keyword")
            return False

    def store_paper_info(self, title, keywords, url, tags=None):
        with closing(shelve.open("paper_info.shelf")) as shelf:
            shelf[title] = {
                "keywords": keywords,
                "url": url,
                "tags": []
            }

class NeuripsSpider(Paper_Spider):
    def __init__(self, **kwargs):
        super().__init__(paper_ending="Paper.pdf", **kwargs)