import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

import src.api.elasticpath as shop_api
from src.tg.bot.utils import get_products_keyboard

logger = logging.getLogger('fish_bot')


def start(update, context):
    user = update.effective_user
    token = context.bot_data['shop_token']
    reply_markup = get_products_keyboard(token)
    update.message.reply_markdown_v2(
        text=f'Привет, {user.mention_markdown_v2()}\!\nХотите заказать рыбки?',
        reply_markup=reply_markup
    )
    return 'HANDLE_MENU'


def handle_menu(update: Update, context: CallbackContext):
    callback_query = update.callback_query
    token = context.bot_data['shop_token']
    logger.debug('callback_query: %s', callback_query)

    product = shop_api.get_product_dy_id_with_currencies(
        token,
        callback_query.data
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
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Назад", callback_data="menu")]
        ]
    )
    context.bot.delete_message(
        chat_id=callback_query.message.chat_id,
        message_id=callback_query.message.message_id
    )
    context.bot.send_photo(
        chat_id=callback_query.message.chat_id,
        photo=product_photo,
        caption=product_card_msg,
        reply_markup=reply_markup
    )
    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    callback_query = update.callback_query
    token = context.bot_data['shop_token']

    if callback_query.data == 'menu':
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=callback_query.message.message_id,
        )

        reply_markup = get_products_keyboard(token)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Выберите товар:',
            reply_markup=reply_markup
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
        'HANDLE_DESCRIPTION': handle_description,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(chat_id, next_state)
