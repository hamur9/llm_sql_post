import json
import re
from app.llm.client import api_client, MODEL_NAME, generate_natural_response
from app.llm.prompts import get_system_prompt
from app.database.connection import get_sales_analytics
from app.reports.excel_generator import generate_excel
from app.reports.graph_generator import generate_graph


async def process_search_query(query_text: str) -> dict:
    system_prompt = get_system_prompt()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_sales_analytics",
                "description": "Получает аналитику по продажам билетов. ВЫЗЫВАЙ ВСЕГДА.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "partner": {"type": "string", "description": "Название компании (например 'ОАО Гусь')."},
                        "start_date": {"type": "string", "description": "Начальная дата (YYYY-MM-DD)."},
                        "end_date": {"type": "string", "description": "Конечная дата (YYYY-MM-DD)."},
                        "service": {"type": "string", "enum": ["ЖД", "Авиа", "Автобус"]},
                        "intent": {
                            "type": "string",
                            "enum": ["count", "sum", "avg", "top", "daily"],
                            "description": "sum - общая сумма; top - рейтинг; daily - динамика по дням."
                        },
                        "limit": {"type": "integer"}
                    },
                    "required": ["intent"]
                }
            }
        }
    ]

    response = await api_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_text}
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_sales_analytics"}},
        temperature=0.0
    )

    message = response.choices[0].message

    extracted_params = {}
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        try:
            extracted_params = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            pass

    query_lower = query_text.lower()
    needs_excel = any(word in query_lower for word in ["эксель", "excel", "таблиц", "выгруз"])
    needs_graph = any(word in query_lower for word in ["график", "диаграмм", "динамик", "сравни"])

    valid_db_keys = {"partner", "service", "start_date", "end_date", "intent", "limit"}
    db_params = {}

    service_roots = {"ЖД": "жд", "Авиа": "авиа", "Автобус": "автобус"}
    time_markers = ["январ", "феврал", "март", "апрел", "май", "мае", "июн", "июл", "август", "сентябр", "октябр",
                    "ноябр", "декабр", "год", "день", "дней", "сегодня", "вчера"]
    has_time_in_query = any(marker in query_lower for marker in time_markers) or bool(re.search(r'\d{4}|\d{1,2}\s*[а-я]+', query_lower))

    for k, v in extracted_params.items():
        if k in valid_db_keys:
            if v not in [None, "", "null", "None"]:
                if k == "limit" and str(v) == "0":
                    continue
                if k == "service":
                    if v not in service_roots:
                        continue
                    if service_roots[v] not in query_lower:
                        continue
                if k in ["start_date", "end_date"]:
                    if not has_time_in_query:
                        continue
                db_params[k] = v

    if needs_graph and "динамик" in query_lower:
        db_params["intent"] = "daily"

    if "start_date" in db_params and "end_date" not in db_params:
        db_params["end_date"] = db_params["start_date"]
    elif "end_date" in db_params and "start_date" not in db_params:
        db_params["start_date"] = db_params["end_date"]

    if "сравни" in query_lower and "service" in db_params:
        del db_params["service"]

    if db_params.get("intent") == "count" and any(
            word in query_lower for word in ["билет", "сколько", "количество", "продаж"]):
        db_params["intent"] = "sum"

    if "intent" not in db_params:
        db_params["intent"] = "sum"

    raw_data = get_sales_analytics(**db_params)
    text_response = await generate_natural_response(query_text, raw_data)

    excel_path = generate_excel(raw_data) if needs_excel else None
    graph_path = generate_graph(raw_data) if needs_graph else None
    base_url = "http://127.0.0.1:8000/"

    return {
        "status": "success",
        "original_query": query_text,
        "extracted_params": db_params,
        "intent_used": db_params.get("intent", "sum"),
        "text_response": text_response,
        "excel_url": f"{base_url}{excel_path}" if excel_path else None,
        "graph_url": f"{base_url}{graph_path}" if graph_path else None
    }