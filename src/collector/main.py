import requests

from src.collector.collector import Collector
from src.utils import get_headers


def get_sharkscope_data(networks, min_buyin, max_buyin, offset, count):
    url = f'https://www.sharkscope.com/api/maxev/networks/{",".join(networks)}/tournaments?' \
          f'Filter=Class:SCHEDULED;StakePlusRake:USD{min_buyin}~{max_buyin};Type:H,NL;Type!:SAT,HU&Order=Last,{offset}~{offset + count}'
    resp = requests.get(url, headers=get_headers())
    print(resp.text)

    return resp.json()


networks = ['GGNetwork', '888Poker', 'Chico', 'iPoker', 'PartyPoker', 'PokerStars', 'Revolution', 'SkyPoker', 'WPN',
            'PokerStars(FR-ES-PT)', 'Winamax.fr']


def run_collector():
    coll = Collector(['Winamax.fr', 'PokerStars', 'PokerStars(FR-ES-PT)', 'GGNetwork'])
    coll.update_data()
    coll.stat()


if __name__ == "__main__":
    run_collector()
