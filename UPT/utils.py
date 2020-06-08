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
from UPT import pastes, proxy, webhook


def printing_thread():
    while True:
        for p in UPT.print_queue:
            print(p)
            UPT.print_queue.remove(p)


def convert_bool_to_success(b):
    if b:
        return colored("Success", "green")
    else:
        return colored("Failed", "red")
