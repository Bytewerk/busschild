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
    forecast = [current_json] + forecast_json['list']
    return forecast

class Forecast():
    def __init__(self, fc_dict):
        self.dt = datetime.fromtimestamp(fc_dict['dt'])
        self.description = fc_dict['weather'][0]['description']
        self.temp = fc_dict['main']['temp']

_forecast_fmt = "{:%H:%M} {:>6}C{}"
_forecast_fmt_min_width = len(_forecast_fmt.format(datetime.fromtimestamp(0), "", ""))
def fmt_forecasts_sidescrolling(fc_dicts, target_width=20):
    forecasts = [Forecast(fc_dict) for fc_dict in fc_dicts]
    max_desc_width = max(map(lambda d: len(d.description), forecasts))
    target_desc_width = target_width - _forecast_fmt_min_width
    for forecast in forecasts:
        forecast.description = forecast.description.ljust(max_desc_width)
    strs = []
    scroll_dist = 1 if target_desc_width >= max_desc_width else max_desc_width - target_desc_width + 1
    for i in range(scroll_dist):
        strs.append("\r\n".join([_forecast_fmt.format(fc.dt, fc.temp, (fc.description[i:]+fc.description[:i])[:target_desc_width]) for fc in forecasts]))
    return strs

# def fmt_forecast(forecast):
#     def __fmt(item):
#         date_time = datetime.fromtimestamp(item['dt'])
#         description = item['weather'][0]['description']
#         temp = item['main']['temp']
#         return "{:%H:%M} {} {:>6}".format(date_time, description, temp)
#     return "\r\n".join(map(__fmt,forecast))
