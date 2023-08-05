import logging

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

import src.api.elasticpath as shop_api

logger = logging.getLogger('fish_bot')

sales_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('➕ 1 кг', callback_data=1),
            InlineKeyboardButton('➕ 5 кг', callback_data=5),
            InlineKeyboardButton('➕ 10 кг', callback_data=10),
        ],
        [InlineKeyboardButton('◀️Назад', callback_data='menu')],
    ]
)


def get_products_keyboard(token):
    logger.info('Создаю клавиатуру товаров')
    products = shop_api.get_products_in_catalog(token)
    keyboard_buttons = []

    for product in products:
        product_id = product['id']
        product_name = product['attributes']['name']

        inline_button = InlineKeyboardButton(
            product_name,
            callback_data=product_id
        )
        keyboard_buttons.append(inline_button)

    keyboard = [keyboard_buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    logger.info('Клавиатура создана')
    return reply_markup
