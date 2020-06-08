import codecs
import json
import os

import requests

# Version Info
__version_info__ = (3, 2, 2)
__version__ = '.'.join(map(str, __version_info__))

# Request Session
session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"

# Values
found = list()
print_queue = list()
webhook_queue = dict()
download_queue = dict()
proxy_dict = dict()

# Load Config, regex, proxies, webhook
if not os.path.isdir('proxies'):
    os.mkdir("proxies")

regex_list = json.load(codecs.open('regex.json', 'r', 'utf-8-sig'))
if os.path.isfile("proxies/socks4-proxies.txt"):
    proxy_dict["socks4"] = open("proxies/socks4-proxies.txt").read().splitlines()
if os.path.isfile("proxies/socks5-proxies.txt"):
    proxy_dict["socks5"] = open("proxies/socks5-proxies.txt").read().splitlines()
if os.path.isfile("proxies/proxies.txt"):
    proxy_dict["http"] = open("proxies/proxies.txt").read().splitlines()

if not os.path.isfile("proxies/socks4-proxies.txt") and not os.path.isfile("proxies/socks5-proxies.txt") and not os.path.isfile("proxies/proxies.txt"):
    proxyscrape = session.get("https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=700&country=all&ssl=all&anonymity=all").text.split("\r\n")
    proxy_dict["http"] = proxyscrape
    with open("proxies/proxies.txt", "w") as f:
        for line in proxyscrape:
            f.write(f"{line}\n")

if not os.path.isdir(f"pastes"):
    os.mkdir(f"pastes")

if os.path.isfile("webhook.txt"):
    webhook_url = open("webhook.txt").read().splitlines()[0]
else:
    webhook_url = None
