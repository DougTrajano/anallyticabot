import streamlit as st
import json
import logging

def load_parameters(path):
    logging.info({"message": "loading parameters.", "path": path})
    with open(path) as json_file:
        data = json.load(json_file)
    return data