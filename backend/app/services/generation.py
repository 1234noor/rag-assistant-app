import ollama
from app.core.config import settings


def build_prompt(question: str, retrieved_chunks: list) -> str:
    """Build a prompt that grounds the LLM's answer in retrieved context."""
    context = "\n\n".join([
        f"[Source: {c['domain']}/{c['source']}]\n{c['text']}"
        for c in retrieved_chunks
    ])

    prompt = f"""You are a helpful study assistant. Answer the question using ONLY the context below.
If the context does not contain enough information, say so honestly instead of guessing.
Always mention which source(s) you used in your answer.

Context:
{context}

Question: {question}

Answer:"""
    return prompt


def generate_answer(question: str, retrieved_chunks: list, distance_threshold: float = 1.0) -> dict:
    """Build prompt and call the LLM to get a grounded answer.
    
    If the closest retrieved chunk is too far (distance above threshold),
    reject the question as out-of-scope instead of calling the LLM,
    to avoid hallucinated answers from the model's general knowledge.
    """
    if not retrieved_chunks or retrieved_chunks[0]["distance"] > distance_threshold:
        return {
            "answer": "I don't have enough relevant information in the provided textbooks to answer this question.",
            "sources": []
        }

    prompt = build_prompt(question, retrieved_chunks)

    response = ollama.chat(model=settings.llm_model, messages=[
        {"role": "user", "content": prompt}
    ])

    answer = response["message"]["content"]
    sources = list(set([f"{c['domain']}/{c['source']}" for c in retrieved_chunks]))

    return {
        "answer": answer,
        "sources": sources
    }