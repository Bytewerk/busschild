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
import re
from datetime import datetime

BASE_URL = "http://www.invg.de"
SEARCH_URL = "http://www.invg.de/showRealtimeCombined.action"
REFRESH_TIMEOUT = 20
STOP = "Klinikum"

__SCROLL_SEP = "***"

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

def do_departures(display):
    departures = get_realtime_info(STOP)['departures']
    departures = departures[:4]
    display.reset()
    before = datetime.now()
    if departures:
        for departure in departures:
            departure['destination'] = "{} {} ".format(__SCROLL_SEP, re.sub(r"\s+", " ", departure['destination']))
        while (datetime.now() - before).seconds < 60:
                display.position_cursor(0,0)
                display_cmds = '\r\n'.join(map(format_departure, departures))
                display.write(display_cmds)
                for departure in departures:
                    departure['destination'] = departure['destination'][1:]+departure['destination'][:1]
                time.sleep(0.25)
    else:
        display.reset()
        display.write("Lauf doch heim.")
        time.sleep(60)

def do_weather(display):
    forecasts = weather.get_forecast("Ingolstadt","de","de")
    forecasts = [[datetime.fromtimestamp(item['dt']), __SCROLL_SEP+" {}°C {} ".format(item['main']['temp'], item['weather'][0]['description'])] for item in forecasts]
    before = datetime.now()
    while (datetime.now() - before).seconds < 60:
        display.position_cursor(0,0)
        display.write("\r\n".join(["{:%H:%M} {}".format(*item)[:20] for item in forecasts]))
        for item in forecasts:
            item[1] = item[1][1:]+item[1][:1]
        time.sleep(0.25)

def main():
    display = ba66.posdisplay(parity="O")
    while True:
        do_weather(display)
        do_departures(display)

if __name__ == '__main__':
    main()
