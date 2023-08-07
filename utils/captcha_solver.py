import asyncio
from utils.get_config_data import *
from logger.logger import logger
from capmonster_python import RecaptchaV2Task
from capmonster_python import HCaptchaTask
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask


def _get_captcha_key():
    logger.info('Решаю капчу...')
    if capmonster_apikey != '':
        capmonster = None
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
    elif anticaptcha_apikey != '':
        anticaptcha_client = AnticaptchaClient(anticaptcha_apikey)
        task = NoCaptchaTaskProxylessTask(website_url=site_url, website_key=captcha_site_key)
        job = anticaptcha_client.createTask(task)
        job.join()
        result = job.get_solution_response()
        if result:
            logger.debug("Получил ключ капчи.")
            return result



async def get_captcha_key():
    return await asyncio.to_thread(_get_captcha_key)
