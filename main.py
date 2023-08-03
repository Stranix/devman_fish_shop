import logging

import requests.exceptions

from config.settings import settings

from utils import generate_elastic_token, get_products_in_catalog, \
    add_product_to_cart, get_cart_items

logger = logging.getLogger('fish_bot')


def main():
    try:
        logger.info('Запуск приложения')
        token, expire_in = generate_elastic_token()
        products = get_products_in_catalog(token)
        product_id = products[0]['id']
        cat_id = '123132dfsdf'
        add_product_to_cart(token, cat_id, product_id, 1)
        get_cart_items(token, cat_id)
    except requests.exceptions.HTTPError as error:
        logger.error('ошибка добавления %s', error.response.json())


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(level=settings.log_level)
    try:
        main()
    except KeyboardInterrupt:
        logger.warning('Работа скрипта прервана')
    except Exception as error:
        logger.exception(error)
