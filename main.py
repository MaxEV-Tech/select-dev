import json
import requests

import pandas as pd

from src.collector import Collector
from src.utils import get_headers, get_statistics_headers
from config import cfg


#https://ru.sharkscope.com/poker-statistics/networks/PokerStars(FR-ES-PT)/tournaments?&Filter=Entrants:8~*;Type!:SAT,HU;Date:1667329200~1668193199;Class:SCHEDULED&Order=Last,1~10
def get_sharkscope_data(networks, min_buyin, max_buyin, offset, count):
    url = f'https://www.sharkscope.com/api/maxev/networks/{",".join(networks)}/tournaments?' \
          f'Filter=Class:SCHEDULED;StakePlusRake:USD{min_buyin}~{max_buyin};Type:H,NL;Type!:SAT,HU&Order=Last,{offset}~{offset + count}'
    resp = requests.get(url, headers=get_headers())
    print(resp.text)
    return resp.json()


def prepare_tour(tour):
    if 'Statistics' in tour:
        stat = tour['Statistics']
        if 'Statistic' in stat:
            stat = stat['Statistic']
            if type(stat) == list:
                for s in stat:
                    tour[s['@id']] = s['$']
            else:
                tour[stat['@id']] = stat['$']
        tour.pop('Statistics')
    return tour


networks = ['GGNetwork', '888Poker', 'Chico', 'iPoker', 'PartyPoker', 'PokerStars', 'Revolution', 'SkyPoker', 'WPN',
            'PokerStars(FR-ES-PT)', 'Winamax.fr']


coll = Collector(['Winamax.fr', 'PokerStars', 'PokerStars(FR-ES-PT)', 'GGNetwork'])
coll.update_data()
coll.stat()





