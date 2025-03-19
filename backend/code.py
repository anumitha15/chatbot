import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import threading

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# PDF Processing Functions
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
    return text_splitter.split_text(text)

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    return ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)

# Streamlit Chatbot UI
def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def run_streamlit():
    st.set_page_config(page_title="Chat with multiple PDFs", page_icon="📚")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with multiple PDFs 📚")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader("Upload your PDFs and click 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)
                st.session_state.conversation = get_conversation_chain(vectorstore)

# FastAPI Model & Endpoint
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    if "conversation" not in st.session_state or not st.session_state.conversation:
        return {"error": "No conversation context found. Please upload PDFs first."}
    
    response = st.session_state.conversation({'question': request.message})
    return {"reply": response['chat_history'][-1].content}

# Run FastAPI and Streamlit concurrently
def run_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_fastapi, daemon=True).start()
    run_streamlit()
