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
import ffin
import invg
import threading
import re
from datetime import datetime

BASE_URL = "http://www.invg.de"
SEARCH_URL = "http://www.invg.de/showRealtimeCombined.action"
BUS_REFRESH_TIMEOUT = 20
WEATHER_REFRESH_TIMEOUT = 120
FREIFUNK_REFRESH_TIMEOUT = 60
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
    display.reset()
    while True:
        departures = get_realtime_info(STOP)['departures']
        departures = departures[:4]
        display.reset()
        before = datetime.now()
        if departures:
            for departure in departures:
                departure['destination'] = "{} {} ".format(__SCROLL_SEP, re.sub(r"\s+", " ", departure['destination']))
            while (datetime.now() - before).seconds < BUS_REFRESH_TIMEOUT:
                    display.position_cursor(0,0)
                    display_cmds = '\r\n'.join(map(format_departure, departures))
                    display.write(display_cmds)
                    for departure in departures:
                        departure['destination'] = departure['destination'][1:]+departure['destination'][:1]
                    time.sleep(0.25)
        else:
            display.reset()
            display.write("Lauf doch heim.")
            time.sleep(BUS_REFRESH_TIMEOUT)

def do_weather(display):
    display.reset()
    while True:
        forecasts = weather.get_forecast("Ingolstadt","de","de")
        forecasts = [[datetime.fromtimestamp(item['dt']), __SCROLL_SEP+" {}\xF8C {} ".format(item['main']['temp'], item['weather'][0]['description'])] for item in forecasts]
        before = datetime.now()
        while (datetime.now() - before).seconds < WEATHER_REFRESH_TIMEOUT:
            display.position_cursor(0,0)
            display.write("\r\n".join(["{:%H:%M} {}".format(*item)[:20] for item in forecasts]))
            for item in forecasts:
                item[1] = item[1][1:]+item[1][:1]
            time.sleep(0.25)

def do_freifunk(display):
    display.reset()
    display.write("{:^20}".format("Freifunk  Ingolstadt"))
    while True:
        nodes_json = ffin.get_nodes_json()
        clients = ffin.count_clients(nodes_json)
        nodes = ffin.count_nodes(nodes_json)
        before = datetime.now()
        stats = "Clients: {} \xDB Nodes: {} \xDB ".format(clients, nodes).ljust(20)
        while (datetime.now() - before).seconds < FREIFUNK_REFRESH_TIMEOUT:
            display.position_cursor(0,2)
            display.write(stats[:20])
            stats = stats[1:]+stats[:1]
            time.sleep(0.25)

def main():
    freifunk_display = ba66.posdisplay(port="/dev/ttyUSB1")
    weather_display = ba66.posdisplay(port="/dev/ttyUSB0", parity='O')
    bus_display = ba66.posdisplay(port="/dev/ttyUSB2", parity='O')

    bus_thread = threading.Thread(None, do_departures, args=[bus_display])
    bus_thread.start()

    freifunk_thread = threading.Thread(None, do_freifunk, args=[freifunk_display])
    freifunk_thread.start()

    weather_thread = threading.Thread(None, do_weather, args=[weather_display])
    weather_thread.start()


if __name__ == '__main__':
    main()
