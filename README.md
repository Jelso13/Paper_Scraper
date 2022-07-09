# Paper_Scraper
Web Scraper for collecting papers with particular key-words from a specified conference link

key_phrase parameter only searches first page of the pdf to reduce the chance of collecting irrelevent papers or not collecting relevent papers.

TODO
- [ ] Create ICML class
- [ ] Issue with titles that contain / character
- [ ] Strict mode keywords not working - many have empty array
- [ ] Issue with File sizes being too large to download
- [ ] Issue with collecting papers that include keyphrase in the references/bibliography
- [X] Issue with getting title from metadata as some files dont have it.
- [X] Add a strict mode that only add keywords to the shelf when searched for.
- [ ] Somehow sort issue with storing key phrases (reinforcement learning) as key words is too broad and current approach doesnt work for phrases
- [ ] handle parameters and options that are passed to the program
- [X] Store paper information in shelving
- [X] store papers organised in some way only if not already downloaded

These are the old objectives *update this
- [ ] Add parameter for save location of papers
- [X] Save file names by the title of the document
- [ ] Handle deeply nested root URL's
- [ ] Determine papers from other pdf files (supplementary material, etc...)
- [ ] Add option for custom file name formatting
- [ ] Improve efficiency to pass over papers that are already collected

# Arguments

