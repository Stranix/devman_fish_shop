import logging

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

import src.api.elasticpath as shop_api

logger = logging.getLogger('fish_bot')


def get_sales_keyboard(product_id):
    logger.info('Создаю клавиатуру карточки товара')
    sales_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    '➕ 1 кг',
                    callback_data=f'{product_id}_1'
                ),
                InlineKeyboardButton(
                    '➕ 5 кг',
                    callback_data=f'{product_id}_5'
                ),
                InlineKeyboardButton(
                    '➕ 10 кг',
                    callback_data=f'{product_id}_10'
                ),
            ],
            [InlineKeyboardButton('🛒 КОРЗИНА', callback_data='cart')],
            [InlineKeyboardButton('◀️Назад', callback_data='menu')],
        ]
    )
    logger.info('Клавиатура создана')
    return sales_keyboard


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
    products_keyboard = InlineKeyboardMarkup(keyboard)
    logger.info('Клавиатура создана')
    return products_keyboard


def get_cart_keyboard(cart_products):
    logger.info('Создаю клавиатуру корзины')
    logger.debug('cart_products: %s', cart_products)
    keyboard_buttons = []
    for product in cart_products['data']:
        product_name = product['name']
        product_id = product['id']
        keyboard_buttons.append([
            InlineKeyboardButton(
                f'✖️Убрать из корзины {product_name}',
                callback_data=product_id
            )
        ])

    if cart_products['data']:
        keyboard_buttons.append([
            InlineKeyboardButton(
                '💳 ОПЛАТА',
                callback_data='check_out')
        ])

    keyboard_buttons.append([
        InlineKeyboardButton(
            '📄 В МЕНЮ',
            callback_data='menu')
    ])
    logger.info('Клавиатура создана')
    return InlineKeyboardMarkup(keyboard_buttons)
