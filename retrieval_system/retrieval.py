from qdrant_client import QdrantClient
import yaml
import os
from google import genai

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.yaml")

# Load config
with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# Kiểm tra nếu đang chạy trong Docker
RUNNING_IN_DOCKER = os.getenv("DOCKERIZED", "false").lower() == "true"

# Chọn host phù hợp
if RUNNING_IN_DOCKER:
    config["qdrant"]["host"] = "http://qdrant:6333"  # Dùng trong Docker
else:
    config["qdrant"]["host"] = "http://localhost:6333"  # Dùng trong Local

# Kết nối Qdrant
client = QdrantClient(config["qdrant"]["host"])
collection_name = config["qdrant"]["collection_name"]

embedding_model_name = config["embedding_model"]["name"]

def get_embedding(text):
    client = genai.Client(api_key = config["gemini"]["api_key"])
    result = client.models.embed_content(
        model=embedding_model_name,
        contents=text
    )
    return list(map(float, result.embeddings[0].values))

def search_answer(query, threshold=config["qdrant"]["threshold"], max_results=config["qdrant"]["max_results"]):
    """Tìm kiếm nhiều văn bản phù hợp trong Qdrant, hiển thị score của từng câu"""
    query_embedding = get_embedding(query)

    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=max_results
    )
    
    relevant_results = [(res.score, res.payload["text"]) for res in results if res.score > threshold]
    print(relevant_results)

    if not relevant_results:
        return None

    print("\n🔎 **Kết quả tìm kiếm trong Qdrant:**")
    for idx, (score, text) in enumerate(relevant_results, start=1):
        print(f"Câu {idx}: 🔹 Score: {score:.4f}\n   📝 Context: {text}\n")

    result = "\n".join([text for _, text in relevant_results])
    return result
