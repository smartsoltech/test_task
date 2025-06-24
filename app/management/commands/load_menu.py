import requests
from django.core.management.base import BaseCommand
from database.models import Category

class Command(BaseCommand):
    help = "Загружает и сохраняет структуру категорий Wildberries"

    def handle(self, *args, **kwargs):
        url = "https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json"
        self.stdout.write("🔄 Получаем структуру категорий...")

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.stderr.write(f"Ошибка загрузки: {e}")
            return

        def save_nodes(nodes, parent=None, level=0):
            for node in nodes:
                cat, _ = Category.objects.update_or_create(
                    wb_id=node["id"],
                    defaults={
                        "name": node["name"],
                        "parent": parent,
                        "shard": node.get("shard", ""),
                        "query": node.get("query", ""),
                        "url": node.get("url", ""),
                        "level": level
                    }
                )
                if node.get("childs"):
                    save_nodes(node["childs"], parent=cat, level=level+1)

        save_nodes(data)
        self.stdout.write(self.style.SUCCESS("✅ Структура категорий успешно загружена."))
