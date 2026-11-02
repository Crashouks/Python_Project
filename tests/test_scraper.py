import csv
import json
import logging
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from tourist_routes.scraper.books_scraper import BOOK_FIELDS, BooksScraper  # noqa: E402
from tourist_routes.scraper.web_scraper import WebScraper  # noqa: E402

BASE = "https://books.test/"


def book_html(title, price, rating, href, availability="In stock"):
    return f"""
    <article class="product_pod">
      <p class="star-rating {rating}"></p>
      <h3><a href="{href}" title="{title}">{title[:10]}...</a></h3>
      <div class="product_price">
        <p class="price_color">{price}</p>
        <p class="instock availability"><i class="icon-ok"></i> {availability} </p>
      </div>
    </article>"""


HOME_HTML = f"""
<html><head><title>All products | Books</title></head><body>
<div class="side_categories"><ul><li><a href="catalogue/category/books_1/index.html">Books</a>
  <ul>
    <li><a href="catalogue/category/books/travel_2/index.html"> Travel </a></li>
    <li><a href="catalogue/category/books/mystery_3/index.html">Mystery</a></li>
  </ul></li></ul></div>
<a href="#top">нагору</a><a href="javascript:void(0)">js</a><a href="mailto:a@b.c">mail</a>
<a href="/about.html">About</a><a href="about.html">About again</a>
<a href="https://other.site/page">Зовнішнє</a><a href="">порожнє</a>
{book_html("Alpha Book", "£10.50", "Three", "catalogue/alpha_1/index.html")}
</body></html>"""

TRAVEL_P1 = f"""<html><body>
{book_html("Travel One", "£45.00", "Five", "../../../travel-one_1/index.html")}
{book_html("Travel Two", "Â£12.99", "Two", "../../../travel-two_2/index.html", "Out of stock")}
<ul class="pager"><li class="next"><a href="page-2.html">next</a></li></ul>
</body></html>"""

TRAVEL_P2 = f"""<html><body>
{book_html("Travel Three", "£99.99", "Four", "../../../travel-three_3/index.html")}
</body></html>"""

MYSTERY_P1 = f"""<html><body>
{book_html("Mystery One", "£30.00", "One", "../../../mystery-one_4/index.html")}
</body></html>"""

CAT = BASE + "catalogue/category/books/"


class FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text
        self.encoding = None


class FakeSession:
    """Підміняє requests.Session: повертає заздалегідь підготовлені відповіді, нічого не качає."""

    def __init__(self, pages=None):
        self.headers = {}
        self.pages = pages or {}
        self.calls = []
        self._lock = threading.Lock()

    def get(self, url, timeout=None):
        with self._lock:
            self.calls.append(url)
        result = self.pages.get(url)
        if result is None:
            return FakeResponse(404, "not found")
        if isinstance(result, Exception):
            raise result
        if isinstance(result, FakeResponse):
            return result
        if isinstance(result, list):  # послідовність відповідей для перевірки повторних спроб
            with self._lock:
                item = result.pop(0) if len(result) > 1 else result[0]
            if isinstance(item, Exception):
                raise item
            return item
        return FakeResponse(200, result)


def make_scraper(pages=None, scraper_class=WebScraper, **kwargs):
    session = FakeSession(pages)
    kwargs.setdefault("retry_delay", 0)
    scraper = scraper_class(session=session, **({"base_url": BASE} | kwargs))
    scraper.logger = logging.getLogger("test.scraper")
    scraper.logger.setLevel(logging.CRITICAL)
    return scraper, session


