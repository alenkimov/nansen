import os
import subprocess
import platform
from pathlib import Path


def open_file(path: Path):
    path_str = str(path)
    if platform.system() == 'Windows':
        os.startfile(path_str)
    elif platform.system() == 'Darwin':
        subprocess.run(['open', path_str])
    else: # Linux
        subprocess.run(['xdg-open', path_str])


def curry_async(async_func):
    async def curried(*args, **kwargs):
        def bound_async_func(*args2, **kwargs2):
            return async_func(*(args + args2), **{**kwargs, **kwargs2})

        return bound_async_func

    return curried
