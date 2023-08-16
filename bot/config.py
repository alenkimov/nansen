from pydantic import BaseModel
from better_web3.utils import load_toml

from bot._logger import LoggingLevel
from bot.paths import CONFIG_TOML, SERVICES_TOML


class Config(BaseModel):
    LOGGING_LEVEL: LoggingLevel = "INFO"
    ANTICAPTCHA_API_KEY: str
    RETRIES: int = 5
    AUTOOPEN: bool = True
    MAX_TASKS: int = 3


class ServiceData(BaseModel):
    host: str
    folders: list[str]
    domains: list[str]


CONFIG = Config(**load_toml(CONFIG_TOML))
SERVICES: list[ServiceData] = [ServiceData(**service_data) for service_data in load_toml(SERVICES_TOML).values()]
