import time
import schedule

from main import run_collector

if __name__ == "__main__":
    schedule.every().day.at("00:00").do(run_collector())

    while True:
        schedule.run_pending()
        time.sleep(1)
