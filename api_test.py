import requests
import json
import time

API_URL = "http://127.0.0.1:8000/webhook/message"
TEST_SCENARIOS = [
    "Сколько всего билетов мы продали?",
    "Какое количество билетов реализовано на Авиа?",
    "Сколько билетов продали Рога и копыта?",
    "Сколько билетов было продано 28 мая 2026 года?",
    "Покажи общие продажи за май",
    "Выведи топ-5 партнеров по продажам.",
    "Кто продал больше 100 билетов на ЖД 9 мая?",
    "Выведи топ-3 партнеров, которые продавали билеты на Автобус.",
    "Покажи динамику продаж по дням.",
    "Сравни количество билетов на ЖД и Авиа.",
    "Выгрузи в таблицу все продажи ОАО Гусь и гонорар.",
    "Дай эксель с топ-10 партнерами за май.",
    "Сколько билетов продали на пароход?",
    "Какая сегодня погода в Москве?",
    "Сколько всего билетов мы продали?",
    "Сравни продажи ЖД и Авиа. Сделай график.",
    "Выгрузи в эксель топ 5 партнеров за май",
    "Какая сегодня погода в Москве?",
    "Сколько билетов продали на пароходы?"
]


def run_tests():
    print("🚀 Запуск интеграционного тестирования AI-Агента...\n" + "=" * 60)

    for i, text in enumerate(TEST_SCENARIOS, 1):
        print(f"🗣 [Пользователь]: {text}")

        payload = {
            "user_id": 100 + i,
            "text": text
        }

        start_time = time.time()
        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            elapsed_time = round(time.time() - start_time, 1)

            print(f"🤖 [AI Агент] ({elapsed_time} сек): {result.get('text_reply')}")
            if result.get("file_attachment"):
                print(f"📎 [Вложение]: {result['file_attachment']}")

        except requests.exceptions.RequestException as e:
            print(f"❌ [Ошибка сервера]: {e}")

        print("-" * 60)


if __name__ == "__main__":
    run_tests()