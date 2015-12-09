# -*- coding: utf-8 -*-
# Copyright (C) 2015, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import lxml.html

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Smoove', 'SmooveStation']

# Each station is formatted as:
# newmark_01(
#    28,
#    45.770958,
#    3.073871,
#    "<div class=\"mapbal\" align=\"left\">022 Jaurès<br>Vélos disponibles: 4<br>Emplacements libres: 10<br>CB: Non<br></div>");
# I.e., (station_id, latitude, longitude, status_html)
# status_html contains name, available_bikes, free_bike_stands, credit_card_enabled (discarded afterwards)
DATA_RGX = r'\(\d+\,\ (\d+.\d+).*?(\d+.\d+)\,\ "(.*?)"\)'
STATUS_RGX = r'.*?\:\ (\d+)'

class Smoove(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Smoove',
        'company': 'Smoove'
    }

    def __init__(self, tag, feed_url, meta):
        super(Smoove, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        
        html = scraper.request(self.feed_url)
        stations_data = re.findall(DATA_RGX, html)

        stations = []
        for station_data in stations_data:
            latitude, longitude, status_raw_html = station_data
            status_html = lxml.html.fromstring(status_raw_html)
            # discards the last element of stations_data
            # which indicates if the station is credit card-enabled
            name, raw_bikes, raw_free = status_html.xpath('text()')[:-1]
            free = int(re.findall(STATUS_RGX, raw_free)[0])
            bikes = int(re.findall(STATUS_RGX, raw_bikes)[0])
            station = BikeShareStation(name, float(latitude), float(longitude),
                                    int(bikes), int(free))
            stations.append(station)
        self.stations = stations