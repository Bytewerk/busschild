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

def main():
    from ba66 import posdisplay
    d = posdisplay()
    d.reset()
    d.write("{:^20}".format("Freifunk  Ingolstadt"))
    while True:
        nodes_json = get_nodes_json()
        clients = count_clients(nodes_json)
        nodes = count_nodes(nodes_json)
        before = datetime.now()
        stats = "Clients: {} \xDB Nodes: {} \xDB ".format(clients, nodes).ljust(20)
        while (datetime.now() - before).seconds < 60:
            d.position_cursor(0,2)
            d.write(stats[:20])
            stats = stats[1:]+stats[:1]
            time.sleep(0.25)

if __name__ == '__main__':
    main()
