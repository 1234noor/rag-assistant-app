from fastapi import APIRouter
from app.schemas.query import QueryRequest, QueryResponse
from app.services.retrieval import retrieve_chunks
from app.services.generation import generate_answer

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    retrieved = retrieve_chunks(request.question, n_results=3)
    result = generate_answer(request.question, retrieved)

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"]
    )