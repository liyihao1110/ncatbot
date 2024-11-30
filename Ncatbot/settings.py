# _*_ coding:utf-8 _*_
# https://github.com/gaojj2000


class Settings:
    def __init__(self):
        self.max_ids: int = 100
        self.port_or_http: (int, str) = None


settings = Settings()
