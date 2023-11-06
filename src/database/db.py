import psycopg2
from config import cfg


class Database:
    def __init__(self, dbname, user, password, host):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        self.cur = self.conn.cursor()

    def query(self, query):
        with self.conn.cursor() as curs:
            curs.execute(query)


db = Database(cfg.DB_NAME, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_HOST)
