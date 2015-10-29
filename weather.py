"""
Simplistic module for querying `openweathermap.org`.
"""

import requests
from datetime import datetime

__OWM_APP_ID = "bd82977b86bf27fb59a04b61b657fb6f"
__OWM_URL_FMT = "http://api.openweathermap.org/data/2.5/forecast?q={},{}&mode=json&appid={}"

def get_forecast(city_name, country_code):
    """
    *country_code*: e.g. "de" for Germany,
    *city_name* should be self-explanatory
    """
    resp = requests.get(__OWM_URL_FMT.format(city_name, country_code, __OWM_APP_ID))
    w_json = resp.json()
    return w_json['list']
