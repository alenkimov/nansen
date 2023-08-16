from better_web3 import Proxy
from better_web3.utils import load_lines

from bot.paths import PROXIES_TXT, EMAILS_TXT

PROXIES: set[Proxy] = Proxy.from_file(PROXIES_TXT)
EMAILS: set[str] = set(load_lines(EMAILS_TXT))
