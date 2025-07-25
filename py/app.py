from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from langchain_pinecone import PineconeVectorStore
from langchain_ollama.llms import OllamaLLM
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import uvicorn
from werkzeug.utils import secure_filename
from store_index import load_data 
from helper import download_hugging_face_embeddings

# Tải các biến môi trường
load_dotenv()

# Cấu hình thư mục tải lên
UPLOAD_FOLDER = "Data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Gắn các tệp tĩnh (CSS, JS, Images)
# Điều này giả định bạn có một thư mục 'css' trong cùng thư mục gốc với app.py
# và tệp chat.html tham chiếu đến tệp CSS bằng đường dẫn '/css/chat.css'
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/Js", StaticFiles(directory="Js"), name="Js")
app.mount("/image", StaticFiles(directory="image"), name="image")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname('bai_tap_lon_js'), "html"))




PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

embeddings = download_hugging_face_embeddings()
index_name = "chatbot"  

# Kết nối với chỉ mục Pinecone hiện có
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

# Tạo retriever
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Mẫu hệ thống cho chuỗi RAG
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

# Khởi tạo mô hình ngôn ngữ
llm = OllamaLLM(model='llama3.2')

# Tạo mẫu trò chuyện
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# Tạo các chuỗi LangChain
Youtube_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, Youtube_chain)



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Lưu tệp tải lên
        with open(filepath, "wb") as buffer:
            content = await file.read()  # Đọc nội dung tệp một cách bất đồng bộ
            buffer.write(content)

        # Xử lý và lập chỉ mục dữ liệu (cuộc gọi này là đồng bộ)
        load_data()

        return JSONResponse(content={"message": f"{filename} uploaded and indexed successfully!"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/index.html")
async def get_index_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat.html")
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/get")
async def chat(msg: str = Form(...)):
    try:
        
        response = await rag_chain.ainvoke({"input": msg})
        answer = response.get("answer", "Sorry, I could not process an answer.")
        print(f"Input: {msg}")
        print(f"Response: {answer}")

        return PlainTextResponse(content=answer)
    except Exception as e:
        print(f"Error during chat: {e}")
        return PlainTextResponse(content="An error occurred while processing your request.", status_code=500)



if __name__ == '__main__':
    uvicorn.run("app:app",  host="127.0.0.1", port=8000, reload=True)