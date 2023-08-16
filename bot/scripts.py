import asyncio
from typing import Iterable

from bot.config import CONFIG, SERVICES, SERVICES_TOML
from bot.input import PROXIES
from bot.logger import logger
from bot.nansen import NansenAPI, solve_nansen_captcha, search_verification_link
from bot.imap_client import CustomIMAPClientSSL
from bot.http_client import CustomClientSession
from bot.anticaptcha import AntiCaptchaError
from bot.process import process_accounts_with_session
from bot.utils import curry_async, open_file
from bot.output import save_completed, completed


async def _join_waitlist(session: CustomClientSession, account: tuple[str, str], invite_code: str):
    """
    1. Попытка логина почты
    2. Попытка регистрации почты в waitlist nansen
    3. Получение ссылки для верификации с почты
    4. Верификация почты посредством перехода по ссылке
    5. Если нет ссылки на верификацию, то получаем csfr токен и отправляем письмо снова
    6. Повторная попытка верификации почты
    """
    email, password = account

    if session.proxy:
        account_info = f"{session.proxy} [{email}]"
    else:
        account_info = f"[{email}]"

    domain = "@" + email.split("@")[1]
    service = next((service_ for service_ in SERVICES if domain in service_.domains), None)

    if service is None:
        logger.error(f"{account_info} Unknown domain. You can add new domains here: {SERVICES_TOML}")
        if CONFIG.AUTOOPEN:
            open_file(SERVICES_TOML)
        return

    async with CustomIMAPClientSSL(service.host) as imap_client:
        await imap_client.login(email, password)

        logger.info(f"{account_info} Solving captcha...")
        try:
            g_captcha_response = await solve_nansen_captcha()
        except AntiCaptchaError as e:
            logger.error(f"{account_info} Failed to solve captcha: {e}")
            return

        nansen = NansenAPI(session)
        logger.info(f"{account_info} Registering...")
        await nansen.init_register(email, invite_code, g_captcha_response)
        logger.info(f"{account_info} Waiting for verification link...")
        tries = 1
        verification_link = None
        while verification_link is None and tries <= CONFIG.RETRIES:
            await asyncio.sleep(10)
            folder_to_messages = await imap_client.get_messages_from_folders(service.folders)
            for folder, messages in folder_to_messages.items():
                logger.info(f"{account_info} (attempt {tries}) Searching into \"{folder}\"...")
                for message in messages:
                    verification_link = search_verification_link(message)
                    if verification_link:
                        logger.debug(f"{account_info} v. link: {verification_link}")
            tries += 1
        if not verification_link:
            logger.warning(f"{account_info} Failed to find verification link. Resending verification message...")
            csrf_token = await nansen.request_csrf_token(email)
            if csrf_token is None:
                logger.error(f"{account_info} Failed to obtain csrf_token")
                return
            await nansen.resend_verification_message(email, csrf_token)
            verification_link = await imap_client.receive_verification_link(service.folders, CONFIG.RETRIES)
        await nansen.verify_account(verification_link)
        completed.add(f"{email}:{password}")
        save_completed()
        logger.success(f"{account_info} Successful registration!")


async def join_waitlist(invite_link_or_code: str, accounts_data: Iterable):
    invite_code = invite_link_or_code
    if "https://" in invite_link_or_code:
        invite_code = invite_link_or_code.split("=")[-1]

    join_waitlist_with_invite_code = await curry_async(_join_waitlist)(invite_code=invite_code)

    accounts = [account_data.split(':') for account_data in accounts_data]
    await process_accounts_with_session(accounts, PROXIES, join_waitlist_with_invite_code)
