import sys
import configparser
import requests
import json
import threading
import os

from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from time import sleep
from random import randint
from requests import RequestException
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from cli import log

load_dotenv()

class SteamGifts:
    def __init__(self, cookie, gifts_type, pinned, min_points):
        self.cookie = {
            'PHPSESSID': cookie
        }
        self.gifts_type = gifts_type
        self.pinned = pinned
        self.min_points = int(min_points)
        
        # Leer DEFAULT_PAGE
        default_page_env = os.getenv("DEFAULT_PAGE")
        self.default_page = int(default_page_env) if default_page_env is not None else 1
        self.is_default_page_set = default_page_env is not None

        # Leer MAX_GAMES
        max_games_env = os.getenv("MAX_GAMES")
        self.max_games = int(max_games_env) if max_games_env and max_games_env.isdigit() else None


        self.base = "https://www.steamgifts.com"
        self.session = requests.Session()

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
            'Origin': 'https://www.steamgifts.com',
        }

        self.filter_url = {
            'All': "search?page=%d",
            'Wishlist': "search?page=%d&type=wishlist",
            'Recommended': "search?page=%d&type=recommended",
            'Copies': "search?page=%d&copy_min=2",
            'DLC': "search?page=%d&dlc=true",
            'New': "search?page=%d&type=new"
        }

    def requests_retry_session(
        self,
        retries=5,
        backoff_factor=0.3
    ):
        session = self.session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(500, 502, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get_soup_from_page(self, url):
        r = self.requests_retry_session().get(url)
        r = requests.get(url, cookies=self.cookie)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def update_info(self):
        soup = self.get_soup_from_page(self.base)

        try:
            self.xsrf_token = soup.find('input', {'name': 'xsrf_token'})['value']
            
            points_element = soup.find('span', {'class': 'nav__points'})
            if points_element and points_element.text.isdigit():
                self.points = int(points_element.text)
                log(f"🔄 Points updated: {self.points}", "blue")
            else:
                log("⚠️  Unable to find or parse points. Setting points to 0.", "yellow")
                self.points = 0
        except TypeError:
            log("⛔  Cookie is not valid.", "red")
            sleep(10)
            exit()

    def get_game_content(self, page=None):
        n = page if page else self.default_page
        while True:
            txt = f"⚙️  Retrieving games from page {n}."
            log(txt, "magenta")

            filtered_url = self.filter_url[self.gifts_type] % n
            paginated_url = f"{self.base}/giveaways/{filtered_url}"

            soup = self.get_soup_from_page(paginated_url)
            game_list = soup.find_all('div', {'class': 'giveaway__row-inner-wrap'})

            if not game_list:
                log("⛔  Page is empty. Please, select another type.", "red")
                sleep(10)
                exit()

            games_processed = 0

            for item in game_list:
                if self.max_games and games_processed >= self.max_games:
                    log(f"✅ Processed {games_processed} games as per MAX_GAMES limit.", "cyan")
                    break

                if 'is-faded' in item.get('class', []):
                    game_name = item.find('a', {'class': 'giveaway__heading__name'}).text
                    txt = f"🔄 Already entered: {game_name}"
                    log(txt, "yellow")
                    games_processed += 1
                    continue

                if len(item.get('class', [])) == 2 and not self.pinned:
                    games_processed += 1
                    continue

                if self.points == 0 or self.points < self.min_points:
                    txt = f"🛋️  Sleeping to get 6 points. We have {self.points} points, but we need {self.min_points} to start."
                    log(txt, "yellow")
                    sleep(900)
                    self.start()
                    break

                game_cost = item.find_all('span', {'class': 'giveaway__heading__thin'})[-1]

                if game_cost:
                    game_cost = game_cost.getText().replace('(', '').replace(')', '').replace('P', '')
                else:
                    games_processed += 1
                    continue

                game_name = item.find('a', {'class': 'giveaway__heading__name'}).text

                if self.points - int(game_cost) < 0:
                    txt = f"⛔ Not enough points to enter: {game_name}"
                    log(txt, "red")
                    games_processed += 1
                    continue

                game_id = item.find('a', {'class': 'giveaway__heading__name'})['href'].split('/')[2]
                res = self.entry_gift(game_id)
                if res:
                    self.points -= int(game_cost)
                    txt = f"🎉 One more game! Has just entered {game_name}"
                    log(txt, "green")
                    sleep(randint(3, 7))

                games_processed += 1

            self.update_info()

            if self.is_default_page_set:
                n = self.default_page
            else:
                n += 1

            log("⏳ Waiting 2 minutes before restarting...", "yellow")
            sleep(120)
            self.start()

    def entry_gift(self, game_id):
        payload = {'xsrf_token': self.xsrf_token, 'do': 'entry_insert', 'code': game_id}
        entry = requests.post('https://www.steamgifts.com/ajax.php', data=payload, cookies=self.cookie)
        json_data = json.loads(entry.text)

        if json_data['type'] == 'success':
            return True

    def start(self):
        self.update_info()

        if self.points > 0:
            txt = "🤖 Hoho! I am back! You have %d points. Lets hack." % self.points
            log(txt, "blue")

        self.get_game_content()
