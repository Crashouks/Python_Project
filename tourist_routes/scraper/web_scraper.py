"""Універсальний клас для парсингу веб-сторінок: завантаження, витяг даних, логування,
багатопотоковий збір, збереження у TXT/CSV/JSON."""
import csv
import json
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

DEFAULT_USER_AGENT = "TouristRoutesScraper/1.0 (навчальний проєкт)"
SKIPPED_HREF_PREFIXES = ("#", "javascript:", "mailto:", "tel:")


class WebScraper:
    def __init__(self, base_url="", session=None, timeout=10.0, retries=2, retry_delay=0.5,
                 delay=0.0, max_workers=5, encoding="utf-8", headers=None, logger=None):
        """
        retries      — скільки повторних спроб робити після невдалої (усього спроб = retries + 1)
        delay        — пауза перед кожним запитом (ввічливість до сервера), секунди
        max_workers  — кількість потоків для багатопотокового збору
        """
        self.base_url = base_url
        self.timeout = timeout
        self.retries = max(0, retries)
        self.retry_delay = retry_delay
        self.delay = delay
        self.max_workers = max(1, max_workers)
        self.encoding = encoding
        self.logger = logger or logging.getLogger("tourist_routes.scraper")
        self.session = session if session is not None else requests.Session()
        self.session.headers.update({"User-Agent": DEFAULT_USER_AGENT, **(headers or {})})
        self.failed_urls = {}
        self._lock = threading.Lock()

    # ---------- завантаження ----------

    def fetch(self, url):
        """Повертає HTML сторінки або None, якщо отримати її не вдалося (причина записується в лог)."""
        total_attempts = self.retries + 1
        reason = "невідома помилка"
        for attempt in range(1, total_attempts + 1):
            if self.delay:
                time.sleep(self.delay)
            retryable = True
            try:
                response = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as error:
                reason = f"{type(error).__name__}: {error}"
            else:
                if response.status_code < 400:
                    response.encoding = self.encoding
                    self.logger.info("Отримано %s (спроба %d/%d)", url, attempt, total_attempts)
                    return response.text
                reason = f"HTTP {response.status_code}"
                retryable = response.status_code >= 500 or response.status_code == 429
            self.logger.warning("Невдала спроба %d/%d для %s: %s", attempt, total_attempts, url, reason)
            if not retryable or attempt == total_attempts:
                break
            time.sleep(self.retry_delay * attempt)
        self._record_failure(url, reason)
        return None

    def _record_failure(self, url, reason):
        with self._lock:
            self.failed_urls[url] = reason
        self.logger.error("Не вдалося отримати %s: %s", url, reason)

    @staticmethod
    def parse(html):
        return BeautifulSoup(html, "html.parser")

    # ---------- витяг даних ----------

    def extract_links(self, soup, page_url=None):
        """Усі унікальні посилання <a href> сторінки (абсолютні адреси, у порядку появи)."""
        base = page_url or self.base_url
        links, seen = [], set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if not href or href.lower().startswith(SKIPPED_HREF_PREFIXES):
                continue
            absolute = urljoin(base, href)
            if absolute not in seen:
                seen.add(absolute)
                links.append(absolute)
        return links

    def extract_text(self, soup, selector):
        """Текст усіх елементів за CSS-селектором (порожні пропускаються)."""
        texts = (element.get_text(strip=True) for element in soup.select(selector))
        return [text for text in texts if text]

    def extract_items(self, soup, item_selector, fields, page_url=None):
        """Універсальний витяг записів.

        fields: {"назва_поля": ("css-селектор", атрибут або None)}. Якщо атрибут None —
        береться текст. Значення href/src перетворюються на абсолютні адреси.
        Відсутній елемент дає None.
        """
        base = page_url or self.base_url
        items = []
        for container in soup.select(item_selector):
            record = {}
            for name, (selector, attribute) in fields.items():
                element = container.select_one(selector)
                if element is None:
                    record[name] = None
                elif attribute is None:
                    record[name] = element.get_text(strip=True)
                else:
                    value = element.get(attribute)
                    if isinstance(value, list):
                        value = " ".join(value)
                    if value is not None and attribute in ("href", "src"):
                        value = urljoin(base, value)
                    record[name] = value
            items.append(record)
        return items

    # ---------- багатопотоковий збір ----------

    def scrape_urls(self, urls, parse_func, parallel=True):
        """Завантажує сторінки та застосовує parse_func(html, url) -> список записів.

        Результати об'єднуються в порядку переданих адрес (незалежно від порядку завершення потоків).
        Помилка однієї сторінки не зупиняє решту.
        """
        urls = list(urls)

        def task(url):
            html = self.fetch(url)
            if html is None:
                return []
            try:
                return parse_func(html, url)
            except Exception as error:  # noqa: BLE001 — одна погана сторінка не має зупиняти збір
                self._record_failure(url, f"помилка розбору: {error}")
                return []

        if parallel and self.max_workers > 1 and len(urls) > 1:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                chunks = list(executor.map(task, urls))
        else:
            chunks = [task(url) for url in urls]
        return [item for chunk in chunks for item in chunk]

    # ---------- фільтрація ----------

    @staticmethod
    def filter_items(items, predicate):
        return [item for item in items if predicate(item)]

    # ---------- збереження ----------

    @staticmethod
    def _prepare_path(path):
        directory = os.path.dirname(str(path))
        if directory:
            os.makedirs(directory, exist_ok=True)

    def save_text(self, lines, path):
        self._prepare_path(path)
        with open(path, "w", encoding="utf-8") as file:
            file.write("\n".join(str(line) for line in lines))
            file.write("\n")
        self.logger.info("Збережено текст: %s", path)

    def save_json(self, items, path):
        self._prepare_path(path)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(items, file, ensure_ascii=False, indent=4)
        self.logger.info("Збережено JSON (%d записів): %s", len(items), path)

    def save_csv(self, items, path, fieldnames=None):
        """CSV у UTF-8 з BOM, щоб Excel коректно відкривав кирилицю та символ £."""
        if fieldnames is None:
            fieldnames = list(items[0].keys()) if items else []
        self._prepare_path(path)
        with open(path, "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(items)
        self.logger.info("Збережено CSV (%d записів): %s", len(items), path)
