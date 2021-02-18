import json
import logging
import collections

def load_parameters(path):
    logging.info({"message": "loading parameters.", "path": path})
    with open(path) as json_file:
        data = json.load(json_file)
    return data

def flatten(d, sep="."):

    obj = collections.OrderedDict()

    def recurse(t, parent_key=""):

        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i], parent_key + sep + str(i)
                        if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t

    recurse(d)

    return dict(obj)