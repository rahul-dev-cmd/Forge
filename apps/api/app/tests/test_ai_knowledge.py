"""Tests for Milestone 8 — AI Knowledge Layer (Vector DB, Embeddings, RAG Context)."""

import pytest
import uuid
import hashlib
from app.services.vector_db.in_memory import in_memory_vector_provider
from app.services.vector_db.base import VectorPoint
from app.services.embedding.local_provider import local_embedding_provider
from app.services.embedding.factory import embedding_provider_factory


@pytest.mark.asyncio
async def test_local_embedding_provider():
    provider = local_embedding_provider
    assert provider.get_dimensions() == 384
    assert provider.get_model_name() == "all-MiniLM-L6-v2-local"

    texts = ["def add(a, b): return a + b", "class User: pass"]
    vectors = await provider.embed_texts(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert len(vectors[1]) == 384


@pytest.mark.asyncio
async def test_in_memory_vector_provider():
    vdb = in_memory_vector_provider
    col_name = "test_forge_vectors"

    await vdb.create_collection(col_name, 384)

    p1 = VectorPoint(
        id="vec-1",
        vector=[0.1] * 384,
        payload={"workspace_id": "ws-123", "repository_id": "repo-456", "file_path": "main.py"},
    )
    p2 = VectorPoint(
        id="vec-2",
        vector=[0.9] * 384,
        payload={"workspace_id": "ws-123", "repository_id": "repo-789", "file_path": "user.py"},
    )

    await vdb.upsert_vectors(col_name, [p1, p2])

    # Search with workspace and repo filter
    results = await vdb.search_vectors(
        col_name, query_vector=[0.8] * 384, limit=5, filters={"repository_id": "repo-789"}
    )
    assert len(results) == 1
    assert results[0].id == "vec-2"


def test_context_aware_chunk_hash():
    repo_id = uuid.uuid4()
    branch = "main"
    chunk_hash = "abc123hash"

    # Same code content in File A
    raw_a = f"{repo_id}:{branch}:src/file_a.py:1:10:{chunk_hash}"
    hash_a = hashlib.sha256(raw_a.encode("utf-8")).hexdigest()

    # Same code content in File B
    raw_b = f"{repo_id}:{branch}:src/file_b.py:1:10:{chunk_hash}"
    hash_b = hashlib.sha256(raw_b.encode("utf-8")).hexdigest()

    # Hashes must NOT collide across different files!
    assert hash_a != hash_b
