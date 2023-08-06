# FishShop bot

**FishShop bot** - это telegram чат-бот для торговли рыбой (и другими морепродуктами).

## Пример бота
Доступен по ссылке в Телеграм: [🐟 Store](https://t.me/stranix_dev_bot)

![fish-shop.gif](assets/fish-shop.gif)

## Переменные окружения

Часть настроек проекта берётся из переменных окружения.

Доступные переменные:
- `ELASTIC_BASE_UR`:`str` - основной адрес для работы с `api elasticpath`. Значение по умолчанию: https://useast.api.elasticpath.com
- `ELASTIC_STORE_ID`: `str` - обязательный параметр. `ID`  магазина в `elasticpath.com`, выдается при регистрации [elasticpath.com](https://elasticpath.com)
- `ELASTIC_CLIENT_ID`: `str` - обязательный параметр. `ID` клиента для работы с CMS [инструкция тут](https://elasticpath.dev/docs/authentication/application-keys/application-keys-cm)
- `ELASTIC_SECRET_KEY`: `str` - обязательный параметр. Секретный ключ для работы с CMS [инструкция тут](https://elasticpath.dev/docs/authentication/application-keys/application-keys-cm)
- `TG_BOT_TOKEN`: `str` - обязательный параметр. `API`-ключ для работы с Telegram-ботом. Как получить описано [тут](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram.html)
- `REDIS_DSN`: `str` - обязательный параметр. Строка для подключения к серверу [Redis](https://redis.io/). 
- `LOG_LEVEL`: `str` - уровень логирования. Возможные значение `DEBUG`,`INFO`, `ERROR`. По умолчанию `INFO`.

## Запуск
- Рекомендуется использовать виртуальное окружение для запуска проекта
- Для корректной работы Вам необходим Python версии 3.10 и выше
- В системе для запуска должен быть установлен [Poetry](https://python-poetry.org/)

- Скачайте код 
```bash 
git clone https://github.com/Stranix/devman_fish_shop
```
- Установите зависимости командой
```bash
poetry install
```
**Перед первым запуском необходимо выполнить все настройки в [elasticpath.com](https://elasticpath.com):**
1. [x] Создать товары
2. [x] Создать каталог
3. [x] Создать иерархию
4. [x] Создать прайсбук
5. [x] В прайсбук добавить товары 
6. [x] В иерархии подцепить товары к категориям
7. [x] В каталоге указать иерархию с товарами
8. [x] В меню каталога, напротив каталога (справа 3 точки) - опубликовать каталог


- Для запуска Telegram-бота необходимо выполнить команду:
```bash
python3 main.py
```
**Проект находится на стадии MVP**
## Цели проекта
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).