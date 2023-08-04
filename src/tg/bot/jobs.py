import logging

from telegram.ext import CallbackContext

from src.api.elasticpath import generate_elastic_token

logger = logging.getLogger('fish_bot')


def regenerate_shop_token(context: CallbackContext):
    logger.debug('Срок действия токена истек. Перезаписываем')
    shop_token, _ = generate_elastic_token()
    context.bot_data['shop_token'] = shop_token
