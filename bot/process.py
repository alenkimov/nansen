from collections import defaultdict
from typing import Iterable, Callable

from better_web3 import Proxy
from tqdm.asyncio import tqdm

from bot.http_client import CustomClientSession
from bot.logger import logger


async def _process_accounts_with_session(
        accounts: Iterable,
        fn: Callable,
        *,
        proxy: Proxy = None,
):
    async with CustomClientSession(proxy=proxy) as session:
        for account in accounts:
            email, password = account

            if session.proxy:
                account_info = f"{session.proxy} [{email}]"
            else:
                account_info = f"[{email}]"

            try:
                await fn(session, account)
            except Exception as e:
                logger.error(f"{account_info} Unexpected error: {e}")


async def process_accounts_with_session(
        accounts: Iterable,
        proxies: Iterable[Proxy],
        fn: Callable,
):
    proxy_to_accounts: defaultdict[Proxy: list[accounts]] = defaultdict(list)
    if proxies:
        proxies = tuple(proxies)
        for i, account in enumerate(accounts):
            proxy = proxies[i % len(proxies)]
            proxy_to_accounts[proxy].append(account)
    else:
        proxy_to_accounts[None] = list(accounts)
    tasks = [_process_accounts_with_session(accounts, fn, proxy=proxy) for proxy, accounts in proxy_to_accounts.items()]
    await tqdm.gather(*tasks)
