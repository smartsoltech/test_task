import os
import requests
import logging
from django.core.management.base import BaseCommand, CommandError
from database.models import Category, Product, ProductHistory

logging.basicConfig(
    filename='parse.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Command(BaseCommand):
    help = "Парсит товары Wildberries по выбранной категории (wb_id из базы Category)"

    def add_arguments(self, parser):
        parser.add_argument("wb_id", type=int, help="WB ID категории из базы данных")

    def handle(self, *args, **options):
        wb_id = options["wb_id"]
        try:
            category = Category.objects.get(wb_id=wb_id)
        except Category.DoesNotExist:
            raise CommandError(f"Категория с wb_id={wb_id} не найдена в базе")

        max_pages = int(os.getenv("PARSER_MAX_PAGES", 5))
        user_agent = os.getenv("PARSER_USER_AGENT", "Mozilla/5.0")
        resultset = os.getenv("PARSER_RESULTSET", "catalog")
        dest = os.getenv("PARSER_DEST", "-1257786")
        app_type = os.getenv("PARSER_APP_TYPE", "1")
        spp = os.getenv("PARSER_SPP", "30")

        headers = {"User-Agent": user_agent}
        logging.info(f"🔍 Парсинг категории: {category.name} (wb_id={wb_id})")

        added_count = 0


        if not category.query:
            self.stderr.write(f"❌ У категории '{category.name}' (wb_id={wb_id}) отсутствует поле query.")
            return

        for page in range(1, max_pages + 1):
            url = (
                f"https://search.wb.ru/exactmatch/ru/common/v5/search"
                f"?appType={app_type}&dest={dest}&spp={spp}"
                f"&query={category.query}&page={page}&resultset={resultset}"
            )

            logging.info(f"📄 Загружается страница {page}: {url}")

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logging.warning(f"⚠️ Ошибка при запросе страницы {page}: {e}")
                continue

            products = data.get("data", {}).get("products", [])
            if not products:
                logging.info(f"⛔ На странице {page} нет товаров")
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
                    defaults={
                        **product_data,
                        "category": category
                    }
                )

                ProductHistory.objects.create(
                    product=obj,
                    price=product_data["price"],
                    discounted_price=product_data["discounted_price"],
                    rating=product_data["rating"],
                    review_count=product_data["review_count"]
                )

                if created:
                    added_count += 1
                    logging.debug(f"🆕 Новый товар: {product_data['name']}")

        logging.info(f"✅ Парсинг завершён. Добавлено новых товаров: {added_count}")
        self.stdout.write(self.style.SUCCESS(
            f"Парсинг завершён. Добавлено новых товаров: {added_count}"
        ))
