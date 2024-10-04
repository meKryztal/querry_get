import sys
import json
import time
from datetime import datetime
from colorama import init, Fore, Style
from urllib.parse import unquote
import cloudscraper
import os
import pyrogram
from pyrogram import Client
from fake_useragent import UserAgent
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName

init(autoreset=True)


PROXY_TYPE = "socks5"  # http/socks5
USE_PROXY = False  # True/False
API_ID = 11111111  # апи
API_HASH = 'авпавпвапвап'


class PixelTod:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Origin': 'https://app.notpx.app',
            'Referer': 'https://app.notpx.app/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Ch-Ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128", "Microsoft Edge WebView2";v="128"',
            'Sec-Ch-Ua-mobile': '?1',
            'Sec-Ch-Ua-platform': '"Android"',
            "User-Agent": UserAgent(os='android').random
        }
        self.ref = None
        self.peer = None
        self.name = None


    def data_parsing(self, data):
        return {key: value for key, value in (i.split('=') for i in unquote(data).split('&'))}

    def main(self):
        action = int(input(f'{Fore.LIGHTBLUE_EX}Выберите действие:\n{Fore.LIGHTWHITE_EX}1. Начать создание querry\n{Fore.LIGHTWHITE_EX}2. Создать сессию\n>'))

        if not os.path.exists('sessions'):
            os.mkdir('sessions')

        if action == 2:
            self.create_sessions()

        if action == 1:
            sessions = self.pars_sessions()
            accounts = self.check_valid_sessions(sessions)

            if not accounts:
                raise ValueError(f"{Fore.LIGHTRED_EX}Нет валидных сессий")
            ref = input(f"{Fore.LIGHTYELLOW_EX}Укажите рефку:\n")
            self.ref = ref
            peer = input(f"{Fore.LIGHTYELLOW_EX}Укажите название бота:\n")
            self.peer = peer
            name = input(f"{Fore.LIGHTYELLOW_EX}Укажите короткое имя:\n")
            self.name = name
            while True:
                for idx, account in enumerate(accounts):
                    if USE_PROXY:
                        proxy_dict = {}
                        with open('proxy.txt', 'r') as file:
                            proxy_list = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                            for prox, name in proxy_list:
                                proxy_dict[name] = prox
                        proxy = proxy_dict[account]
                        proxy_client = {
                            "scheme": PROXY_TYPE,
                            "hostname": proxy.split(':')[0],
                            "port": int(proxy.split(':')[1]),
                            "username": proxy.split(':')[2],
                            "password": proxy.split(':')[3],
                        }
                        prox = proxy_client
                    else:
                        prox = None

                    data = self.get_tg_web_data(account, prox, ref=self.ref, peer=self.peer, name=self.name)
                    with open('initdata.txt', 'a', encoding='utf-8') as file:
                        file.write(str(data) + '\n')
                    time.sleep(5)
                sys.exit()
    def pars_sessions(self):
        sessions = []
        for file in os.listdir('sessions/'):
            if file.endswith(".session"):
                sessions.append(file.replace(".session", ""))

        self.log(f"{Fore.LIGHTYELLOW_EX}Найдено сессий: {Fore.LIGHTWHITE_EX}{len(sessions)}!")
        return sessions
    def create_sessions(self):
        while True:
            session_name = input(F'{Fore.LIGHTBLUE_EX}Введите название сессии (для выхода нажмите Enter)\n')
            if not session_name:
                return

            if USE_PROXY:
                proxy_dict = {}
                with open('proxy.txt', 'r') as file:
                    proxy_list = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                    for prox, name in proxy_list:
                        proxy_dict[name] = prox

                if session_name in proxy_dict:
                    proxy = proxy_dict[session_name]
                    proxy_client = {
                        "scheme": PROXY_TYPE,
                        "hostname": proxy.split(':')[0],
                        "port": int(proxy.split(':')[1]),
                        "username": proxy.split(':')[2],
                        "password": proxy.split(':')[3],
                    }

                    with pyrogram.Client(
                        api_id=API_ID,
                        api_hash=API_HASH,
                        name=session_name,
                        workdir="sessions/",
                        proxy=proxy_client
                    ) as session:
                        user_data = session.get_me()
                    self.log(f'{Fore.LIGHTYELLOW_EX}Добавлена сессия +{user_data.phone_number} @{user_data.username} PROXY {proxy.split(":")[0]}')
                else:
                    with pyrogram.Client(
                        api_id=API_ID,
                        api_hash=API_HASH,
                        name=session_name,
                        workdir="sessions/"
                    ) as session:


                        user_data = session.get_me()

                    self.log(f'{Fore.LIGHTYELLOW_EX}Добавлена сессия +{user_data.phone_number} @{user_data.username} PROXY : NONE')
            else:
                with pyrogram.Client(
                        api_id=API_ID,
                        api_hash=API_HASH,
                        name=session_name,
                        workdir="sessions/"
                ) as session:

                    user_data = session.get_me()

                self.log(f'{Fore.LIGHTYELLOW_EX}Добавлена сессия +{user_data.phone_number} @{user_data.username} PROXY : NONE')

    def check_valid_sessions(self, sessions: list):
        self.log(f"{Fore.LIGHTYELLOW_EX}Проверяю сессии на валидность!")
        valid_sessions = []
        if USE_PROXY:
            proxy_dict = {}
            with open('proxy.txt', 'r') as file:
                proxy_list = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                for prox, name in proxy_list:
                    proxy_dict[name] = prox
            for session in sessions:
                try:
                    if session in proxy_dict:
                        proxy = proxy_dict[session]
                        proxy_client = {
                            "scheme": PROXY_TYPE,
                            "hostname": proxy.split(':')[0],
                            "port": int(proxy.split(':')[1]),
                            "username": proxy.split(':')[2],
                            "password": proxy.split(':')[3],
                        }
                        client = Client(name=session, api_id=API_ID, api_hash=API_HASH, workdir="sessions/",
                                        proxy=proxy_client)

                        if client.connect():
                            client.get_me()
                            valid_sessions.append(session)
                        else:
                            self.log(f"{Fore.LIGHTRED_EX}{session}.session is invalid")

                        client.disconnect()
                    else:
                        client = Client(name=session, api_id=API_ID, api_hash=API_HASH, workdir="sessions/")

                        if client.connect():
                            client.get_me()
                            valid_sessions.append(session)
                        else:
                            self.log(f"{Fore.LIGHTRED_EX}{session}.session is invalid")
                        client.disconnect()
                except:
                    self.log(f"{Fore.LIGHTRED_EX}{session}.session is invalid")
            self.log(f"{Fore.LIGHTYELLOW_EX}Валидных сессий: {Fore.LIGHTWHITE_EX}{len(valid_sessions)}; {Fore.LIGHTYELLOW_EX}Невалидных: {Fore.LIGHTWHITE_EX}{len(sessions) - len(valid_sessions)}")

        else:
            for session in sessions:
                try:
                    client = Client(name=session, api_id=API_ID, api_hash=API_HASH, workdir="sessions/")

                    if client.connect():
                        client.get_me()
                        valid_sessions.append(session)
                    else:
                        self.log(f"{session}.session is invalid")
                    client.disconnect()
                except:
                    self.log(f"{Fore.LIGHTRED_EX}{session}.session is invalid")
            self.log(f"{Fore.LIGHTYELLOW_EX}Валидных сессий: {Fore.LIGHTWHITE_EX}{len(valid_sessions)}; {Fore.LIGHTYELLOW_EX}Невалидных: {Fore.LIGHTWHITE_EX}{len(sessions) - len(valid_sessions)}")
        return valid_sessions

    def get_tg_web_data(self, account, prox, ref: str, peer: str, name: str):
        auth_url = None
        if USE_PROXY:
            client = Client(name=account, api_id=API_ID, api_hash=API_HASH, workdir="sessions/", proxy=prox)
        else:
            client = Client(name=account, api_id=API_ID, api_hash=API_HASH, workdir="sessions/")
        client.connect()
        client.get_me()

        try:
            bot = client.resolve_peer(peer)
            app = InputBotAppShortName(bot_id=bot, short_name=f"{name}")
            web_view = client.invoke(RequestAppWebView(
                    peer=bot,
                    app=app,
                    platform='android',
                    write_allowed=True,
                    start_param=ref
                ))
            auth_url = web_view.url
            json.loads((unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])))[5:].split('&chat_instance')[0])

        except Exception as err:
            self.log(f"{err}")
        client.disconnect()
        return unquote(auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])



    def log(self, message):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{Fore.LIGHTBLACK_EX}[{now}]{Style.RESET_ALL} {message}")



if __name__ == "__main__":
    try:
        app = PixelTod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
