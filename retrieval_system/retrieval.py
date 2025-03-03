from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import yaml

# Load config
with open(r"../config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# Kết nối Qdrant
client = QdrantClient(config["qdrant"]["host"])
collection_name = config["qdrant"]["collection_name"]

# Load model embedding
embedding_model = SentenceTransformer(config["embedding_model"]["name"], trust_remote_code=True)

def search_answer(query, threshold=config["qdrant"]["threshold"], max_results=config["qdrant"]["max_results"]):
    """Tìm kiếm nhiều văn bản phù hợp trong Qdrant, hiển thị score của từng câu"""
    query_embedding = embedding_model.encode(query).tolist()

    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=max_results  # Lấy nhiều kết quả thay vì chỉ 1
    )

    # Lọc các kết quả có độ tương đồng cao hơn ngưỡng
    relevant_results = [(res.score, res.payload["text"]) for res in results if res.score > threshold]

    # Nếu không có dữ liệu phù hợp, trả về None
    if not relevant_results:
        return None

    # Hiển thị debug: In từng câu với điểm số tương ứng
    print("\n🔎 **Kết quả tìm kiếm trong Qdrant:**")
    for idx, (score, text) in enumerate(relevant_results, start=1):
        print(f"Câu {idx}: 🔹 Điểm: {score:.4f}\n   📝 Context: {text}\n")

    # Ghép nhiều câu thành một context duy nhất
    result = "\n".join([text for _, text in relevant_results])
    return result
