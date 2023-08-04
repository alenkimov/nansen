import asyncio

from client import Client
from asyncio import Semaphore, create_task

from utils.get_config_data import ramblers_iter, proxy_iter
from logger.logger import logger

async def _process_accounts(rambler_data, proxy, semaphore):
    async with semaphore:
        try:
            await Client(rambler_data=rambler_data, proxy=proxy).main()
        except Exception as exc:
            logger.error(f"Аккаунт: {rambler_data} | {exc}")

async def process_accounts():
    semaphore = Semaphore(10)

    tasks = []
    for account in ramblers_iter:
        task = create_task(_process_accounts(rambler_data=account, proxy=next(proxy_iter), semaphore=semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    logger.debug("Разработчик: @flextive | TG CHANNEL: @flexterwork | Donate: 0x63f9716a17c751d97306289b22556b879ed8fb74")
    asyncio.run(process_accounts())