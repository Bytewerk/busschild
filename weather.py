"""
Simplistic module for querying `openweathermap.org`.
"""

import requests
from datetime import datetime

__OWM_APP_ID = "bd82977b86bf27fb59a04b61b657fb6f"
__OWM_FORECAST_URL_FMT = "http://api.openweathermap.org/data/2.5/forecast?q={},{}&mode=json&lang={}&units=metric&cnt={}&appid={}"
__OWM_CURRENT_URL_FMT = "http://api.openweathermap.org/data/2.5/weather?q={},{}&mode=json&lang={}&units=metric&appid={}"

def get_forecast(city_name, country_code, lang="en", forecast_cnt=3):
    """
    *country_code*: e.g. "de" for Germany,
    *city_name* should be self-explanatory
    Return the current weather + *forecast_cnt* forecasts.
    """
    forecast_resp = requests.get(__OWM_FORECAST_URL_FMT.format(city_name, country_code, lang, forecast_cnt, __OWM_APP_ID))
    forecast_json = forecast_resp.json()
    current_resp = requests.get(__OWM_CURRENT_URL_FMT.format(city_name, country_code, lang, __OWM_APP_ID))
    current_json = current_resp.json()
    return [current_json] + forecast_json['list']

def fmt_forecast(forecast):
    def __fmt(item):
        date_time = datetime.fromtimestamp(item['dt'])
        description = item['weather'][0]['description']
        temp = item['main']['temp']
        return "{:%H:%M} {} {:>6}".format(date_time, description, temp)
    return "\r\n".join(map(__fmt,forecast))
