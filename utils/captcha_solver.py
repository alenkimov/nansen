import asyncio
from utils.get_config_data import *
from logger.logger import logger
from capmonster_python import RecaptchaV2Task
from capmonster_python import HCaptchaTask


def _get_captcha_key():
    capmonster = None
    logger.info('Решаю капчу...')
    if captcha_type == 'recaptcha':
        capmonster = RecaptchaV2Task(capmonster_apikey)
    elif captcha_type == 'hcaptcha':
        capmonster = HCaptchaTask(capmonster_apikey)
    if capmonster:
        task_id = capmonster.create_task(site_url, captcha_site_key)
        result = capmonster.join_task_result(task_id)
        if result.get('gRecaptchaResponse'):
            logger.debug("Получил ключ капчи.")
            return result.get('gRecaptchaResponse')

async def get_captcha_key():
    return await asyncio.to_thread(_get_captcha_key)
