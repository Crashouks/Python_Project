"""Парсер каталогу https://books.toscrape.com/ (навчальний сайт, створений для парсингу).

Збирає: назва, ціна, рейтинг, категорія, наявність, посилання.
"""
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

from tourist_routes.scraper.web_scraper import WebScraper

BASE_URL = "https://books.toscrape.com/"
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
BOOK_FIELDS = ["title", "price", "rating", "category", "availability", "url"]


class BooksScraper(WebScraper):
    def __init__(self, base_url=BASE_URL, **kwargs):
        super().__init__(base_url=base_url, **kwargs)

    # ---------- розбір окремих елементів ----------

    @staticmethod
    def parse_price(text):
        """'£51.77' (або зіпсоване 'Â£51.77') -> 51.77; якщо числа немає — None."""
        match = re.search(r"\d+(?:\.\d+)?", text or "")
        return float(match.group()) if match else None

    @staticmethod
    def parse_rating(element):
        """<p class="star-rating Three"> -> 3; невідомий або відсутній рейтинг — None."""
        if element is None:
            return None
        for css_class in element.get("class", []):
            if css_class in RATING_WORDS:
                return RATING_WORDS[css_class]
        return None

    def parse_listing_soup(self, soup, page_url, category=None):
        books = []
        for article in soup.select("article.product_pod"):
            link = article.select_one("h3 a")
            if link is None:
                continue
            availability = article.select_one("p.availability")
            price = article.select_one("p.price_color")
            books.append({
                "title": link.get("title") or link.get_text(strip=True),
                "price": self.parse_price(price.get_text(strip=True) if price else ""),
                "rating": self.parse_rating(article.select_one("p.star-rating")),
                "category": category,
                "availability": availability.get_text(strip=True) if availability else None,
                "url": urljoin(page_url, link.get("href", "")),
            })
        return books

    def parse_listing(self, html, page_url, category=None):
        return self.parse_listing_soup(self.parse(html), page_url, category)

    @staticmethod
    def next_page_url(soup, page_url):
        link = soup.select_one("li.next a")
        return urljoin(page_url, link["href"]) if link is not None and link.get("href") else None

    # ---------- збір даних ----------

    def get_categories(self):
        """Словник {назва категорії: адреса} з бічного меню головної сторінки."""
        html = self.fetch(self.base_url)
        if html is None:
            return {}
        soup = self.parse(html)
        categories = {}
        for anchor in soup.select("div.side_categories ul li ul li a"):
            name = anchor.get_text(strip=True)
            if name and anchor.get("href"):
                categories[name] = urljoin(self.base_url, anchor["href"])
        return categories

    def scrape_category(self, name, url, max_pages=None):
        """Збирає всі сторінки категорії, переходячи за посиланням «next» (пагінація)."""
        books, pages = [], 0
        while url and (max_pages is None or pages < max_pages):
            html = self.fetch(url)
            if html is None:
                break
            soup = self.parse(html)
            books.extend(self.parse_listing_soup(soup, url, name))
            pages += 1
            url = self.next_page_url(soup, url)
        self.logger.info("Категорія «%s»: %d книг, сторінок: %d", name, len(books), pages)
        return books

    def scrape_catalog(self, categories=None, max_pages=None, parallel=True):
        """Збирає книги вибраних категорій (за замовчуванням — усіх). Категорії обробляються паралельно."""
        available = self.get_categories()
        if not available:
            self.logger.error("Не вдалося отримати список категорій — збір неможливий.")
            return []
        if categories:
            lookup = {name.lower(): name for name in available}
            selected = {}
            for requested in categories:
                real_name = lookup.get(requested.strip().lower())
                if real_name is None:
                    self.logger.warning("Категорію «%s» не знайдено, пропускаю.", requested)
                else:
                    selected[real_name] = available[real_name]
        else:
            selected = available

        def task(pair):
            return self.scrape_category(pair[0], pair[1], max_pages)

        pairs = list(selected.items())
        if parallel and self.max_workers > 1 and len(pairs) > 1:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                chunks = list(executor.map(task, pairs))
        else:
            chunks = [task(pair) for pair in pairs]
        return [book for chunk in chunks for book in chunk]
