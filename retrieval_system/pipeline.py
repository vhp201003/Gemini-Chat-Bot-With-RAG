from retrieval import search_answer
from generator import generate_response

def chatbot_pipeline():
    print("Chabot đang chạy... Gõ 'exit' để thoát.")

    while True:
        query = input("\nBạn: ")
        if query.lower() == "exit":
            print("👋 Tạm biệt!")
            break

        # Tìm kiếm ngữ cảnh liên quan từ Qdrant
        context = search_answer(query)
        
        # Nếu không có dữ liệu phù hợp, trả lời mặc định
        response = generate_response(context, query)
        print(f"🤖 Chatbot: {response}")

if __name__ == "__main__":
    chatbot_pipeline()