class FetchTests(unittest.TestCase):
    def test_success_sets_headers_and_encoding(self):
        scraper, session = make_scraper({BASE: "<html>ok</html>"})
        self.assertEqual(scraper.fetch(BASE), "<html>ok</html>")
        self.assertIn("User-Agent", session.headers)
        self.assertEqual(scraper.failed_urls, {})

    def test_404_is_not_retried(self):
        scraper, session = make_scraper({}, retries=3)
        self.assertIsNone(scraper.fetch(BASE + "missing"))
        self.assertEqual(len(session.calls), 1)
        self.assertEqual(scraper.failed_urls[BASE + "missing"], "HTTP 404")

    def test_server_error_is_retried_then_succeeds(self):
        pages = {BASE: [FakeResponse(500), FakeResponse(503), FakeResponse(200, "<p>ok</p>")]}
        scraper, session = make_scraper(pages, retries=2)
        self.assertEqual(scraper.fetch(BASE), "<p>ok</p>")
        self.assertEqual(len(session.calls), 3)
        self.assertEqual(scraper.failed_urls, {})

    def test_server_error_gives_up_after_all_attempts(self):
        scraper, session = make_scraper({BASE: FakeResponse(500)}, retries=2)
        self.assertIsNone(scraper.fetch(BASE))
        self.assertEqual(len(session.calls), 3)
        self.assertEqual(scraper.failed_urls[BASE], "HTTP 500")

    def test_429_is_retried(self):
        pages = {BASE: [FakeResponse(429), FakeResponse(200, "x")]}
        scraper, session = make_scraper(pages, retries=1)
        self.assertEqual(scraper.fetch(BASE), "x")
        self.assertEqual(len(session.calls), 2)

    def test_network_errors(self):
        for error in (requests.ConnectionError("down"), requests.Timeout("slow")):
            with self.subTest(error=type(error).__name__):
                scraper, session = make_scraper({BASE: error}, retries=1)
                self.assertIsNone(scraper.fetch(BASE))
                self.assertEqual(len(session.calls), 2)
                self.assertIn(type(error).__name__, scraper.failed_urls[BASE])

    def test_recovers_after_network_error(self):
        pages = {BASE: [requests.ConnectionError("blip"), FakeResponse(200, "ok")]}
        scraper, _ = make_scraper(pages, retries=1)
        self.assertEqual(scraper.fetch(BASE), "ok")

    def test_logging_of_success_and_failure(self):
        scraper, _ = make_scraper({BASE: "ok"})
        scraper.logger.setLevel(logging.INFO)
        with self.assertLogs(scraper.logger, level="INFO") as captured:
            scraper.fetch(BASE)
            scraper.fetch(BASE + "missing")
        text = "\n".join(captured.output)
        self.assertIn("Отримано", text)
        self.assertIn("Не вдалося отримати", text)

    def test_delay_is_applied(self):
        scraper, _ = make_scraper({BASE: "ok"}, delay=0.001)
        self.assertEqual(scraper.fetch(BASE), "ok")


class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.scraper, _ = make_scraper()
        self.soup = self.scraper.parse(HOME_HTML)

    def test_extract_links_absolute_unique_and_filtered(self):
        links = self.scraper.extract_links(self.soup)
        self.assertIn(BASE + "about.html", links)
        self.assertIn("https://other.site/page", links)
        self.assertEqual(links.count(BASE + "about.html"), 1)
        for link in links:
            self.assertTrue(link.startswith("http"), link)
        joined = " ".join(links)
        for bad in ("javascript", "mailto", "#top"):
            self.assertNotIn(bad, joined)

    def test_extract_links_respects_page_url(self):
        soup = self.scraper.parse('<a href="x.html">x</a>')
        self.assertEqual(self.scraper.extract_links(soup, "https://a.test/dir/"), ["https://a.test/dir/x.html"])

    def test_extract_text(self):
        self.assertEqual(self.scraper.extract_text(self.soup, "title"), ["All products | Books"])
        self.assertEqual(self.scraper.extract_text(self.soup, ".nope"), [])

    def test_extract_items_generic(self):
        fields = {
            "title": ("h3 a", "title"),
            "price": ("p.price_color", None),
            "url": ("h3 a", "href"),
            "missing": (".nope", None),
            "css": ("p.star-rating", "class"),
        }
        items = self.scraper.extract_items(self.soup, "article.product_pod", fields)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Alpha Book")
        self.assertEqual(items[0]["price"], "£10.50")
        self.assertEqual(items[0]["url"], BASE + "catalogue/alpha_1/index.html")
        self.assertIsNone(items[0]["missing"])
        self.assertEqual(items[0]["css"], "star-rating Three")

    def test_extract_items_on_empty_page(self):
        self.assertEqual(self.scraper.extract_items(self.scraper.parse(""), "article", {"a": ("a", None)}), [])


