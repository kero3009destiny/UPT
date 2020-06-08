import codecs
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from colorama import init
from termcolor import colored

import UPT
from UPT import proxy, utils, webhook


def paste_downloader_thread(link):
    while UPT.download_queue[link][0] is None:
        proxies = proxy.request_new_proxy()
        UPT.download_queue[link][1] += 1
        try:
            src = UPT.session.get(link, proxies=proxies, timeout=10)
        except Exception:
            success = False
            UPT.download_queue[link][1] += 1
            continue
        else:
            if UPT.download_queue[link][0] is not None:
                success = None
                break
            elif "<title>Pastebin.com - Access Denied Warning</title>" in src.text:
                success = False
                if UPT.download_queue[link][0] is None:
                    UPT.print_queue.append(
                        f"[{link}]: {UPT.utils.convert_bool_to_success(success)} ({UPT.download_queue[link][1]} attempts)")
                    pass
                else:
                    break
            elif "<title>Attention Required! | Cloudflare</title>" in src.text:
                success = False
                if UPT.download_queue[link][0] is None:
                    UPT.print_queue.append(
                        f"[{link}]: {UPT.utils.convert_bool_to_success(success)} ({UPT.download_queue[link][1]} attempts)")
                    pass
                else:
                    break
            elif "<title>Pastebin.com - Heavy Load Warning :(</title>" in src.text:
                success = False
                if UPT.download_queue[link][0] is None:
                    UPT.print_queue.append(
                        f"[{link}]: {UPT.utils.convert_bool_to_success(success)} ({UPT.download_queue[link][1]} attempts)")
                    pass
                else:
                    break
            else:
                success = True
                if UPT.download_queue[link][0] is None:
                    UPT.download_queue[link][0] = src.text
                    UPT.print_queue.append(f"[{link}]: {UPT.utils.convert_bool_to_success(success)} ({UPT.download_queue[link][1]} attempts)")
                break
                


def process_paste(content, filename, link):
    for reg in UPT.regex_list:
        search = set([x.group() for x in re.finditer(UPT.regex_list[reg]["regex"], content)])
        if not len(search) == 0:
            e = 0
            q = f"New {reg}(s) found"
            for expression in search:
                expression = "".join(expression)
                e += 1
                if not e > 20:
                    q += "\n" + str(colored(expression, 'green'))
                if not os.path.isdir(f"regex finds"):
                    os.mkdir(f"regex finds")
                if not os.path.isdir(f"regex finds/raw/"):
                    os.mkdir(f"regex finds/raw/")
                with open(f"regex finds/{reg}.txt", "a+") as f:
                    f.write(f"{expression} | {filename}\n")
                with open(f"regex finds/raw/{reg}.txt", "a+") as f:
                    f.write(f"{expression}\n")
            if e > 20:
                q += f"\n+{len(search) - 20} more"
            UPT.print_queue.append(q)
            if UPT.webhook_url is not None:
                txt = "\n"
                co = 0
                for x in search:
                    if co == 10:
                        break
                    else:
                        co += 1
                        txt += f"{x}\n"
                if len(search) > 10:
                    txt += f"+ {len(search) - 10} more"
                UPT.webhook_queue[txt] = (reg, f"https://pastebin.com/{filename}", )
    try:
        if not os.path.isdir(f"pastes/"):
            os.mkdir(f"pastes/")
        with open(f"pastes/{filename}.txt", "w+") as f:
            f.write(content)
    except:
        pass
    UPT.download_queue.pop(link, None)


def download_paste(link):
    UPT.download_queue[link] = [None, 0]

    with ThreadPoolExecutor(max_workers=5) as executor:
        for x in range(5):
            executor.submit(paste_downloader_thread, link)
            time.sleep(1.5)

    while UPT.download_queue[link][0] is None:
        time.sleep(1)
    
    filename = link.split("/")[-1]
    process_paste(UPT.download_queue[link][0], filename, link)


def discovery_thread(thread_num, mode):
    while True:
        while True:
            proxies = proxy.request_new_proxy()
            try:
                if mode == 0:
                    html_doc = UPT.session.get('https://pastebin.com/archive',
                                        proxies=proxies, timeout=10).text
                elif mode == 1:
                    html_doc = UPT.session.get('https://pastebin.com/',
                                               proxies=proxies, timeout=10).text
            except Exception as e:
                UPT.print_queue.append(
                    f"[Thread {thread_num}]: Failed to Get latest pastes. Trying again...")
                continue
            else:
                if "<title>Pastebin.com - Access Denied Warning</title>" in html_doc:
                    UPT.print_queue.append(
                        f"[Thread {thread_num}]: Proxy is blocked by Pastebin. Trying again...")
                    continue
                elif "<title>Attention Required! | Cloudflare</title>" in html_doc:
                    UPT.print_queue.append(
                        f"[Thread {thread_num}]: Proxy is blocked by Cloudflare. Trying again...")
                    continue
                elif "<title>Pastebin.com - Heavy Load Warning :(</title>" in html_doc:
                    UPT.print_queue.append(
                        f"[Thread {thread_num}]: {colored('Pastebin is under heavy load.', 'red')} Trying again in 20 seconds...")
                    time.sleep(20)
                    continue
                else:
                    break
        soup = BeautifulSoup(html_doc, 'html.parser')
        links = list()
        if mode == 0:
            for a in soup.find_all('tr'):
                reg = re.findall("\/[a-zA-Z0-9]{8}", str(a))
                for r in reg:
                    links.append(f"https://pastebin.com/raw{r}")
        elif mode == 1:
            for a in soup.find_all('li'):
                reg = re.findall("\/[a-zA-Z0-9]{8}", str(a))
                for r in reg:
                    links.append(f"https://pastebin.com/raw{r}")
        number = 0
        for link in links:
            if link in UPT.found:
                pass
            else:
                number += 1
                UPT.found.append(link)
                threading.Thread(target=download_paste,
                                 args=[str(link)], daemon=True).start()
        UPT.print_queue.append(
            f"[Thread {thread_num}]: Found {number} new pastes.")
        time.sleep(10)
