import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
    return "ECHO"


def echo(update, context):
    users_reply = update.message.text
    update.message.reply_text(users_reply)
    return "ECHO"


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
        'ECHO': echo
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(chat_id, next_state)