class BooksParsingTests(unittest.TestCase):
    def setUp(self):
        self.scraper, _ = make_scraper(scraper_class=BooksScraper, base_url=BASE)

    def test_parse_price(self):
        for text, expected in [("£51.77", 51.77), ("Â£12.99", 12.99), ("£5", 5.0), ("free", None), (None, None), ("", None)]:
            with self.subTest(text=text):
                self.assertEqual(BooksScraper.parse_price(text), expected)

    def test_parse_rating(self):
        soup = self.scraper.parse('<p class="star-rating Four"></p><p class="star-rating Zero"></p>')
        first, second = soup.select("p")
        self.assertEqual(BooksScraper.parse_rating(first), 4)
        self.assertIsNone(BooksScraper.parse_rating(second))
        self.assertIsNone(BooksScraper.parse_rating(None))

    def test_parse_listing(self):
        books = self.scraper.parse_listing(TRAVEL_P1, CAT + "travel_2/index.html", "Travel")
        self.assertEqual(len(books), 2)
        first, second = books
        self.assertEqual(set(first), set(BOOK_FIELDS))
        self.assertEqual((first["title"], first["price"], first["rating"], first["category"]),
                         ("Travel One", 45.0, 5, "Travel"))
        self.assertEqual(first["availability"], "In stock")
        self.assertEqual(first["url"], BASE + "catalogue/travel-one_1/index.html")
        self.assertEqual((second["price"], second["rating"], second["availability"]), (12.99, 2, "Out of stock"))

    def test_parse_listing_handles_broken_and_empty_pages(self):
        self.assertEqual(self.scraper.parse_listing("", BASE), [])
        broken = '<article class="product_pod"><p>без посилання</p></article>'
        self.assertEqual(self.scraper.parse_listing(broken, BASE), [])
        partial = '<article class="product_pod"><h3><a href="b.html">Назва</a></h3></article>'
        book = self.scraper.parse_listing(partial, BASE)[0]
        self.assertEqual(book["title"], "Назва")
        self.assertIsNone(book["price"])
        self.assertIsNone(book["rating"])
        self.assertIsNone(book["availability"])

    def test_next_page_url(self):
        soup = self.scraper.parse(TRAVEL_P1)
        self.assertEqual(BooksScraper.next_page_url(soup, CAT + "travel_2/index.html"), CAT + "travel_2/page-2.html")
        self.assertIsNone(BooksScraper.next_page_url(self.scraper.parse(TRAVEL_P2), CAT))


def catalog_pages():
    return {
        BASE: HOME_HTML,
        CAT + "travel_2/index.html": TRAVEL_P1,
        CAT + "travel_2/page-2.html": TRAVEL_P2,
        CAT + "mystery_3/index.html": MYSTERY_P1,
    }


class CatalogTests(unittest.TestCase):
    def make(self, pages=None, **kwargs):
        return make_scraper(pages if pages is not None else catalog_pages(), scraper_class=BooksScraper, **kwargs)

    def test_get_categories(self):
        scraper, _ = self.make()
        categories = scraper.get_categories()
        self.assertEqual(list(categories), ["Travel", "Mystery"])
        self.assertEqual(categories["Travel"], CAT + "travel_2/index.html")

    def test_get_categories_when_home_unavailable(self):
        scraper, _ = self.make({})
        self.assertEqual(scraper.get_categories(), {})

    def test_scrape_category_follows_pagination(self):
        scraper, session = self.make()
        books = scraper.scrape_category("Travel", CAT + "travel_2/index.html")
        self.assertEqual([b["title"] for b in books], ["Travel One", "Travel Two", "Travel Three"])
        self.assertEqual(len(session.calls), 2)

    def test_scrape_category_max_pages(self):
        scraper, session = self.make()
        books = scraper.scrape_category("Travel", CAT + "travel_2/index.html", max_pages=1)
        self.assertEqual(len(books), 2)
        self.assertEqual(len(session.calls), 1)

    def test_scrape_category_stops_when_page_fails(self):
        pages = catalog_pages()
        del pages[CAT + "travel_2/page-2.html"]
        scraper, _ = self.make(pages)
        self.assertEqual(len(scraper.scrape_category("Travel", CAT + "travel_2/index.html")), 2)
        self.assertIn(CAT + "travel_2/page-2.html", scraper.failed_urls)

    def test_scrape_catalog_parallel_and_sequential_match(self):
        parallel, _ = self.make()
        sequential, _ = self.make()
        a = parallel.scrape_catalog(parallel=True)
        b = sequential.scrape_catalog(parallel=False)
        self.assertEqual(a, b)
        self.assertEqual([x["title"] for x in a], ["Travel One", "Travel Two", "Travel Three", "Mystery One"])
        self.assertEqual({x["category"] for x in a}, {"Travel", "Mystery"})

    def test_scrape_catalog_selected_categories_case_insensitive(self):
        scraper, _ = self.make()
        books = scraper.scrape_catalog(["mystery", "Unknown"])
        self.assertEqual([b["title"] for b in books], ["Mystery One"])

    def test_scrape_catalog_without_internet(self):
        scraper, _ = self.make({})
        self.assertEqual(scraper.scrape_catalog(), [])


