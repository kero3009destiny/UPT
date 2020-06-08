import codecs
from datetime import datetime
import json
import os
import random
import re
import sys
import threading
import time
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from colorama import init
from termcolor import colored

import UPT
from UPT import pastes, proxy, utils


def webhook_controller():
    webhook = requests.Session()
    proxies_len = 0
    for proxy_type in list(UPT.proxy_dict):
        proxies_len += len(UPT.proxy_dict[proxy_type])
    payload = {
        "username": f"Unnamed Paste Tool v{UPT.__version__}",
        "avatar_url": "https://i.imgur.com/YVafcin.png",
        "embeds": [
            {
                "title": "Unnamed Paste Tool is now running.",
                "description": f"Version: {UPT.__version__}\nProxies: {proxies_len} ({', '.join(sorted(list(UPT.proxy_dict)))})\nTime Started: {datetime.fromtimestamp(int(datetime.timestamp(datetime.now()))).strftime('%d/%m/%Y %I:%M %p')}",
                "color": random.randint(1, 16777215),
            }
        ]
    }
    webhook.post(UPT.webhook_url, json=payload)
    while True:
        for x in list(UPT.webhook_queue):
            try:
                payload = {
                    "username": f"Unnamed Paste Tool v{UPT.__version__}",
                    "avatar_url": "https://i.imgur.com/YVafcin.png",
                    "embeds": [
                        {
                            "title": f"New {UPT.webhook_queue[x][0]}(s) found:",
                            "description": f"{x}\n\nLocation: {UPT.webhook_queue[x][1]}",
                            "color": random.randint(1, 16777215),
                        }
                    ]
                }
                counter = 0
                for action in UPT.regex_list[UPT.webhook_queue[x][0]]["actions"]:
                    try:
                        payload["content"]
                    except:
                        payload["content"] = str()
                    if action.startswith("mention:"):
                        payload["content"] += UPT.regex_list[UPT.webhook_queue[x][0]]["actions"][counter].replace("mention:", "") + "\n"
                    elif action.startswith("send_raw"):
                        payload["content"] += x + "\n"
                    counter += 1
                webhook.post(UPT.webhook_url, json=payload)
                del UPT.webhook_queue[x]
                time.sleep(5)
            except:
                time.sleep(5)
