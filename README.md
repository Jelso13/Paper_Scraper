# Paper_Scraper
Web Scraper for collecting papers with particular key-words from a specified conference link

key_phrase parameter only searches first page of the pdf to reduce the chance of collecting irrelevent papers or not collecting relevent papers.

TODO
- [ ] Add parameter for save location of papers
- [X] Save file names by the title of the document
- [ ] Handle deeply nested root URL's
- [ ] Determine papers from other pdf files (supplementary material, etc...)
- [ ] Add option for custom file name formatting

# Arguments
Example 1 shows providing the link argument to direct to a root url and a key phrase to search within pdfs
```
$ python3 --link https://papers.nips.cc/paper/2015 --key_phrase "reinforcement learning"
```
Example 2 will collect all pdfs regardless of key phrase
```
$ python3 --link https://papers.nips.cc/paper/2015
```
