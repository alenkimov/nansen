from utils.captcha_solver import get_captcha_key
from logger.logger import logger
from utils.get_config_data import nansen_ref_key, ramblers_iter, proxy_iter

import asyncio
import email.parser
from bs4 import BeautifulSoup
import email.policy
import json
import time
import aiohttp
import imapclient
import imapclient.exceptions
import pyuseragents


HEADERS = {
            'authority': 'getlaunchlist.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-GB,en;q=0.6',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.nansen.ai',
            'referer': 'https://www.nansen.ai/',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': pyuseragents.random()
        }


class Client:

    imap_server = 'imap.rambler.ru'

    def __init__(self, rambler_data, proxy = None):
        self.mail, self.password = rambler_data.split(':')
        if proxy:
            self.proxy = f"http://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"
        else:
            self.proxy = None
        self.mail_client = None

    async def connect_to_rambler(self):
        logger.info(f"Проверка почты на валидность: {self.mail}")
        self.mail_client = imapclient.IMAPClient(Client.imap_server)
        try:
            self.mail_client.login(self.mail, self.password)
            logger.info(f"Почта валид: {self.mail}")
            return True
        except imapclient.exceptions.LoginError:
            logger.error(f"Неверная почта или пароль: {self.mail}:{self.password}")
            return False
        except Exception as exc:
            logger.error(exc)
            return False

    async def get_messages(self):
        self.mail_client.select_folder('INBOX')
        messages = self.mail_client.search()
        messages_list = []
        for msgid, data in self.mail_client.fetch(messages, 'RFC822').items():
            email_message = data[b'RFC822'].decode('utf-8')
            msg = email.message_from_string(email_message)
            messages_list.append(msg)
        return messages_list

    async def receive_verification_link(self):
        for _ in range(4):
            logger.info(f"Аккаунт: {self.mail} | Чекаю почту... попытка {_+1}/4")
            messages_list = await self.get_messages()
            for msg in messages_list:
                if msg['From'].find('LaunchList') != -1:
                    msg = msg.as_string().replace('=\n', '')
                    soup = BeautifulSoup(msg, 'lxml')
                    for elem in soup.find_all('a'):
                        link = elem.get_text()
                        if link.find('https://getlaunchlist.com/') != -1:
                            logger.debug(f"Аккаунт: {self.mail} | Получил ссылку верификации")
                            return link
                await asyncio.sleep(5)
        return False

    async def verify_nansen_account(self, verification_link):
        async with aiohttp.ClientSession() as session:
            async with session.get(verification_link, headers=HEADERS, proxy=self.proxy) as response:
                json = await response.text()
                if response.status == 200:
                    logger.success(f"Аккаунт: {self.mail} | Успешно подтвердил почту.")
                    with open('success.txt', 'a+') as file:
                        file.writelines(f"{self.mail}:{self.password}\n")
                        return True

    async def init_register(self):
        params = {
            'ref': nansen_ref_key,
        }

        captcha_setting = json.dumps(
                            {"keyname":"google_recaptcha_classic",
                           "fallback":"true","orgId":"00D5i0000088WA3",
                           "ts": time.time()}
                            )
        data = {
            '_gotcha': '',
            'email': self.mail,
            'captcha_settings': captcha_setting,
            'g-recaptcha-response': await get_captcha_key(),
            'submit': 'Join Waitlist'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://getlaunchlist.com/s/yeywGr', params=params, headers=HEADERS,
                                 data=data, proxy=self.proxy) as response:
                if response.status == 200:
                    logger.debug(f"Успешно отправил письмо на регистрацию. Аккаунт: {self.mail}:{self.password}")
                    return True

    async def get_csrf_token(self):
        try:
            async with aiohttp.ClientSession() as session:
                HEADERS['Content-Type'] = 'text/html; charset=UTF-8'
                async with session.get(f'https://getlaunchlist.com/s/yeywGr/{self.mail}?confetti=fire', headers=HEADERS,
                                     proxy=self.proxy) as response:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'lxml')
                    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
                    return csrf_token
        except Exception as exc:
            logger.error(f"Ошибка при получении csrf токена: {exc}")
            return False

    async def resend_verification_message(self, csrf_token):
        try:
            async with aiohttp.ClientSession() as session:
                json_data = {
                    'email': self.mail,
                    'csrf_token': csrf_token,
                }
                HEADERS['Content-Type'] = 'application/json'
                async with session.post(f'https://getlaunchlist.com/s/verify/send/{self.mail}', headers=HEADERS,
                                     proxy=self.proxy, json=json_data) as response:
                    json = await response.json()
                    if json.get('ok'):
                        logger.debug(f"Аккаунт: {self.mail} | Запросил повторное сообщение")
                        return True
        except Exception as exc:
            logger.error(f"Ошибка при получении csrf токена: {exc}")
            return False


    async def main(self):
        if await self.connect_to_rambler():
            if await self.init_register():
                verification_link = await self.receive_verification_link()
                if verification_link:
                    verify_account = await self.verify_nansen_account(verification_link=verification_link)
                if not verification_link:
                    csrf_token = await self.get_csrf_token()
                    resend_mail = await self.resend_verification_message(csrf_token=csrf_token)
                    verification_link = await self.receive_verification_link()
                    if verification_link:
                        verify_account = await self.verify_nansen_account(verification_link=verification_link)
