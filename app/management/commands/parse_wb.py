import os
import requests
import logging
from django.core.management.base import BaseCommand
from database.models import Product


logging.basicConfig(
    filename='parse.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Command(BaseCommand):
    help = "Парсит товары с Wildberries по ключевому слову"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Поисковый запрос")

    def handle(self, *args, **options):
        query = options["query"]
        max_pages = int(os.getenv("PARSER_MAX_PAGES", 5))
        app_type = os.getenv("PARSER_APP_TYPE", "1")
        dest = os.getenv("PARSER_DEST", "-1257786")
        spp = os.getenv("PARSER_SPP", "30")
        user_agent = os.getenv("PARSER_USER_AGENT", "Mozilla/5.0")

        headers = {"User-Agent": user_agent}
        logging.info(f"Запуск парсера для запроса: {query}")

        added_count = 0

        for page in range(1, max_pages + 1):
            url = (
                "https://search.wb.ru/exactmatch/ru/common/v5/search"
                f"?query={query}&resultset=catalog&page={page}"
                f"&appType={app_type}&dest={dest}&spp={spp}"
            )

            logging.info(f"Загрузка страницы {page}: {url}")

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                logging.warning(f"Ошибка запроса (страница {page}): {e}")
                self.stderr.write(f"[page {page}] ошибка запроса: {e}")
                continue

            try:
                products = response.json().get("data", {}).get("products", [])
            except Exception as e:
                logging.error(f"Ошибка разбора JSON (страница {page}): {e}")
                self.stderr.write(f"[page {page}] ошибка JSON: {e}")
                continue

            if not products:
                logging.info(f"На странице {page} нет товаров")
                continue

            for item in products:
                sizes = item.get("sizes", [])
                price_info = sizes[0].get("price", {}) if sizes else {}

                product_data = {
                    "name": item.get("name", "Unnamed"),
                    "price": price_info.get("basic", 0) // 100,
                    "discounted_price": price_info.get("product", 0) // 100,
                    "rating": item.get("rating", 0),
                    "review_count": item.get("feedbacks", 0),
                }

                obj, created = Product.objects.update_or_create(
                    name=product_data["name"],
                    defaults=product_data
                )

                if created:
                    added_count += 1
                    logging.debug(f"Добавлен товар: {product_data['name']}")

        logging.info(f"Парсинг завершён. Добавлено товаров: {added_count}")
        self.stdout.write(f"Завершено. Добавлено товаров: {added_count}")
