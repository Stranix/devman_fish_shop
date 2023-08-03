import logging
import sys

from pydantic_core import ValidationError
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

logger = logging.getLogger('fish_bot')


class Settings(BaseSettings):
    elastic_base_url: str = 'https://useast.api.elasticpath.com'
    elastic_store_id: str
    elastic_client_id: str
    elastic_secret_key: str
    tg_bot_token: str = ''
    tg_admin_chat_id: int = 0
    log_level: str = logging.INFO

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


try:
    settings = Settings()
except ValidationError as exc:
    logger.critical('Заданы не все обязательные настройки')
    logger.critical(exc.json())
    sys.exit()

