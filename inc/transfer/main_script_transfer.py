
import requests
import json

from exception.exception import ConvertionExceprion
from collections import defaultdict

class UserInfo:

    ''' Кеш пользователя '''

    def __init__(self):
        self.f = "RUB"
        self.t = "USD"

class UserDB:

    ''' База даных для пользователий '''

    def __init__(self):
        self.db = defaultdict(UserInfo)

    def change_from(self, user_id, val):
        self.db[user_id].f = val

    def change_too(self, user_id, val):
        self.db[user_id].t = val

    def get_pair(self, user_id):
        user = self.db[user_id]
        return user.f, user.t

class CryptoConverter:

    ''' Обработка исключений функции get_values '''

    @staticmethod
    def convert(values):
        if len(values) != 3:
            raise ConvertionExceprion('Слишком много параметров')
        quote, base, amount = values

        if quote == base:
            raise ConvertionExceprion(f'Невозможно перевести одинкаовые валюты {base}')

        quote_ticker = quote
        base_ticker = base

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertionExceprion(f'Не удалось обработать количество {amount}')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        total = float(json.loads(r.content)[base_ticker])*amount

        return round(total, 3)
