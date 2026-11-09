"""Turn texts into vectors."""

from typing import Protocol

from openai import OpenAI

# Texts per request; the API accepts up to 2048, and a case study has a handful of chunks
BATCH_SIZE = 100


class Embedder(Protocol):
    model: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIEmbedder:
    def __init__(self, client: OpenAI, model: str) -> None:
        self._client = client
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), BATCH_SIZE):
            response = self._client.embeddings.create(
                model=self.model, input=texts[start : start + BATCH_SIZE]
            )
            vectors.extend(item.embedding for item in response.data)
        return vectors
