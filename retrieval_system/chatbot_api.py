from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from retrieval_system.retrieval import search_answer
from retrieval_system.generator import generate_response


app = FastAPI()

class ChatRequest(BaseModel):
    query: str

@app.post("/query")
def chat(request: ChatRequest):
    """API nhận câu hỏi và trả về câu trả lời từ chatbot."""
    try:
        # Tìm kiếm dữ liệu trong Qdrant
        context = search_answer(request.query)
        
        # Sinh câu trả lời từ model
        response = generate_response(context, request.query)
        
        return {"query": request.query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")

@app.get("/")
def root():
    return {"message": "Chatbot API đang chạy!"}
