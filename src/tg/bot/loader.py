import redis
from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
)

from config.settings import settings
from src.tg.bot.handles import handle_users_reply


def start_tg_bot():
    updater = Updater(settings.tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['db'] = redis.Redis.from_url(str(settings.redis_dsn))
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
