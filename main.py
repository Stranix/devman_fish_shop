import logging

from config.settings import settings
from utils import generate_elastic_token

logger = logging.getLogger('fish_bot')


def main():
    logger.info('Запуск приложения')
    generate_elastic_token()


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(level=settings.log_level)
    try:
        main()
    except KeyboardInterrupt:
        logger.warning('Работа скрипта прервана')
    except Exception as error:
        logger.exception(error)
