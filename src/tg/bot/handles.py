import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger('fish_bot')


def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2')
        ],
        [
            InlineKeyboardButton("Option 3", callback_data='3')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Привет!', reply_markup=reply_markup)
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

    print(user_state)
    states_functions = {
        'START': start,
        'ECHO': echo
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(chat_id, next_state)
