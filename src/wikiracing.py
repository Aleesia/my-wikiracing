from typing import List
import psycopg2
import requests
from bs4 import BeautifulSoup
import urllib
import re
import time
from datetime import timedelta
from ratelimit import limits, sleep_and_retry

rqst_per_min = 100
links_per_page = 200
database_path = "pg_data/postgres_db.sql"
ukrainian = r'[а-яА-ЯіїєґІЇЄҐ-]'
english = r'[a-zA-z]'
max_retries = 50


def title_to_link(title: str) -> str:
    return "https://uk.wikipedia.org/wiki/" + title


def link_to_title(link: str) -> str:
    return link.split('/')[-1]


def remove_apostroph(title: str) -> str:
    if "'" in title:
        title = title.split("'")
        title = "''".join(title)
    return title


class WikiRacer:
    def __init__(self) -> None:
        self.db_path = database_path
        self.db_table = "wikipages"

    def establish_connection(self) -> None:
        flag = True
        counter = 0
        while flag and counter < max_retries:
            counter += 1
            try:
                self.conn = psycopg2.connect(dbname="postgres_db",
                                             host="localhost",
                                             user="postgres",
                                             password="postgres",
                                             port=5432)
                self.cursor = self.conn.cursor()
                flag = False
            except Exception:
                time.sleep(1)
        try:
            q = f"SELECT * FROM {self.db_table}"
            self.cursor.execute(q)
        except Exception:
            self.conn.commit()
            self.create_table()

    def create_table(self) -> None:
        mylist = [str(i) for i in range(1, max_path_length + 1)]
        columns = " varchar(255), page_".join(mylist)
        columns = "page_" + columns + " varchar(255)"
        query = f"CREATE TABLE {self.db_table} ({columns});"
        self.cursor.execute(query)
        self.conn.commit()

    def find_path(self, start: str, finish: str) -> List[str]:
        self.establish_connection()
        self.finish = re.sub(' ', '_', finish)
        start = re.sub(' ', '_', start)
        self.path_length = 2
        curr_all_pages = self.get_next_pages_one(start)
        while self.finish not in curr_all_pages:
            self.path_length += 1
            curr_all_pages = self.get_next_pages(curr_all_pages)
        if self.finish in curr_all_pages:
            result_path = self.build_path(self.finish)
        else:
            print("Failed to find path of length <= ", max_path_length)
            result_path = []
        self.conn.close()
        return result_path

    def build_path(self, finish: str) -> List[str]:
        pages_path = self.get_path(finish)
        pages_path.append(finish)
        return [re.sub('_', ' ', page) for page in pages_path]

    def add_pages_to_db(self, page: str, next_pages: List[str]) -> None:
        path = self.get_path(page)
        for next_one in next_pages:
            self.add_one_page_to_db(path, next_one)

    def get_path(self, page: str) -> List[str]:
        if self.path_length == 2:
            return [page,]
        else:
            my_s = ', '.join([f"page_{i}" for i in range(
                1, self.path_length)])
            if page == self.finish:
                query = f"SELECT {my_s} FROM {self.db_table}\
                        WHERE page_{self.path_length} =\
                        '{remove_apostroph(page)}'"
            else:
                query = f"SELECT {my_s} FROM {self.db_table}\
                        WHERE page_{self.path_length - 1} =\
                        '{remove_apostroph(page)}'"
            self.cursor.execute(query)
            prev = self.cursor.fetchall()
            prev = prev[0]
            return [pr for pr in prev]

    def add_one_page_to_db(self, path: List[str], next_one: str) -> None:
        columns = ", ".join([f"page_{i}"
                             for i in range(1, self.path_length + 1)])
        values = [remove_apostroph(pg) for pg in path] + [
            remove_apostroph(next_one)]
        str_values = "', '".join(values)
        query = f"INSERT INTO {self.db_table} ({columns})\
            VALUES ('{str_values}')"
        self.cursor.execute(query, values)
        self.conn.commit()

    def get_next_from_db(self, start: str) -> List[str]:
        next_pages = []
        for i in range(1, 5):
            query = f"SELECT page_{i+1}\
                FROM {self.db_table} WHERE\
                page_{i} = '{remove_apostroph(start)}'"
            self.cursor.execute(query)
            pages = self.cursor.fetchall()
            for p in pages:
                if p[0] is not None:
                    next_pages.append(p)
        return next_pages

    def check_page_in_database(self, start: str) -> bool:
        for i in range(1, 5):
            query = f"SELECT page_{i+1} FROM {self.db_table}\
                    WHERE page_{i} = '{remove_apostroph(start)}'"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if len(result) > 0:
                for elem in result:
                    if elem[0] is None:
                        return False
                return True
        return False

    def get_next_pages_one(self, start: str) -> List[str]:
        if self.check_page_in_database(start):
            next_pages = self.get_next_from_db(start)
        else:
            all_links = self.get_next_links(start)
            next_pages = []
            for link in all_links:
                curr_page = link_to_title(link)
                next_pages.append(curr_page)
            self.add_pages_to_db(start, next_pages)
        return next_pages

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
        while i < len(all_links) and counter < 200:
            link = all_links[i]
            if self.is_good_link(link):
                curr_href = urllib.parse.unquote(link.get("href"))
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
