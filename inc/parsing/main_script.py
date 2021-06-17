import requests
from bs4 import BeautifulSoup

from exception.exception import ServerError, HTMLError, SortingError

from .config_for_script import HOST, URL, HEADERS
from .case_video import CASE_NVIDIA




def get_html(url, params=None):

    ''' Получение данных с сайта в виде Html кода '''

    html = requests.get(url, headers=HEADERS, params=params)
    return html


def get_content(html):

    ''' Поиск контента на сайте '''

    try:

        # В данном случае: Поиск проходит по сайту 'https://www.citilink.ru'
        # А именно в теги '<div class="product_data__gtm-js ..."..>'
        # В даном теге содержиться информация об отдельных видеокартах

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='product_data__gtm-js')

    except Exception:
        raise HTMLError('На сайте изменился HTML или CSS у карты товара')

    card = []

    try:

        # В этом блоке кода данные получинаые с сайта а именно
        # Название, Ссылка, Цена достаются и складыватся в словарь
        # Который потом помещается в словарь для более удобной работы

        for item in items:
            if item.find('a', class_='ProductCardHorizontal__title') != None:
                card_title = item.find('a', class_='ProductCardHorizontal__title').get_text()
                card_link = HOST + item.find('a', class_='ProductCardHorizontal__title').get('href'),
            if item.find('span', class_='_current-price') != None:
                card_price = item.find('span', class_='_current-price').get_text().strip() + ' руб'
            card.append({
                'Название:': card_title,
                'Ссылка:': card_link,
                'Цена:': card_price,
            })

    except ValueError:
        raise HTMLError('На сайте изменился HTML или CSS у отдельных элементов в карте товара')

    return card

def start_parsing():

    ''' Функция для начала парсинга '''

    try:
        html = get_html(URL)
    except ServerError:
        raise ServerError('Некоректно введен URL')

    if html.status_code == 200:
        card = get_content(html.text)
        return card
    raise ServerError('Ошибка подключения на сайт "status_code > 200"')

def get_card(bot_message):

    ''' Функция для сортировки и отпраки информации пользователю'''

    if bot_message == 'all':

        cards = start_parsing()
        cart = []

        try:
            for card in cards:
                cart.append(card)
        except Exception:
            raise SortingError('Что то пошло не так, ошибка сортировки, повторите попытку позже...')

        return cart

    cards = start_parsing()
    cart = []

    try:

        # Данный блок служит для сортировки информации
        # В "bot_message" помещается чипсет видеокарты для
        # дольнейшего поиска в списке
        # Далее он помещается в другой список, который уже отпровляется пользователю

        for card in cards:
            if bot_message in card['Название:']:
                cart.append(card)

    except Exception:
        raise SortingError('Что то пошло не так, ошибка сортировки, повторите попытку позже...')

    return cart


if __name__ == '__main__':

    ''' Проверка коректной работы скрипта '''

    while True:
        question = int(input('1 - Показать список всех видео карт \n 2 - Показать отдельные видео карты'))

        if question == 1:
            card = start_parsing()
            for i in card:
                print(i)

        elif question == 2:
            print(i for i in CASE_NVIDIA.keys())
            question_2 = int(input('Какая модель нужна?'))
            if question_2 not in CASE_NVIDIA.keys():
                raise ValueError('Пошел нахуй ебень...')
            print(get_card(question_2))

        else:
            print('Что-то пошло не так..')
            continue
