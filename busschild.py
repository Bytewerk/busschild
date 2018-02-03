"""
Show bus departures times on a POS display.
"""

import requests
from bs4 import BeautifulSoup
import json
import ba66
import time
import sys
import weather
import threading
import re
from datetime import datetime

BASE_URL = "https://www.invg.de"
SEARCH_URL = "https://www.invg.de/rt/showRealtimeCombined.action"
BUS_REFRESH_TIMEOUT = 20
WEATHER_REFRESH_TIMEOUT = 120
FREIFUNK_REFRESH_TIMEOUT = 60
STOP = "Klinikum"

__SCROLL_SEP = "\xDB"

def get_realtime_info(stop_name):
    """
    Return the real time info for the first search hit for *stop_name* as a dict.
    """
    resp = requests.post(SEARCH_URL, {"nameKey": stop_name})
    soup = BeautifulSoup(resp.text, "lxml")
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

def do_departures(display):
    display.reset()
    while True:
        try:
            departures = get_realtime_info(STOP)['departures']
            departures = departures[:4]
            before = datetime.now()
            for departure in departures:
                departure['destination'] = "{} {} ".format(__SCROLL_SEP, re.sub(r"\s+", " ", departure['destination']))
            while (datetime.now() - before).seconds < BUS_REFRESH_TIMEOUT:
                    display.position_cursor(0,0)
                    display_cmds = '\r\n'.join(map(format_departure, departures))
                    display.write(display_cmds)
                    for departure in departures:
                        departure['destination'] = departure['destination'][1:]+departure['destination'][:1]
                    time.sleep(0.25)
        except:
            display.reset()
            display.write("Keine Daten od. Feh-\r\nler. Lauf heim.")
            time.sleep(BUS_REFRESH_TIMEOUT)

def main():
    bus_display = ba66.posdisplay(port="/dev/ttyUSB2", parity='O')
    do_departures(bus_display)

if __name__ == '__main__':
    main()
