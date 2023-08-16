from typing import Optional, List
import aiohttp
import pyuseragents
from better_web3 import Proxy
from http.cookies import SimpleCookie


class CustomClientSession(aiohttp.ClientSession):
    def __init__(
            self,
            *,
            proxy: Optional[Proxy] = None,
            cookies_list: Optional[List[dict]] = None,
            useragent: Optional[str] = None,
            **kwargs,
    ) -> None:
        """
        Кастомный клиентский сеанс с поддержкой прокси, cookies и user-agent.
        :param proxy: Объект прокси
        :param cookies_list: Список словарей cookies
        :param useragent: Строка user-agent
        :param kwargs: Дополнительные аргументы для сеанса клиента
        """
        super().__init__(**kwargs)
        self.proxy = proxy

        if useragent is None:
            useragent = pyuseragents.random()
        self.set_useragent(useragent)

        if cookies_list:
            for cookie in cookies_list:
                simple_cookie = SimpleCookie()
                simple_cookie[cookie['name']] = cookie['value']
                self.cookie_jar.update_cookies(simple_cookie)

    async def _request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        proxy_url = self.proxy.as_url if self.proxy else None
        return await super()._request(
            method,
            url,
            proxy=proxy_url,
            **kwargs,
        )

    def set_useragent(self, useragent: str):
        """
        Устанавливает заголовок User-Agent для всех запросов.
        :param useragent: Строка User-Agent
        """
        self._default_headers.update({'user-agent': useragent})
