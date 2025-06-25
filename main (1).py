from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, chat

# Initialize FastAPI app
app = FastAPI(
    title="Police Assistance Chatbot API",
    description="APIs for document upload, vector search, and chatbot queries.",
    version="1.0.0",
)

# CORS Middleware (Allows frontend to access backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(upload.router, tags=["Document Upload"])
app.include_router(chat.router, tags=["Chat"])
# app.include_router(history.router, tags=["Chat History"])

# Root Endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Police Assistance Chatbot API!"}
