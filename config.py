import os


class Settings:
    API_KEY = os.getenv("API_KEY")
    PASSWORD = os.getenv("PASSWORD")
    USER = os.getenv("USER")
    EMAIL = os.getenv("EMAIL")


cfg = Settings()
