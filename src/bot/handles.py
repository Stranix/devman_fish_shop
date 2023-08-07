import logging

from telegram import Update
from telegram.ext import CallbackContext

import src.api.elasticpath as shop_api

from src.bot.keyboards import get_products_keyboard
from src.bot.keyboards import get_sales_keyboard
from src.bot.keyboards import get_cart_keyboard

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

    product = shop_api.get_product_by_id_with_currencies(
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
    context.bot.delete_message(
        chat_id=callback_query.message.chat_id,
        message_id=callback_query.message.message_id
    )
    context.bot.send_photo(
        chat_id=callback_query.message.chat_id,
        photo=product_photo,
        caption=product_card_msg,
        reply_markup=get_sales_keyboard(callback_query.data)
    )
    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    callback_query = update.callback_query
    token = context.bot_data['shop_token']

    if callback_query.data in ['menu', 'cart']:
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=callback_query.message.message_id,
        )

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
    cart_id = update.effective_chat.id

    if callback_query.data == 'cart':
        cart_products = shop_api.get_cart_items(token, cart_id)
        cart_message = ''
        for product in cart_products['data']:
            cart_message += f"""Корзина:
            {product['name']}
            {product['description']}
            ${product['unit_price']['amount'] / 100} per kg
            сколько в корзине и цена за все
            {product['quantity']}kg in cart for ${product['value']['amount'] / 100}
                
            """
        cart_total_price = cart_products['meta']['display_price']['with_tax'][
            'formatted']
        cart_message += f'Total: {cart_total_price}'
        context.bot.send_message(
            chat_id=cart_id,
            text=cart_message,
            reply_markup=get_cart_keyboard(cart_products)
        )
        return 'HANDLE_CART'

    product_id, product_quantity = callback_query.data.split("_")

    shop_api.add_product_to_cart(token, cart_id, product_id, product_quantity)
    callback_query.answer(
        text=f'Добавили в корзину {product_quantity} кг',
        show_alert=True
    )
    return 'HANDLE_DESCRIPTION'


def handle_cart(update, context):
    callback_query = update.callback_query
    token = context.bot_data['shop_token']

    if callback_query.data in ['menu', 'check_out']:
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=callback_query.message.message_id,
        )

    if callback_query.data == 'menu':
        reply_markup = get_products_keyboard(token)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Выберите товар:',
            reply_markup=reply_markup
        )
        return 'HANDLE_MENU'

    if callback_query.data == 'check_out':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Пришлите ваш E-Mail',
        )
        return 'WAITING_EMAIL'

    shop_api.delete_cart_item(
        token,
        update.effective_chat.id,
        callback_query.data
    )
    update.callback_query.data = 'cart'
    return handle_description(update, context)


def waiting_email(update, context):
    email = update.message.text
    token = context.bot_data['shop_token']
    shop_api.create_customer(token, email)
    update.message.reply_text(
        f'Благодарим за заказ! Мы свяжемся с вами по email {email}. \n'
        f'Для запуска меню используйте команду /start '
    )
    return 'START'


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
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(chat_id, next_state)
