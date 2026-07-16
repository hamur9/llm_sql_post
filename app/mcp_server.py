import sqlite3
import pandas as pd
import plotly.express as px
import os
import uuid
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("CorporateSQL")

DB_PATH = os.getenv("DB_PATH", "./data/sales.db")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/output/")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def safe_execute(sql: str, params: list) -> pd.DataFrame:
    """Безопасное выполнение SQL через Read-Only коннект и параметризацию."""
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Security Error: Разрешены только SELECT запросы.")

    expected_params = sql.count("?")
    if expected_params == 0:
        params = []
    elif len(params) > expected_params:
        params = params[:expected_params]

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.create_function("LOWER", 1, lambda x: str(x).lower() if x is not None else None)

    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()

@mcp.tool()
def execute_sql(sql_query: str, explanation: str, parameters: list) -> dict:
    """Выполняет обычный SQL-запрос для ответа текстом."""
    try:
        df = safe_execute(sql_query, parameters)
        df = df.where(pd.notnull(df), None)
        return {
            "status": "success",
            "explanation": explanation,
            "data": df.to_dict(orient="records"),
            "file_url": None
        }
    except Exception as e:
        return {"status": "error", "explanation": f"Ошибка БД: {str(e)}"}


@mcp.tool()
def export_excel(sql_query: str, explanation: str, parameters: list, filename: str) -> dict:
    """Выгружает результаты в Excel (.xlsx)."""
    try:
        df = safe_execute(sql_query, parameters)
        file_name = f"{filename}_{uuid.uuid4().hex[:6]}.xlsx"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        df.to_excel(file_path, index=False)
        return {
            "status": "success",
            "explanation": explanation,
            "file_url": f"{BASE_URL}{file_name}"
        }
    except Exception as e:
        return {"status": "error", "explanation": f"Ошибка Excel: {str(e)}"}


@mcp.tool()
def generate_chart(sql_query: str, explanation: str, parameters: list, x_col: str, y_col: str, filename: str) -> dict:
    """Строит HTML-график. Требует точного указания колонок X и Y из SQL-ответа."""
    try:
        df = safe_execute(sql_query, parameters)
        file_name = f"{filename}_{uuid.uuid4().hex[:6]}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)

        fig = px.bar(df, x=x_col, y=y_col, title=explanation)
        fig.write_html(file_path)
        return {
            "status": "success",
            "explanation": explanation,
            "file_url": f"{BASE_URL}{file_name}"
        }
    except Exception as e:
        return {"status": "error", "explanation": f"Ошибка графика: {str(e)}"}