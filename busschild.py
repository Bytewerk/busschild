"""
Show bus departures times on a POS display.
"""

from bs4 import BeautifulSoup
from datetime import datetime
import ba66
import json
import re
import requests
import socket
import sys
import time
import traceback

RT_URLS = [
    "https://fpa.invg.de/bin/stboard.exe/dny?L=vs_liveticker&tpl=liveticker2json&&input=39099&boardType=dep&productsFilter=1111111111&additionalTime=0&disableEquivs=yes&ignoreMasts=yes&maxJourneys=5&start=yes&selectDate=today&monitor=1&outputMode=tickerDataOnly",
    "https://fpa.invg.de/bin/stboard.exe/dny?L=vs_liveticker&tpl=liveticker2json&&input=39002&boardType=dep&productsFilter=1111111111&additionalTime=0&disableEquivs=yes&ignoreMasts=yes&maxJourneys=5&start=yes&selectDate=today&monitor=1&outputMode=tickerDataOnly",
    "https://fpa.invg.de/bin/stboard.exe/dny?L=vs_liveticker&tpl=liveticker2json&&input=39001&boardType=dep&productsFilter=1111111111&additionalTime=0&disableEquivs=yes&ignoreMasts=yes&maxJourneys=5&start=yes&selectDate=today&monitor=1&outputMode=tickerDataOnly"
]
BUS_REFRESH_TIMEOUT = 20
STOP = "Klinikum"
DISPLAY_WIDTH = 20
__SCROLL_SEP = "\xDB"


class Bus:
    def __init__(self, date, time, route, destination):
        self.datetime = datetime.strptime(date + " " + time, "%d.%m.%y %H:%M")
        self.route = route
        self.destination = destination

    def __str__(self):
        return "{:%H}:{:%M} {} {}".format(self.datetime, self.datetime, self.route, self.destination)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.datetime < other.datetime


def get_realtime_info():
    """
    Fetch realtime information from RT_URLS.
    """
    buses = []
    for url in RT_URLS:
        json = requests.get(url).json()
        for j in json['journey']:
            buses.append(Bus(j['da'], j['ti'], j['pr'].split()[1], j['st']))
    buses.sort()
    return buses


def do_departures(display):
    display.reset()
    while True:
        try:
            buses = get_realtime_info()[:4]
            before = datetime.now()
            for bus in buses:
                if (len(str(bus)) >= DISPLAY_WIDTH):
                    bus.destination = "{} {} ".format(__SCROLL_SEP, re.sub(r"\s+", " ", bus.destination))
                else:
                    bus.destination = bus.destination.ljust(DISPLAY_WIDTH - len(str(bus)))
            while (datetime.now() - before).seconds < BUS_REFRESH_TIMEOUT:
                display.position_cursor(0, 0)
                display_cmds = '\r\n'.join(map(lambda b: str(b)[:20], buses))
                display.write(display_cmds)
                for bus in buses:
                    if (len(str(bus)) >= DISPLAY_WIDTH):
                        bus.destination = bus.destination[1:] + bus.destination[:1]
                time.sleep(0.5)
        except:
            display.reset()
            display.write("Keine Daten od. Feh-\r\nler. Lauf heim.")
            time.sleep(BUS_REFRESH_TIMEOUT)


def main():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((sys.argv[1], int(sys.argv[2])))
            display = ba66.posdisplay(sock)
            do_departures(display)
        except:
            print(traceback.format_exc(), file=sys.stderr)
            time.sleep(10)


if __name__ == '__main__':
    main()
