from pathlib import Path

from better_web3.utils import copy_file

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent

CONFIG_DIR = BASE_DIR / "config"
DEFAULT_CONFIG_DIR = CONFIG_DIR / "default"
INPUT_DIR  = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
for dir in (INPUT_DIR, OUTPUT_DIR):
    dir.mkdir(exist_ok=True)

DEFAULT_CONFIG_TOML = DEFAULT_CONFIG_DIR / "config.toml"
DEFAULT_SERVICES_TOML = DEFAULT_CONFIG_DIR / "services.toml"
CONFIG_TOML = CONFIG_DIR / "config.toml"
SERVICES_TOML = CONFIG_DIR / "services.toml"

for default_config_file, config_file in zip(
        (DEFAULT_CONFIG_TOML, DEFAULT_SERVICES_TOML),
        (CONFIG_TOML, SERVICES_TOML)
):
    copy_file(default_config_file, config_file)

PROXIES_TXT = INPUT_DIR / "proxies.txt"
EMAILS_TXT = INPUT_DIR / "emails.txt"
COMPLETED_TXT = OUTPUT_DIR / "completed.txt"
for filepath in (PROXIES_TXT, EMAILS_TXT, COMPLETED_TXT):
    filepath.touch(exist_ok=True)
