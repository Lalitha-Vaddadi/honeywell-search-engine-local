from sentence_transformers import SentenceTransformer
import asyncio
from typing import Union, List
from app.config import settings

_model = SentenceTransformer(settings.embedding_model_name)


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    return _model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()


async def embed_text_async(text: str) -> List[float]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: generate_embeddings([text])[0],
    )


async def embed_query(
    query: Union[str, List[str]]
) -> Union[List[float], List[List[float]]]:

    if isinstance(query, str):
        q = query.lower()

        intent = ""
        if any(w in q for w in ["drawback", "shortcoming", "limitation"]):
            intent = "limitations drawbacks shortcomings disadvantages"
        elif any(w in q for w in ["investigate", "investigation", "examine", "study", "effect"]):
            intent = "investigation study analysis effect"

        expanded_query = f"{query}. {intent}".strip()
        return await embed_text_async(expanded_query)

    if isinstance(query, list):
        texts = [q for q in query if isinstance(q, str) and q.strip()]
        if not texts:
            return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: generate_embeddings(texts),
        )

    raise TypeError("embed_query expects str or List[str]")
