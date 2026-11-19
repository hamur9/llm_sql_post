import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI
import httpx
from app.prompt import get_system_prompt, get_tools_schema
from app.mcp_server import execute_sql, export_excel, generate_chart

app = FastAPI(title="Corporate SQL Agent API")
app.mount("/output", StaticFiles(directory="output"), name="output")

client = AsyncOpenAI(
    base_url="http://host.docker.internal:11434/v1",
    api_key="ollama",
    http_client=httpx.AsyncClient(proxies=None)
)

MODEL_NAME = "qwen2.5:14b"


class MessengerRequest(BaseModel):
    user_id: int
    text: str


class MessengerResponse(BaseModel):
    text_reply: str
    file_attachment: str | None


@app.post("/webhook/message", response_model=MessengerResponse)
async def handle_message(request: MessengerRequest):
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": request.text}
            ],
            tools=get_tools_schema(),
            tool_choice="auto",
            temperature=0.0
        )

        message = response.choices[0].message
        content = message.content or ""

        tool_name = None
        args = {}

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                return MessengerResponse(text_reply="⚠️ Ошибка декодирования JSON от ИИ.", file_attachment=None)

        elif "{" in content and '"name"' in content and '"arguments"' in content:
            try:
                start = content.find('{')
                end = content.rfind('}') + 1
                parsed = json.loads(content[start:end])

                if "name" in parsed and "arguments" in parsed:
                    tool_name = parsed["name"]
                    args = json.loads(parsed["arguments"]) if isinstance(parsed["arguments"], str) else parsed[
                        "arguments"]
            except Exception:
                pass

        if not tool_name:
            clean_text = content.replace("</tool_call>", "").replace("<tool_call>", "").strip()
            return MessengerResponse(text_reply=clean_text or "Извините, не смог обработать запрос.",
                                     file_attachment=None)

        if "parameters" not in args:
            args["parameters"] = []
        if "explanation" not in args:
            args["explanation"] = "Вот аналитика по вашему запросу."
        if tool_name in ["export_excel", "generate_chart"] and "filename" not in args:
            args["filename"] = "report"
        if tool_name == "generate_chart":
            if "x_col" not in args: args["x_col"] = "Date"
            if "y_col" not in args: args["y_col"] = "Tickets"

        try:
            if tool_name == "export_excel":
                result = export_excel(**args)
            elif tool_name == "generate_chart":
                result = generate_chart(**args)
            else:
                result = execute_sql(**args)
        except TypeError as e:
            return MessengerResponse(text_reply=f"⚠️ Ошибка сборки параметров: {e}\nАргументы: {args}",
                                     file_attachment=None)

        sql_query = args.get("sql_query", "Нет SQL")
        sql_params = args.get("parameters", [])

        if result["status"] == "error":
            return MessengerResponse(
                text_reply=f"⚠️ Ошибка БД:\n{result['explanation']}\n\n⚙️ **SQL:**\n```sql\n{sql_query}\n```",
                file_attachment=None
            )

        final_text = f"🤖 **Анализ:** {result['explanation']}\n\n"

        if tool_name == "execute_sql":
            data = result.get("data", [])
            if data:
                final_text += "📊 **Данные:**\n"
                for row in data:
                    row_str = " | ".join([f"{k}: {v}" for k, v in row.items()])
                    final_text += f"• {row_str}\n"
            else:
                final_text += "🤷‍♂️ По вашему запросу данные не найдены.\n"

        final_text += f"\n⚙️ **Сгенерированный SQL:**\n{sql_query}\n"
        if sql_params:
            final_text += f"\n*Параметры:* {sql_params}"

        return MessengerResponse(
            text_reply=final_text,
            file_attachment=result.get("file_url")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))