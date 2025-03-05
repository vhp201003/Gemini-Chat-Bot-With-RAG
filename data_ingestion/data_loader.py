from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
import re
import json
import pdfplumber
import docx
import yaml
from google import genai
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.yaml")

# Định nghĩa kích thước chunk tối đa
CHUNK_SIZE = 200
BATCH_SIZE = 10  # Kích thước batch
MAX_WORKERS = 5  # Số luồng tối đa

global_id_counter = 1  # Bắt đầu từ 1

def generate_sequential_id():
    """Tạo ID tự tăng mà không bị trùng"""
    global global_id_counter
    unique_id = global_id_counter
    global_id_counter += 1
    return unique_id

def chunk_text(text, chunk_size=CHUNK_SIZE):
    chunks = []
    while len(text) > chunk_size:
        match = re.search(r'([.!?\n])\s', text[:chunk_size][::-1])
        if match:
            last_period_index = chunk_size - match.start() - 1
        else:
            space_index = text[:chunk_size].rfind(' ')
            last_period_index = space_index if space_index != -1 else chunk_size
        
        chunks.append(text[:last_period_index].strip())
        text = text[last_period_index+1:].lstrip()
    
    chunks.append(text.strip())
    return chunks

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(?<=\w)- (?=\w)', '', text)
    text = text.lower()
    return text.strip()

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [{"id": generate_sequential_id(), "text": chunk} for item in data for chunk in chunk_text(item["text"])]

def load_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    text = clean_text(text)
    return [{"id": generate_sequential_id(), "text": chunk} for chunk in chunk_text(text)]

def load_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    text = clean_text(text)
    return [{"id": generate_sequential_id(), "text": chunk} for chunk in chunk_text(text)]

def load_all_files(directory_path):
    all_data = []
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            try:
                data = load_data(file_path)
                all_data.extend(data)
            except Exception as e:
                print(f"Lỗi khi xử lý file {file_path}: {e}")
    return all_data

def load_data(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".json":
        return load_json(file_path)
    elif ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return load_docx(file_path)
    else:
        raise ValueError(f"Định dạng file không được hỗ trợ: {ext}")

def get_embedding(text):
    """Giữ nguyên model embedding theo yêu cầu"""
    client = genai.Client(api_key=config["gemini"]["api_key"])
    result = client.models.embed_content(
        model=embedding_model_name,
        contents=text
    )
    return list(map(float, result.embeddings[0].values))

# Load config
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Kiểm tra nếu đang chạy trong Docker
RUNNING_IN_DOCKER = os.getenv("DOCKERIZED", "false").lower() == "true"

# Chọn host phù hợp
if RUNNING_IN_DOCKER:
    config["qdrant"]["host"] = "http://qdrant:6333"  # Dùng trong Docker
else:
    config["qdrant"]["host"] = "http://localhost:6333"  # Dùng trong Local

embedding_model_name = config["embedding_model"]["name"]

input_path = config['data_input']['path']
datas = load_all_files(input_path)

client = QdrantClient(config["qdrant"]["host"])
collection_name = config["qdrant"]["collection_name"]

client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=config["embedding_model"]["vector_size"], distance=Distance.COSINE),
)
print("Đã tạo collection mới trong Qdrant.")

# 🚀 **Sử dụng đa luồng để xử lý embedding song song**
points = []

def process_item(item):
    """Xử lý embedding cho một item"""
    try:
        embedding = get_embedding(item["text"])
        return PointStruct(id=item["id"], vector=embedding, payload=item)
    except Exception as e:
        print(f"Lỗi khi xử lý embedding: {e}")
        return None  # Trả về None nếu có lỗi

# Dùng ThreadPoolExecutor để tăng tốc độ xử lý
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(process_item, item): item for item in datas}

    for future in tqdm(as_completed(futures), total=len(futures), desc="Embedding dữ liệu"):
        result = future.result()
        if result:
            points.append(result)

# 🚀 **Upsert dữ liệu vào Qdrant theo batch**
if points:
    for i in tqdm(range(0, len(points), 100), desc="Upsert dữ liệu vào Qdrant"):
        batch = points[i:i + 100]
        client.upsert(collection_name=collection_name, points=batch)
    print("Dữ liệu đã được lưu vào Qdrant.")
else:
    print("Không có dữ liệu để upsert vào Qdrant.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_FILE = os.path.join(BASE_DIR, "data_loader_done.flag")

# ✅ Sau khi hoàn tất nạp dữ liệu vào Qdrant, tạo file flag
with open(FLAG_FILE, "w") as f:
    f.write("done")

print(f"✅ Data loading hoàn tất! Flag file được tạo tại: {FLAG_FILE}")