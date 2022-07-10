import json
from contextlib import closing
import shelve

def show_shelf(shelf_name):
    with closing(shelve.open(shelf_name)) as shelf:
        print(json.dumps(dict(shelf), sort_keys=True, indent=4))

def get_rl(shelf_name):
    with closing(shelve.open(shelf_name)) as shelf:
        tmp = shelf
        out_dict = {}
        for year in tmp.keys():
            out_dict[year] = {}
            for title in tmp[year].keys():
                if "reinforcement learning" in tmp[year][title]["keywords"]:
                    out_dict[year][title] = tmp[year][title]
        print(json.dumps(dict(out_dict), sort_keys=True, indent=4))         

if __name__ == "__main__":
    #show_shelf("NeurIPS.shelf")
    get_rl("NeurIPS.shelf")