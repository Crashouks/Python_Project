"""Парсинг каталогу книг (books.toscrape.com).

Приклади:
  python scripts/run_scraper.py                                  # демо головної сторінки + збір 2 категорій
  python scripts/run_scraper.py --categories Travel Mystery      # конкретні категорії
  python scripts/run_scraper.py --all --workers 8                # увесь каталог (50 категорій)
  python scripts/run_scraper.py --min-price 30 --min-rating 4    # фільтр результатів
"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tourist_routes.scraper.books_scraper import BOOK_FIELDS, BooksScraper  # noqa: E402

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "scraped"


def parse_args():
    parser = argparse.ArgumentParser(description="Парсинг каталогу https://books.toscrape.com/")
    parser.add_argument("--categories", nargs="+", default=["Travel", "Mystery"],
                        help="назви категорій (за замовчуванням: Travel Mystery)")
    parser.add_argument("--all", action="store_true", help="зібрати всі категорії")
    parser.add_argument("--max-pages", type=int, default=None, help="максимум сторінок на категорію")
    parser.add_argument("--workers", type=int, default=5, help="кількість потоків")
    parser.add_argument("--sequential", action="store_true", help="без багатопотоковості")
    parser.add_argument("--delay", type=float, default=0.0, help="пауза перед запитом, с")
    parser.add_argument("--min-price", type=float, default=None, help="мінімальна ціна (£)")
    parser.add_argument("--max-price", type=float, default=None, help="максимальна ціна (£)")
    parser.add_argument("--min-rating", type=int, default=None, help="мінімальний рейтинг (1-5)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="папка для результатів")
    parser.add_argument("--skip-demo", action="store_true", help="пропустити демо однієї сторінки")
    return parser.parse_args()


def setup_logging(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(output_dir / "scraper.log", encoding="utf-8")],
    )


def print_books_table(books, limit=None):
    shown = books if limit is None else books[:limit]
    print(f"{'№':>3}  {'Ціна':>7}  {'★':>1}  {'Категорія':<16} Назва")
    for index, book in enumerate(shown, start=1):
        price = f"£{book['price']:.2f}" if book["price"] is not None else "—"
        rating = book["rating"] if book["rating"] is not None else "-"
        print(f"{index:>3}  {price:>7}  {rating:>1}  {str(book['category'] or ''):<16.16} {book['title']}")
    if limit is not None and len(books) > limit:
        print(f"... і ще {len(books) - limit}")


def demo_single_page(scraper, output_dir):
    """Базовий рівень: одна сторінка -> структуровані дані, усі посилання, текстовий файл."""
    print("\n=== 1. Демо: головна сторінка ===")
    html = scraper.fetch(scraper.base_url)
    if html is None:
        print("Не вдалося завантажити головну сторінку (див. лог).")
        return
    soup = scraper.parse(html)
    books = scraper.parse_listing_soup(soup, scraper.base_url)
    print(f"Заголовок сторінки: {soup.title.get_text(strip=True) if soup.title else '—'}")
    print(f"Книг на сторінці: {len(books)}\n")
    print_books_table(books)

    links = scraper.extract_links(soup)
    print(f"\nПосилань <a href> на сторінці: {len(links)}")
    for link in links:
        print("  ", link)

    lines = [f"Сторінка: {scraper.base_url}", f"Книг: {len(books)}", ""]
    lines += [f"{b['title']} | £{b['price']} | рейтинг {b['rating']} | {b['url']}" for b in books]
    lines += ["", f"Посилання ({len(links)}):"] + links
    scraper.save_text(lines, output_dir / "page_report.txt")
    print(f"\nЗбережено: {output_dir / 'page_report.txt'}")


def main():
    args = parse_args()
    setup_logging(args.output)
    scraper = BooksScraper(max_workers=args.workers, delay=args.delay)

    if not args.skip_demo:
        demo_single_page(scraper, args.output)

    print("\n=== 2. Збір каталогу з пагінацією ===")
    categories = None if args.all else args.categories
    books = scraper.scrape_catalog(categories, max_pages=args.max_pages, parallel=not args.sequential)
    print(f"Зібрано книг: {len(books)}")
    if not books:
        print("Нічого не зібрано. Перевірте з'єднання та назви категорій (див. лог).")
        return 1

    scraper.save_csv(books, args.output / "books.csv", BOOK_FIELDS)
    scraper.save_json(books, args.output / "books.json")
    print(f"Датасет збережено: {args.output / 'books.csv'}, {args.output / 'books.json'}")

    def matches(book):
        price = book["price"]
        if args.min_price is not None and (price is None or price < args.min_price):
            return False
        if args.max_price is not None and (price is None or price > args.max_price):
            return False
        if args.min_rating is not None and (book["rating"] or 0) < args.min_rating:
            return False
        return True

    filtered = scraper.filter_items(books, matches)
    print(f"\n=== 3. Фільтр (ціна ≥ {args.min_price}, ≤ {args.max_price}, рейтинг ≥ {args.min_rating}) ===")
    print(f"Підходить книг: {len(filtered)} із {len(books)}")
    print_books_table(filtered, limit=15)
    scraper.save_csv(filtered, args.output / "books_filtered.csv", BOOK_FIELDS)

    if scraper.failed_urls:
        print(f"\nНевдалих сторінок: {len(scraper.failed_urls)} (деталі в {args.output / 'scraper.log'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
