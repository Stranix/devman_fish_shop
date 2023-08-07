import logging

import requests.exceptions

from config.settings import settings
from src.bot.loader import start_tg_bot

logger = logging.getLogger('fish_bot')


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(level=settings.log_level)
    try:
        start_tg_bot()
    except KeyboardInterrupt:
        logger.warning('Работа скрипта прервана')
    except requests.exceptions.HTTPError as error:
        logger.exception(error)
    except Exception as error:
        logger.exception(error)
