from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.service.search import process_search_query

router = APIRouter()

class SearchRequest(BaseModel):
    query_text: str

class SearchResponse(BaseModel):
    status: str
    original_query: str
    extracted_params: Dict[str, Any]
    text_response: str
    excel_url: str | None
    graph_url: str | None

@router.post("/search", response_model=SearchResponse)
async def handle_search(request: SearchRequest):
    try:
        result = await process_search_query(request.query_text)
        return result
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))