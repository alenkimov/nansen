import time
import json

from bot.http_client import CustomClientSession


class NansenAPI:
    def __init__(self, session: CustomClientSession):
        self.session = session

    async def verify_email(self, verification_link: str):
        await self.session.get(verification_link)

    async def join_waitlist(self, email: str, invite_code: str, g_recaptcha_response: str):
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
