import json
import urllib.request
from urllib.error import HTTPError, URLError

URL = "http://127.0.0.1:8000/api/search"

TEST_QUERIES = [
    "Сколько всего билетов мы продали?",
    "Какое количество билетов реализовано на Авиа?",
    "Сколько билетов продали Рога и копыта?",
    "Сколько билетов было продано 28 мая 2026 года?",
    "Покажи общие продажи за май.",
    "Выведи топ-5 партнеров по продажам.",
    "Кто продал больше 100 билетов на ЖД 9 мая?",
    "Выведи топ-3 партнеров, которые продавали билеты на Автобус.",
    "Покажи динамику продаж по дням.",
    "Сравни количество билетов на ЖД и Авиа.",
    "Выгрузи в таблицу все продажи ОАО Гусь и гонорар.",
    "Дай эксель с топ-10 партнерами за май.",
    "Сколько билетов продали на пароход?",
    "Какая сегодня погода в Москве?"
]


def run_postman_emulation():
    print("🚀 Запускаем прогон боевых запросов...\n" + "=" * 60)

    for query in TEST_QUERIES:
        print(f"🗣 ЗАПРОС: {query}")
        payload_dict = {"query_text": query}
        payload_bytes = json.dumps(payload_dict).encode('utf-8')

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        req = urllib.request.Request(URL, data=payload_bytes, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req) as response:
                status_code = response.getcode()
                response_body = response.read().decode('utf-8')

                try:
                    parsed_json = json.loads(response_body)
                    params = parsed_json.get("extracted_params", {})
                    intent = parsed_json.get("intent_used", "N/A")
                    answer = parsed_json.get("text_response", "Нет ответа")
                    excel = parsed_json.get("excel_url")
                    graph = parsed_json.get("graph_url")

                    print(f"⚙️  ИЗВЛЕЧЕНО: Интент='{intent}', Параметры={params}")
                    print(f"🤖 ОТВЕТ: {answer}")
                    if excel: print(f"📊 EXCEL: {excel}")
                    if graph: print(f"📈 ГРАФИК: {graph}")

                except json.JSONDecodeError:
                    print(f"📦 СЫРОЙ ОТВЕТ: {response_body}")

        except HTTPError as e:
            print(f"🔴 ОШИБКА {e.code}: {e.read().decode('utf-8')}")
        except URLError as e:
            print(f"❌ СЕРВЕР НЕДОСТУПЕН: {e.reason}")
            break

        print("-" * 60)


if __name__ == "__main__":
    run_postman_emulation()