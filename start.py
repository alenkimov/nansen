import asyncio

import questionary

from bot.config import CONFIG
from bot.input import EMAILS, PROXIES
from bot.output import completed
from bot.paths import CONFIG_TOML, EMAILS_TXT
from bot.scripts import join_waitlist
from bot.author import TG_LINK
from bot.utils import open_file


async def main():
    print(f"Telegram channel: {TG_LINK}")
    if not CONFIG.ANTICAPTCHA_API_KEY:
        print(f"Enter your AntiCaptcha API key here: {CONFIG_TOML}")
        if CONFIG.AUTOOPEN:
            open_file(CONFIG_TOML)
        return

    uncompleted = set(EMAILS).difference(completed)
    print(f"Total emails: {len(EMAILS)} ({len(tuple(uncompleted))} uncompleted)")
    if not uncompleted:
        print(f"Enter your email:password here: {EMAILS_TXT}")
        if CONFIG.AUTOOPEN:
            open_file(EMAILS_TXT)
        return

    if PROXIES:
        print(f"Total proxies: {len(tuple(PROXIES))}")

    invite_link_or_code = await questionary.text("Enter invite link or code: ").ask_async()
    await join_waitlist(invite_link_or_code, uncompleted)


if __name__ == '__main__':
    asyncio.run(main())
