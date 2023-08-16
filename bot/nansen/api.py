import time
import json

from bs4 import BeautifulSoup

from bot.http_client import CustomClientSession


class NansenAPI:
    # DEFAULT_HEADERS = {
    #     'authority': 'getlaunchlist.com',
    #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    #     'accept-language': 'en-GB,en;q=0.6',
    #     'cache-control': 'max-age=0',
    #     'content-type': 'application/x-www-form-urlencoded',
    #     'origin': 'https://www.nansen.ai',
    #     'referer': 'https://www.nansen.ai/',
    #     'sec-ch-ua': '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'document',
    #     'sec-fetch-mode': 'navigate',
    #     'sec-fetch-site': 'cross-site',
    #     'sec-fetch-user': '?1',
    #     'sec-gpc': '1',
    #     'upgrade-insecure-requests': '1',
    # }

    def __init__(self, session: CustomClientSession):
        self.session = session

    async def verify_account(self, verification_link: str):
        await self.session.get(verification_link)

    async def init_register(self, email: str, invite_code: str, g_recaptcha_response: str):
        url = 'https://getlaunchlist.com/s/yeywGr'
        params = {
            'ref': invite_code,
        }
        captcha_setting = json.dumps({
            "keyname": "google_recaptcha_classic",
            "fallback": "true",
            "orgId": "00D5i0000088WA3",
            "ts": time.time()
        })
        data = {
            '_gotcha': '',
            'email': email,
            'captcha_settings': captcha_setting,
            'g-recaptcha-response': g_recaptcha_response,
            'submit': 'Join Waitlist'
        }
        await self.session.post(url, params=params, data=data)

    async def request_csrf_token(self, email: str) -> str:
        url = f'https://getlaunchlist.com/s/yeywGr/{email}?confetti=fire'
        headers = {
            'Content-Type': 'text/html; charset=UTF-8',
        }
        async with self.session.get(url, headers=headers) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'lxml')
            csrf_token_body = soup.find('meta', {'name': 'csrf-token'})
            if csrf_token_body is not None:
                csrf_token = csrf_token_body['content']
                return csrf_token

    async def resend_verification_message(self, email: str, csrf_token: str) -> bool:
        url = f'https://getlaunchlist.com/s/verify/send/{email}'
        json_data = {
            'email': email,
            'csrf_token': csrf_token,
        }
        headers = {
            'Content-Type': 'application/json',
        }
        async with self.session.post(url, headers=headers, json=json_data) as response:
            response_data = await response.json()
            return "ok" in response_data
