from config import cfg
import hashlib


def get_headers():
    enc_pass = hashlib.md5(cfg.PASSWORD.encode('utf-8')).hexdigest()
    key = enc_pass + cfg.API_KEY
    hash_api = hashlib.md5(key.encode('utf-8')).hexdigest()

    return {
        'Accept': 'application/json',
        'Username': cfg.EMAIL,
        'Password': hash_api,
        'User-Agent': 'Mozzila'
    }


def get_statistics_headers():

    return {
        'Accept': 'application/json',
        'Username': 'maxevteam@gmail.com',
        'Login': 'maxevteam@gmail.com~,~a9b7f1ea8c3ce86e709f45719f8eea3f',
        'Password': 'a9b7f1ea8c3ce86e709f45719f8eea3f',
        'User-Agent': 'Mozzila'
    }


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

