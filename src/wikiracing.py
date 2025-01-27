from typing import List
import psycopg2
import requests
from bs4 import BeautifulSoup
import urllib
import re
from datetime import timedelta
from ratelimit import limits, sleep_and_retry

rqst_per_min = 100
links_per_page = 200
ukrainian = r'[а-яА-ЯіїєґІЇЄҐ-]'
english = r'[a-zA-z]'


def title_to_link(title: str) -> str:
    return "https://uk.wikipedia.org/wiki/" + title


def link_to_title(link: str) -> str:
    return link.split('/')[-1]


class WikiRacer:
    def __init__(self) -> None:
        self.establish_connection()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS wikipages (
            root varchar(250),
            parent varchar(250),
            child varchar(250));""")
        self.conn.commit()

    def establish_connection(self) -> None:
        self.conn = psycopg2.connect(dbname="postgres_db",
                                     host="localhost",
                                     user="postgres",
                                     password="postgres",
                                     port=5432)
        self.cursor = self.conn.cursor()
        print("Connection Is Ready!!!!")

    def find_path(self, start: str, finish: str) -> List[str]:
        self.finish = re.sub(' ', '_', finish)
        self.start = re.sub(' ', '_', start)
        self.path_len = 2
        curr_all_pages = self.get_next_pages_one(self.start)
        while self.finish not in curr_all_pages:
            self.path_len += 1
            curr_all_pages = self.get_next_pages(curr_all_pages)
        result_path = self.get_path(self.finish, self.start)
        final_result = [re.sub('_', ' ', page) for page in result_path]
        print("found path : ", ', '.join(final_result))
        return final_result

    def add_pages_to_db(self, page: str, next_pages: List[str]) -> None:
        for next_one in next_pages:
            self.add_one_page_to_db(page, next_one)

    def get_path(self, page: str, start: str) -> List[str]:
        result = [page,]
        while result[0] != start:
            self.cursor.execute("""
                SELECT parent FROM wikipages
                WHERE child = %s
                AND root = %s;""", (result[0], self.start))
            prev = self.cursor.fetchall()[0][0]
            result.insert(0, prev)
        return result

    def add_one_page_to_db(self, page: str, next_one: str) -> None:
        if not self.child_in_db(next_one):
            self.cursor.execute("""
                INSERT INTO wikipages (root, parent, child)
                VALUES (%s, %s, %s);""", (self.start, page, next_one))
            self.conn.commit()

    def get_next_from_db(self, start: str) -> List[str]:
        self.cursor.execute("""
            SELECT DISTINCT child FROM wikipages
            WHERE parent = %s;""", (start,))
        pages = self.cursor.fetchall()
        return [p[0] for p in pages]

    def child_in_db(self, child: str) -> bool:
        self.cursor.execute("""
            SELECT * FROM wikipages
            WHERE root = %s
            AND child = %s;""", (self.start, child))
        res = self.cursor.fetchall()
        return len(res) > 0

    def parent_in_curr_db(self, parent: str) -> bool:
        self.cursor.execute("""
            SELECT * FROM wikipages
            WHERE root = %s
            AND parent = %s;""", (self.start, parent))
        res = self.cursor.fetchall()
        return len(res) > 0

    def parent_in_all_db(self, page: str) -> bool:
        self.cursor.execute("""
            SELECT * FROM wikipages
            WHERE parent = %s;""", (page,))
        res = self.cursor.fetchall()
        return len(res) > 0

    def get_next_pages(self, curr_all_pages: List[str]) -> List[str]:
        next_all_pages = []
        for page in curr_all_pages:
            pages = self.get_next_pages_one(page)
            for p in pages:
                if p not in next_all_pages:
                    next_all_pages.append(p)
            if self.finish in pages:
                break
        return next_all_pages

    def get_next_pages_one(self, start: str) -> List[str]:
        if self.parent_in_all_db(start):
            next_pages = self.get_next_from_db(start)
        else:
            all_links = self.get_next_links(start)
            next_pages = []
            for link in all_links:
                curr_page = link_to_title(link)
                next_pages.append(curr_page)
            self.add_pages_to_db(start, next_pages)
        return next_pages

    @sleep_and_retry
    @limits(calls=rqst_per_min, period=timedelta(seconds=60).total_seconds())
    def get_next_links(self, start: str) -> List[str]:
        url = title_to_link(start)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find(id="bodyContent").find_all("a")
        links = self.parse_page_links(all_links)
        return links

    def parse_page_links(self, all_links: List[str]) -> List[str]:
        selected_links = []
        counter = 0
        i = 0
        while i < len(all_links) and counter < links_per_page:
            link = all_links[i]
            if self.is_good_link(link):
                curr_href = urllib.parse.unquote(link.get("href"))
                if curr_href not in selected_links:
                    selected_links.append(curr_href)
                    counter += 1
            i += 1
        return selected_links

    def is_good_link(self, link: str) -> bool:
        try:
            curr_href = urllib.parse.unquote(link.get("href"))
            if link['href'].find("/wiki/") == -1:
                return False
        except Exception:
            return False
        else:
            if curr_href is None or curr_href[0:6] != "/wiki/":
                return False
            if '.' in curr_href or ':' in curr_href:
                return False
            curr_href = curr_href[6:]
            ua_letters = ''.join(re.findall(ukrainian, curr_href))
            en_letters = ''.join(re.findall(english, curr_href))
            if len(ua_letters) >= 3 and len(en_letters) <= 3:
                return True
        return False
