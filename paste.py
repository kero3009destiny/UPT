# Unnamed Paste Tool by blakeando

import codecs
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from colorama import init
from termcolor import colored

import UPT
from UPT import pastes, proxy, utils, webhook


if __name__ == "__main__":
    init()
    proxies_len = 0
    for proxy_type in list(UPT.proxy_dict):
        proxies_len += len(UPT.proxy_dict[proxy_type])
    for char in list(f"Welcome to Unnamed Paste Tool (Version {UPT.__version__}).\n\nLoaded {proxies_len} Proxies ({', '.join(sorted(list(UPT.proxy_dict)))})\nLoaded {len(list(UPT.regex_list))} Regex\n\n"):
        print(char, end="")
        if char == "\n":
            time.sleep(0.05)
        else:
            time.sleep(0.01)
    print()
    if UPT.webhook_url is None:
        h = input("Use Discord Webhook for output? (Default: n): ")
        if h.lower() == "y":
            UPT.webhook_url = input("Your Webhook, sir?: ")
        else:
            UPT.webhook_url = None
    else:
        print("Using webhook.txt webhook:", UPT.webhook_url)
    if not UPT.webhook_url is None:
        threading.Thread(target=webhook.webhook_controller, daemon=True).start()
    threading.Thread(target=utils.printing_thread, daemon=True).start()
    with ThreadPoolExecutor(max_workers=12) as executor:
        for x in range(12):
            if x + 1 > 8:
                executor.submit(pastes.discovery_thread, x + 1, 1)
            else:
                executor.submit(pastes.discovery_thread, x + 1, 0)
