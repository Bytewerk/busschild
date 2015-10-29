"""
Show bus departures times on a POS display.
"""

import requests
from bs4 import BeautifulSoup
import json
import ba66
import time
import sys

BASE_URL = "http://www.invg.de"
SEARCH_URL = "http://www.invg.de/showRealtimeCombined.action"
REFRESH_TIMEOUT = 20
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

def format_departure(departure):
    route = departure['route'].replace(' ','')
    destination = departure['destination']
    strtime = departure['strTime'].replace(' ','')
    if strtime == "0":
        strtime = "RENN!"
    line = "{} {} {} ".format(route, strtime, destination)
    if len(line) >= 20:
        line = line[:20]
    else:
        line = line.ljust(20, ' ')
    return line

def main():
    display = ba66.posdisplay(parity="O")
    while True:
        departures = get_realtime_info(STOP)['departures']
        departures = departures[:4]
        display.position_cursor(0,0)
        if departures:
            display_cmds = '\r\n'.join(map(format_departure, departures))
            print(repr(display_cmds), file=sys.stderr)
            for c in display_cmds:
                display.write(c)
                time.sleep(0.1)
        else:
            display.reset()
            display.write("Lauf doch heim.")
        time.sleep(REFRESH_TIMEOUT)

if __name__ == '__main__':
    main()
