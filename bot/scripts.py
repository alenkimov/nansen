import asyncio
from typing import Iterable

from bot.config import CONFIG, SERVICES, SERVICES_TOML
from bot.input import PROXIES
from bot.logger import logger
from bot.nansen import NansenAPI, solve_nansen_captcha, search_verification_link
from bot.imap_client import CustomIMAPClient
from bot.http_client import CustomClientSession
from bot.anticaptcha import AntiCaptchaError
from bot.process import process_accounts_with_session
from bot.utils import curry_async, open_file
from bot.output import save_completed, completed


async def _join_waitlist(session: CustomClientSession, account: tuple[str, str], invite_code: str):
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

    try:
        async with CustomIMAPClient(service.host, proxy=session.proxy) as imap_client:
            await imap_client.login(email, password)
            nansen = NansenAPI(session)

            async def search_verification_link_in_inbox(tries: int = 1, sleep_time: int = 0) -> str or None:
                verification_link = None
                logger.debug(f"{account_info} Checking email inbox...")
                while verification_link is None and tries <= CONFIG.RETRIES:
                    await asyncio.sleep(sleep_time)
                    folder_to_messages = await imap_client.get_messages_from_folders(service.folders)
                    for folder, messages in folder_to_messages.items():
                        logger.debug(f"{account_info} (attempt {tries}) Searching into \"{folder}\"...")
                        for message in messages:
                            verification_link = search_verification_link(message)
                            if verification_link:
                                logger.debug(f"{account_info} v. link: {verification_link}")
                                return verification_link
                    tries += 1
                return None

            verification_link = await search_verification_link_in_inbox()
            if verification_link is None:
                logger.debug(f"{account_info} Solving captcha...")
                try:
                    g_captcha_response = await solve_nansen_captcha()
                except AntiCaptchaError as e:
                    logger.error(f"{account_info} Failed to solve captcha: {e}")
                    return

                await nansen.join_waitlist(email, invite_code, g_captcha_response)
                verification_link = await search_verification_link_in_inbox(CONFIG.RETRIES, sleep_time=10)
                if verification_link is None:
                    logger.error(f"{account_info} Failed to find the verification link in"
                                 f" the mailbox in {CONFIG.RETRIES * 10} secs. Try again later")
                    return

            await nansen.verify_email(verification_link)
            completed.add(f"{email}:{password}")
            save_completed()
            logger.success(f"{account_info} Joined the waitlist!")
    except TimeoutError:
        logger.error(f"{account_info} TimeoutError. Try again later")
        return


async def join_waitlist(invite_code: str, accounts_data: Iterable):
    if "https://" in invite_code:
        invite_code = invite_code.split("=")[-1]

    join_waitlist_with_invite_code = await curry_async(_join_waitlist)(invite_code=invite_code)

    accounts = [account_data.split(':') for account_data in accounts_data]
    await process_accounts_with_session(accounts, PROXIES, join_waitlist_with_invite_code)
