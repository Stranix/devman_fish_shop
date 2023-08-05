import logging

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

import src.api.elasticpath as shop_api

logger = logging.getLogger('fish_bot')


def get_products_keyboard(token):
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
    return reply_markup
