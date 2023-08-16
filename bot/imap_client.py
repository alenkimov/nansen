import email
from collections import defaultdict
from email.message import Message
from typing import Iterable

from aioimaplib import IMAP4_SSL


class CustomIMAPClientSSL(IMAP4_SSL):
    async def __aenter__(self):
        await self.wait_hello_from_server()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.logout()

    async def get_messages_from_folders(self, folders: Iterable[str]) -> dict[str: list[Message]]:
        messages = defaultdict(list)
        for folder in folders:
            await self.select(folder)
            result, data = await self.search("ALL")
            if result == 'OK':
                for number_bytes in data[0].split():
                    number = number_bytes.decode('utf-8')
                    result, data = await self.fetch(number, '(RFC822)')
                    if result == 'OK':
                        messages[folder].append(email.message_from_bytes(data[1]))
        return messages
