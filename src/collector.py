import logging
import time
from datetime import datetime, timedelta

import requests
import pandas as pd
from pathlib import Path
from prettytable import PrettyTable

from src.utils import get_headers

logging.basicConfig(level=logging.DEBUG,  # Устанавливаем уровень логирования
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат вывода сообщений
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger("updater")


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


class Collector:
    def __init__(self, networks, min_buyin=3, max_buyin=1300):
        self.networks = networks
        self.today_searches = self.get_today_searches()
        self.buyin_range = (min_buyin, max_buyin)

    @staticmethod
    def get_today_searches():
        try:
            resp = requests.get(f'https://www.sharkscope.com/api/maxev/playergroups', headers=get_headers())
            return int(resp.json()['Response']['UserInfo']['Subscriptions']['@totalSearchesRemaining'])
        except Exception as e:
            logger.error(e)
            return 0

    def update_data(self):
        for room in self.networks:
            if self.today_searches <= 0:
                logger.info('Searches is over today')
                break
            else:
                logger.info(f'{self.today_searches} searches remaining')
            self.update_network(room)

    def update_network(self, network):
        last_tour_time = self.get_last_tour_time(f'/home/dron/poker_data/{network}.csv')
        tour_list = self.get_completed_tournaments(last_tour_time, network)
        if tour_list and isinstance(tour_list, list):
            logger.info(f'From {network} received {len(tour_list)} tournaments')
            self.add_tournaments(tour_list, network)
        else:
            logger.warning(f'Data on new tournaments cannot be retrieved from {network}.')

    def get_completed_tournaments(self, begin_time, network):
        try:
            exclude = ['SAT', 'HU']
            if network == 'Winamax.fr':
                exclude.pop(0)
            if not begin_time:
                begin_time = int((datetime.now() - timedelta(days=32)).timestamp())
            url = f'https://www.sharkscope.com/api/maxev/networks/{network}/tournaments?' \
                  f'Filter=Class:SCHEDULED;StakePlusRake:USD{self.buyin_range[0]}~{self.buyin_range[1]};Type:H,NL;' \
                  f'Type!:{",".join(exclude)};' \
                  f'Date:{begin_time}~{int(time.time())}&Order=Last,{1}~{self.today_searches * 10}'
            resp = requests.get(url, headers=get_headers())
            res = resp.json()
            self.today_searches = int(res['Response']['UserInfo']['Subscriptions']['@totalSearchesRemaining'])
            return res['Response']['CompletedTournamentsResponse']['CompletedTournaments']['CompletedTournament']
        except Exception as e:
            logger.error(e)

    @staticmethod
    def add_tournaments(tour_list, network):
        new_tournaments = pd.DataFrame([prepare_tour(t) for t in tour_list])
        new_tournaments['timestamp'] = new_tournaments['@date']
        new_tournaments['@date'] = pd.to_datetime(new_tournaments['@date'], unit='s')
        new_tournaments['weekDay'] = new_tournaments['@date'].dt.day_name()
        full_path = Path(f'/home/dron/poker_data/{network}.csv')
        if full_path.is_file():
            old_data = pd.read_csv(full_path)
            updated_data = pd.concat([old_data, new_tournaments], ignore_index=True)
            updated_data.to_csv(full_path, index=False)
        else:
            new_tournaments.to_csv(full_path, index=False)

    @staticmethod
    def get_last_tour_time(filename):
        try:
            df = pd.read_csv(filename)
            return df['timestamp'].max()
        except Exception as e:
            logger.error(f'Cannot to recieve max time {e}')
            return None

    def stat(self):
        table = PrettyTable()
        table.field_names = ['from', 'to', 'count', 'network']
        for network in self.networks:
            row = self.get_network_stat(f'/home/dron/poker_data/{network}.csv', network)
            table.add_row(row)

        print(table)

    @staticmethod
    def get_network_stat(filename, network):
        try:
            df = pd.read_csv(filename)
            return [df["@date"].min(), df["@date"].max(), df.count()[0], network]
        except Exception as e:
            logger.error(e)
            return [f'{network} has no data']
