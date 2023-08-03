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
