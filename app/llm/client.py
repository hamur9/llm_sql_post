import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.llm.prompts import get_natural_response_prompt

load_dotenv()

ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434/v1")

api_client = AsyncOpenAI(
    base_url=ollama_url,
    api_key="ollama"
)

MODEL_NAME = "llama3.1"

async def generate_natural_response(user_query: str, raw_data: list) -> str:
    prompt = get_natural_response_prompt(user_query, raw_data)

    response = await api_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Ты бизнес-аналитик, отвечающий в корпоративном мессенджере."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()