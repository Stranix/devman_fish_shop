import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

import src.api.elasticpath as shop_api

logger = logging.getLogger('fish_bot')


def start(update, context):
    user = update.effective_user
    token = context.bot_data['shop_token']
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
    update.message.reply_markdown_v2(
        text=f'Привет, {user.mention_markdown_v2()}\!\nХотите заказать рыбки?',
        reply_markup=reply_markup
    )
    return 'HANDLE_MENU'


def handle_menu(update: Update, context: CallbackContext):
    user_query = update.callback_query
    token = context.bot_data['shop_token']
    logger.debug('user_query: %s', user_query)

    context.user_data['product_id'] = user_query.data
    context.bot.delete_message(
        chat_id=user_query.message.chat_id,
        message_id=user_query.message.message_id
    )
    product = shop_api.get_product_dy_id_with_currencies(
        token,
        user_query.data
    )

    product_name = product['attributes']['name']
    product_price = product['currencies']['USD']['amount'] / 100
    product_description = product['attributes']['description']
    product_quantity_in_stock = shop_api.get_product_quantity_in_stock(
        token,
        product['id']
    )
    product_image_id = product['relationships']['main_image']['data']['id']
    product_photo_url = shop_api.get_product_image_url(
        token,
        product_image_id
    )
    product_photo = shop_api.downloads_file(product_photo_url)

    product_card_msg = f""" {product_name}
    
    ${product_price} per kg
    {product_quantity_in_stock} kg in stock
    
    {product_description}
    """
    context.bot.send_photo(
        chat_id=user_query.message.chat_id,
        photo=product_photo,
        caption=product_card_msg
    )
    return 'HANDLE_MENU'


def handle_users_reply(update, context):
    db = context.bot_data['db']
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    logger.debug('user_state: %s', user_state)
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(chat_id, next_state)
