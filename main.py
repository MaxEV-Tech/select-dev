import json
import requests

import pandas as pd

from src.collector import Collector
from src.utils import get_headers, get_statistics_headers
from config import cfg


def get_sharkscope_data(networks, min_buyin, max_buyin, offset, count):
    url = f'https://www.sharkscope.com/api/maxev/networks/{",".join(networks)}/tournaments?' \
          f'Filter=Class:SCHEDULED;StakePlusRake:USD{min_buyin}~{max_buyin};Type:H,NL;Type!:SAT,HU&Order=Last,{offset}~{offset + count}'
    resp = requests.get(url, headers=get_headers())
    print(resp.text)
    return resp.json()


networks = ['GGNetwork', '888Poker', 'Chico', 'iPoker', 'PartyPoker', 'PokerStars', 'Revolution', 'SkyPoker', 'WPN',
            'PokerStars(FR-ES-PT)', 'Winamax.fr']


coll = Collector(['Winamax.fr', 'PokerStars', 'PokerStars(FR-ES-PT)', 'GGNetwork'])
coll.update_data()
coll.stat()

from src.predictors.ability_predictor import AbilityPredictor


network = 'Winamax.fr'
df = pd.read_json('tmp.json')
ap = AbilityPredictor(network)
prediction = ap.predict(df)
print(prediction.columns)
prediction['buyin'] = prediction['@rake'] + prediction['@stake']
for buyin in sorted(prediction['buyin'].unique().tolist()):
    print(prediction[prediction['buyin'] == buyin])
print(prediction)



