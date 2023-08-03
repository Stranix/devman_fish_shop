import logging

from config.settings import settings
from utils import generate_elastic_token, get_products_in_catalog

logger = logging.getLogger('fish_bot')


def main():
    logger.info('Запуск приложения')
    token, expire_in = generate_elastic_token()
    products = get_products_in_catalog(token)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(level=settings.log_level)
    try:
        main()
    except KeyboardInterrupt:
        logger.warning('Работа скрипта прервана')
    except Exception as error:
        logger.exception(error)
