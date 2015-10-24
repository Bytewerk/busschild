"""
Show bus departures times on a POS display.
"""

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "http://www.invg.de"
SEARCH_URL = "http://www.invg.de/showRealtimeCombined.action"
BAUDRATE = 9600
STOP = "Klinikum"

def get_realtime_info(stop_name):
    """
    Return the real time info for the first search hit for *stop_name* as a dict.
    """
    resp = requests.post(SEARCH_URL, {"nameKey": stop_name})
    soup = BeautifulSoup(resp.text)
    table = soup.select("table.table-bs")[0]
    tbody = table.tbody
    first_hit = BASE_URL + tbody.tr.td.a["href"]
    first_hit = first_hit.replace("showMultiple", "getRealtimeData")
    stop_resp = requests.get(first_hit)
    return json.loads(stop_resp.text)

if __name__ == '__main__':
    main()
