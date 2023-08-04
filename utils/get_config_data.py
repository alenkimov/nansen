import os
import json
from itertools import cycle

config_path = os.path.abspath('config.json')
with open(config_path, 'r') as file:
    config_file = json.load(file)
    capmonster_apikey = config_file['capmonster_apikey']
    captcha_type = config_file['captcha_type']
    captcha_site_key = config_file['captcha_site_key']
    site_url = config_file['site_url']
    nansen_ref_key = config_file['nansen_ref_key']

with open('ramblers.txt', 'r') as file:
    ramblers_list = [x.rstrip() for x in file.readlines()]
    ramblers_iter = iter(ramblers_list)

with open('proxy.txt', 'r') as file:
    proxy_list = [x.rstrip() for x in file.readlines()]
    proxy_iter = cycle(proxy_list)