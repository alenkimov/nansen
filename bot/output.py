from better_web3.utils import load_lines, write_lines

from bot.paths import COMPLETED_TXT

completed = set(load_lines(COMPLETED_TXT))


def save_completed():
    write_lines(COMPLETED_TXT, completed)
