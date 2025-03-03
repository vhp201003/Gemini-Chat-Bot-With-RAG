from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import os
import re
import yaml
import json
import pdfplumber  # Sử dụng pdfplumber thay vì PyPDF2 để đọc PDF
import docx
import hashlib

# Định nghĩa kích thước chunk tối đa
CHUNK_SIZE = 200

# Hàm chunking thông minh
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
        # Tìm dấu câu gần nhất (".", "!", "?", "\n") để cắt
        match = re.search(r'([.!?\n])\s', text[:chunk_size][::-1])
        if match:
            last_period_index = chunk_size - match.start() - 1
        else:
            # Nếu không tìm thấy dấu câu, tìm khoảng trắng gần nhất để cắt
            space_index = text[:chunk_size].rfind(' ')
            last_period_index = space_index if space_index != -1 else chunk_size
        
        chunks.append(text[:last_period_index].strip())  # Cắt chunk
        text = text[last_period_index+1:].lstrip()  # Cập nhật phần còn lại
    
    chunks.append(text.strip())  # Thêm phần còn lại của văn bản
    return chunks

# Hàm chuẩn hóa văn bản (loại bỏ khoảng trắng dư thừa, xử lý từ bị tách)
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Thay thế nhiều khoảng trắng bằng 1 khoảng trắng
    text = re.sub(r'(?<=\w)- (?=\w)', '', text)  # Xử lý từ bị tách ở cuối dòng
    text = text.lower()
    return text.strip()

# Hàm đọc file JSON
def load_json(file_path):
    global global_id_counter
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    filename = os.path.basename(file_path)
    return [{"id": generate_sequential_id(), "text": chunk} for idx, item in enumerate(data) for chunk in chunk_text(item["text"])]

def load_pdf(file_path):
    global global_id_counter
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    text = clean_text(text)
    filename = os.path.basename(file_path)
    return [{"id": generate_sequential_id(), "text": chunk} for idx, chunk in enumerate(chunk_text(text))]

def load_docx(file_path):
    global global_id_counter
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    text = clean_text(text)
    filename = os.path.basename(file_path)
    return [{"id": generate_sequential_id(), "text": chunk} for idx, chunk in enumerate(chunk_text(text))]

# Hàm đọc toàn bộ file trong thư mục
def load_all_files(directory_path):
    all_data = []
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            try:
                data = load_data(file_path)
                print(data, sep = "\n")
                all_data.extend(data)
            except Exception as e:
                print(f"Lỗi khi xử lý file {file_path}: {e}")
    return all_data

# Xác định loại file và tải dữ liệu
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

# Load config
with open(r"../config.yaml", "r") as f:
    config = yaml.safe_load(f)

input_path = config['data_input']['path']

# Load dữ liệu từ tất cả các file trong thư mục
datas = load_all_files(input_path)

# Kết nối Qdrant
client = QdrantClient(config["qdrant"]["host"])
collection_name = config["qdrant"]["collection_name"]

# Load model embedding
embedding_model = SentenceTransformer(config["embedding_model"]["name"], trust_remote_code=True)

# Tạo collection nếu chưa có
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=config["embedding_model"]["vector_size"], distance=Distance.COSINE),
)

# Chuyển văn bản thành vector và lưu vào Qdrant
points = [
    PointStruct(id=item["id"], vector=embedding_model.encode(item["text"]).tolist(), payload=item)
    for item in datas
]

client.upsert(collection_name=collection_name, points=points)
print("Dữ liệu đã được lưu vào Qdrant.")
