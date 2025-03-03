from fastapi import FastAPI
from .retrieval import search_answer
from .generator import generate_response

app = FastAPI()

@app.post("/chat")
async def chatbot(query: str):
    retrieved_text = search_answer(query)
    final_response = generate_response(retrieved_text)
    return {"response": final_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
