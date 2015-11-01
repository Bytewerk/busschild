"""
Provide information about the current status of Freifunk Ingolstadt.
"""

NODES_URL = "http://freifunk-ingolstadt.de/map/nodes.json"

import requests
import time
from datetime import datetime

def get_nodes_json():
    """
    Fetch the nodes.json file from Freifunk Ingolstadt, turn it into a dictionary and return that.
    """
    resp = requests.get(NODES_URL)
    return resp.json()

def count_clients(nodes_json):
    """
    Extract the total count of connected clients from *nodes_json*.
    """
    return sum(map(lambda n: n['statistics']['clients'], nodes_json['nodes'].values()))

def count_nodes(nodes_json):
    """
    Extract the total count of nodes from *nodes_json*.
    """
    return len(nodes_json['nodes'])
