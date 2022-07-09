from contextlib import closing
import shelve
import tqdm
import time

# runs in 2.3125727 seconds
def populate_dict():
    with closing(shelve.open('mydict.shelf', 'c')) as shelf:
        years = 2022-2015
        num_papers = 2500 * years
        num_keywords = 5000
        for i in tqdm.tqdm(range(num_papers)):
            shelf["paper_with_name_"+str(i)] = {
                "keywords": ["fadslkfjd" for i in range(num_keywords)],
                "url": "https://test.com/something/something"
            }

# Runs in 0.0634 seconds
def update_dict():
    with closing(shelve.open('mydict.shelf')) as shelf:
        shelf["paper_with_name_400"] = {
            "keywords": ["yeet", "yote"],
            "url": "https://testing.com"
        }
        shelf.close()
        
def update_partial_dict():
    with closing(shelve.open('mydict.shelf'), "w") as shelf:
        #shelf["paper_with_name_400"]["keywords"].append("yute")
        #shelf["paper_with_name_400"]["keywords"] = shelf["paper_with_name_400"]["keywords"] + ["yute"]
        tmp = shelf["paper_with_name_400"]
        tmp["keywords"].append("yute")
        shelf["paper_with_name_400"] = tmp

        shelf.close()


# Runs in 0.052658 seconds
def query_dict():
    with closing(shelve.open('mydict.shelf')) as shelf:
        print("shelf['paper_with_name_400'] = ", shelf["paper_with_name_400"])
        #print("shelf['paper_with_name_235'] = ", shelf["paper_with_name_235"])

# Runs in 0.0625329 seconds
def check_key_exists():
    with closing(shelve.open('mydict.shelf')) as shelf:
        if "paper_with_name_10100" in shelf.keys():
            print("in the dictionary")

start = time.time()
#check_key_exists()
#query_dict()
#update_dict()
populate_dict()
print("time taken to query dict = ", time.time()-start)

