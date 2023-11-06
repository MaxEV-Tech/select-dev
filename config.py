from decouple import config


class Settings:
    # API
    API_KEY = config("API_KEY")
    API_PASSWORD = config("API_PASSWORD")
    API_USER = config("API_USER")
    API_EMAIL = config("API_EMAIL")
    # DB
    DB_NAME = config("DB_NAME")
    DB_USER = config("DB_USER")
    DB_PASSWORD = config("DB_PASSWORD")
    DB_HOST = config("DB_HOST")


cfg = Settings()
