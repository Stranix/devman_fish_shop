import logging

logger = logging.getLogger('fish_bot')


def main():
    logger.info('Запуск приложения')
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(level=logging.DEBUG)
    try:
        main()
    except KeyboardInterrupt:
        logger.warning('Работа скрипта прервана')
    except Exception as error:
        logger.exception(error)
