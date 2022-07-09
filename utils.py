import json
from contextlib import closing
import shelve

def show_shelf(shelf_name):
    with closing(shelve.open(shelf_name)) as shelf:
        print(json.dumps(dict(shelf), sort_keys=True, indent=4))

if __name__ == "__main__":
    show_shelf("NeurIPS.shelf")