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
from src.tg.bot.jobs import regenerate_shop_token
from src.api.elasticpath import generate_elastic_token


def start_tg_bot():
    shop_token, shop_token_exp_period = generate_elastic_token()

    updater = Updater(settings.tg_bot_token)
    updater.job_queue.run_repeating(
        regenerate_shop_token,
        interval=shop_token_exp_period
    )

    dispatcher = updater.dispatcher
    dispatcher.bot_data['db'] = redis.Redis.from_url(str(settings.redis_dsn))
    dispatcher.bot_data['shop_token'] = shop_token

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()
