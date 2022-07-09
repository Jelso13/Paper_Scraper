import requests
import time
import shelve
from contextlib import closing


#from twisted.internet import reactor
#from scrapy.crawler import CrawlerRunner





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
from spiders import NeuripsSpider, Paper_Spider

logging.getLogger("scrapy").propagate = False


def test_pdf_checker():
    #no_rl_link = "https://proceedings.neurips.cc/paper/2019/file/02f063c236c7eef66324b432b748d15d-Paper.pdf"
    #rl_link = "https://proceedings.neurips.cc/paper/2019/file/02ed812220b0705fabb868ddbf17ea20-Paper.pdf"
    #rl_link = "https://proceedings.neurips.cc/paper/2019/hash/02ed812220b0705fabb868ddbf17ea20-Abstract.html"
    #no_rl_link = "https://proceedings.neurips.cc/paper/2019/hash/02f063c236c7eef66324b432b748d15d-Abstract.html"
    no_rl_link = "https://proceedings.neurips.cc/paper/1998"
    #spdr = Paper_Spider
    spdr = NeuripsSpider
    process = CrawlerProcess()
    process.crawl(spdr, url_list=["https://proceedings.neurips.cc/paper/1998"], phrase_list=["reinforcement learning"])
    #process.crawl(spdr, url_list=[
    #    "https://proceedings.neurips.cc/paper/1998",
    #    "https://proceedings.neurips.cc/paper/1999",
    #    "https://proceedings.neurips.cc/paper/2000",
    #    "https://proceedings.neurips.cc/paper/2001",
    #    "https://proceedings.neurips.cc/paper/2002",
    #    "https://proceedings.neurips.cc/paper/2003",
    #    "https://proceedings.neurips.cc/paper/2004",
    #    ], phrase_list=["reinforcement learning"])


    #process = CrawlerRunner()
    #process.crawl(spdr, **{"url_list":["https://proceedings.neurips.cc/paper/1998"], "phrase_list":["reinforcement learning"]})
    #process.crawl(spdr, **{"url_list":["https://proceedings.neurips.cc/paper/1999"], "phrase_list":["reinforcement learning"]})
    #process.crawl(spdr, **{"url_list":["https://proceedings.neurips.cc/paper/2000"], "phrase_list":["reinforcement learning"]})
    #process.crawl(spdr, **{"url_list":["https://proceedings.neurips.cc/paper/2001"], "phrase_list":["reinforcement learning"]})
    #process.crawl(spdr, **{"url_list":["https://proceedings.neurips.cc/paper/2002"], "phrase_list":["reinforcement learning"]})
    #process.crawl(spdr, **{"url_list":["https://proceedings.neurips.cc/paper/2003"], "phrase_list":["reinforcement learning"]})
    #process.crawl(spdr, **{"url_list":["https://proceedings.neurips.cc/paper/2004"], "phrase_list":["reinforcement learning"]})
    #deferred = process.join()
    #deferred.addBoth(lambda _: reactor.stop())

    time_start = time.time()
    #reactor.run()
    process.start()
    print("time taken = {:.2f} seconds".format(time.time()-time_start))


if __name__ == "__main__":
    #start = time.time()
    #Paper_Spider.contains_keywords("https://proceedings.neurips.cc/paper/2019/file/02ed812220b0705fabb868ddbf17ea20-Paper.pdf", ["reinforcement learning"])
    #print("Time taken = {:.2f} seconds".format(time.time()-start))
    #start = time.time()
    #Paper_Spider.contains_keywords("https://proceedings.neurips.cc/paper/2019/file/02f063c236c7eef66324b432b748d15d-Paper.pdf", ["reinforcement learning"])
    #print("Time taken = {:.2f} seconds".format(time.time()-start))
    test_pdf_checker()
    #start_neurips_spider()

    # Time taken for all links from 1998-2004:
    #   seperate spiders takes:                     658 seconds
    #   one spider multiple links takes             747 seconds