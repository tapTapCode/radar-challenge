import os


class Settings:
    def __init__(self) -> None:
        self.debug = os.getenv("DEBUG", "0") == "1"
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")


settings = Settings()

