import codecs
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
from UPT import pastes, utils, webhook


def select_random_proxy():
    proxy_type = random.choice(list(UPT.proxy_dict))
    return f"{proxy_type}://{random.choice(list(set(UPT.proxy_dict[proxy_type])))}"


def request_new_proxy():
    proxy_origin = select_random_proxy()
    proxies = {
        'http': proxy_origin,
        'https': proxy_origin
    }
    return proxies