class ScrapeUrlsTests(unittest.TestCase):
    def test_order_preserved_and_failures_skipped(self):
        urls = [f"{BASE}p{i}" for i in range(6)]
        pages = {u: f"<b>{i}</b>" for i, u in enumerate(urls) if i != 3}
        scraper, _ = make_scraper(pages, max_workers=4)
        result = scraper.scrape_urls(urls, lambda html, url: [(url, html)])
        self.assertEqual([u for u, _ in result], [u for i, u in enumerate(urls) if i != 3])
        self.assertIn(urls[3], scraper.failed_urls)

    def test_parser_exception_is_recorded_not_raised(self):
        scraper, _ = make_scraper({BASE: "x"})

        def explode(html, url):
            raise ValueError("boom")

        self.assertEqual(scraper.scrape_urls([BASE], explode), [])
        self.assertIn("помилка розбору", scraper.failed_urls[BASE])

    def test_sequential_mode_and_empty_input(self):
        scraper, _ = make_scraper({BASE: "x"})
        self.assertEqual(scraper.scrape_urls([BASE], lambda h, u: [h], parallel=False), ["x"])
        self.assertEqual(scraper.scrape_urls([], lambda h, u: [h]), [])


class SaveAndFilterTests(unittest.TestCase):
    BOOKS = [
        {"title": "Дешева", "price": 10.0, "rating": 2},
        {"title": "Дорога, з комою", "price": 150.5, "rating": 5},
        {"title": "Без ціни", "price": None, "rating": 3},
    ]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.scraper, _ = make_scraper()

    def tearDown(self):
        self.tmp.cleanup()

    def test_filter_items(self):
        expensive = WebScraper.filter_items(self.BOOKS, lambda b: (b["price"] or 0) > 100)
        self.assertEqual([b["title"] for b in expensive], ["Дорога, з комою"])
        self.assertEqual(WebScraper.filter_items([], lambda b: True), [])

    def test_save_json_roundtrip_creates_directories(self):
        path = self.dir / "nested" / "books.json"
        self.scraper.save_json(self.BOOKS, path)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), self.BOOKS)
        self.assertIn("Дешева", path.read_text(encoding="utf-8"))

    def test_save_csv_roundtrip(self):
        path = self.dir / "books.csv"
        self.scraper.save_csv(self.BOOKS, path)
        with open(path, encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual([r["title"] for r in rows], [b["title"] for b in self.BOOKS])
        self.assertEqual(rows[0]["price"], "10.0")
        self.assertEqual(rows[2]["price"], "")

    def test_save_csv_with_fieldnames_and_empty_data(self):
        path = self.dir / "only_header.csv"
        self.scraper.save_csv([], path, ["title", "price"])
        self.assertEqual(path.read_text(encoding="utf-8-sig").strip(), "title,price")
        empty = self.dir / "empty.csv"
        self.scraper.save_csv([], empty)
        self.assertEqual(empty.read_text(encoding="utf-8-sig").strip(), "")

    def test_save_csv_ignores_extra_keys(self):
        path = self.dir / "subset.csv"
        self.scraper.save_csv(self.BOOKS, path, ["title"])
        self.assertEqual(path.read_text(encoding="utf-8-sig").splitlines()[0], "title")

    def test_save_text(self):
        path = self.dir / "report.txt"
        self.scraper.save_text(["рядок 1", 2], path)
        self.assertEqual(path.read_text(encoding="utf-8"), "рядок 1\n2\n")


if __name__ == "__main__":
    unittest.main()
