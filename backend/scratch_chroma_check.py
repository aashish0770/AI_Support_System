from app.services.vectorstore.chroma_client import get_collection

c = get_collection()

c.upsert(
    ids=["test_1"],
    embeddings=[[0.1] * 384],
    documents=["hello"],
)

print(c.query(
    query_embeddings=[[0.1] * 384],
    n_results=1,
))

print("count:", c.count())

c.delete(ids=["test_1"])

print("Test document deleted.")
print("final count:", c.count())