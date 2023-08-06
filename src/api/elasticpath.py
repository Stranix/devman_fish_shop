import logging
import urllib.parse

import requests

from config.settings import settings

logger = logging.getLogger('fish_bot')


def generate_elastic_token() -> tuple:
    logger.info('Запрос токена')
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        '/oauth/access_token'
    )
    data = {
        'client_id': settings.elastic_client_id,
        'client_secret': settings.elastic_secret_key,
        'grant_type': 'client_credentials',
    }
    logger.debug('url: %s', url)
    logger.debug('data: %s', data)

    response = requests.post(url, data=data)
    response.raise_for_status()

    token_access = response.json()['access_token']
    token_expire_in = response.json()['expires_in']
    logger.info('Токен получен')
    logger.debug(
        'access_token: %s, expires_in: %s',
        token_access,
        token_expire_in
    )
    return token_access, token_expire_in


def get_products_in_catalog(token):
    logger.info('Получаем список всех продуктов')
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        '/pcm/products/'
    )
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'EP-Channel': 'web store'
    }
    logger.debug('url: %s', url)
    logger.debug('headers: %s', headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    products = response.json()['data']
    logger.debug('products: %s', products)
    logger.info('Продукты получены')
    return products


def get_price_books(token):
    logger.info('Получаем доступные ценовые книги')
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        '/pcm/pricebooks/'
    )
    headers = {
        'Authorization': f'Bearer {token}',
    }
    logger.debug('url: %s', url)
    logger.debug('headers: %s', headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    price_books = response.json()['data']
    logger.debug('price_books: %s', price_books)
    logger.info('Ценовые книги получены')
    return price_books


def get_price_book_by_name(token, price_book_name='Default'):
    logger.info('Ищу ценовую книгу по имени %s', price_book_name)
    for price_book in get_price_books(token):
        logger.debug('Поиск в price_book: %s', price_book)
        if price_book['attributes']['name'] == price_book_name:
            logger.info('Ценовая книга найдена')
            return price_book


def get_price_book_by_id(token, price_book_id):
    logger.info('Получаю данные ценовой книги с id %s', price_book_id)
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        f'/pcm/pricebooks/{price_book_id}'
    )
    headers = {
        'Authorization': f'Bearer {token}',
    }
    params = {
        'include': 'prices'
    }
    logger.debug('url: %s', url)
    logger.debug('params: %s', params)
    logger.debug('headers: %s', headers)

    response = requests.get(url, headers=headers, params=params)
    logger.debug('response url: %s', response.url)
    response.raise_for_status()

    price_book = response.json()
    logger.debug('price_book: %s', price_book)
    logger.info('Данные ценовой книги получены')
    return price_book


def get_product_currencies_in_book_price(
        token,
        product_sku,
        price_book_name='Default'
):
    logger.info('Ищу цены продукта в ценовой книге')
    logger.debug('product_sku: %s', product_sku)
    price_book_id = get_price_book_by_name(token, price_book_name).get('id')

    if not price_book_id:
        logger.error('Не найдена ценовая книга с именем %s', price_book_name)
        return

    price_book = get_price_book_by_id(token, price_book_id)
    for product in price_book.get('included', []):
        if product_sku == product['attributes']['sku']:
            currencies = product['attributes']['currencies']
            logger.debug('currencies: %s', currencies)
            logger.info('Цены найдены')
            return currencies


def get_product_by_id(token, product_id):
    logger.info('Получаем информацию о продукте с id: %s', product_id)
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        f'/pcm/products/{product_id}'
    )
    headers = {
        'Authorization': f'Bearer {token}',
    }
    logger.debug('url: %s', url)
    logger.debug('headers: %s', headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    product = response.json()['data']
    logger.debug('products: %s', product)
    logger.info('Продукты получены')
    return product


def get_product_dy_id_with_currencies(
        token,
        product_id,
        price_book_name='Default'
):
    logger.info('Получение информации о продукте с ценой')
    product = get_product_by_id(token, product_id)
    product_sku = product['attributes']['sku']
    product_currencies = get_product_currencies_in_book_price(
        token,
        product_sku,
        price_book_name
    )
    if not product_currencies:
        logger.warning('Не нашел подходящих цен для продукта')
    product.update({'currencies': product_currencies})
    logger.debug('product_with_currencies: %s', product)
    logger.info('Данные о продукте получены')
    return product


def get_product_quantity_in_stock(token, product_id):
    logger.info('Получаем остаток по продукту %s на складе', product_id)
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        f'/v2/inventories/{product_id}'
    )
    headers = {
        'Authorization': f'Bearer {token}',
    }
    logger.debug('url: %s', url)
    logger.debug('headers: %s', headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    product_quantity = response.json()['data']['available']
    logger.debug('product_quantity: %s', product_quantity)
    logger.info('Остатки по продукту получены')
    return product_quantity


def add_product_to_cart(token, cart_id, product_id, quantity):
    logger.info('Добавление продуктов в корзину')
    logger.debug(
        'cart_id: %s, product_id: %s, quantity: %s',
        cart_id,
        product_id,
        quantity
    )
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        f'/v2/carts/{cart_id}/items'
    )
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    payload = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': int(quantity),
        }
    }
    logger.debug('url: %s', url)
    logger.debug('headers: %s', headers)
    logger.debug('payload: %s', payload)

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    logger.info('Продукты добавлены.')
    product_in_cart = response.json()['data']
    logger.debug('product_in_cart: %s', product_in_cart)
    return product_in_cart


def get_cart_items(token, cart_id):
    logger.info('Получение продуктов в корзине')
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        f'/v2/carts/{cart_id}/items'
    )
    headers = {
        'Authorization': f'Bearer {token}',
    }
    logger.debug('url: %s', url)
    logger.debug('headers: %s', headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_items = response.json()['data']
    logger.debug('cart_items: %s', cart_items)
    logger.info('Продукты в корзине получены')

    return cart_items


def get_product_image_url(token, product_image_id):
    logger.info('Получаю url изображение продукта')
    url = urllib.parse.urljoin(
        settings.elastic_base_url,
        f'/v2/files/{product_image_id}'
    )
    headers = {
        'Authorization': f'Bearer {token}',
    }
    logger.debug('url: %s', url)
    logger.debug('headers: %s', headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    product_image_link = response.json()['data']['link']['href']
    logger.debug('product_image_link: %s', product_image_link)
    logger.info('url изображения получен')
    return product_image_link


def downloads_file(url):
    logger.info('Загружаю файл по ссылке')
    logger.debug('url: %s', url)
    response = requests.get(url)
    response.raise_for_status()
    logger.info('Файл получен')
    return response.content
