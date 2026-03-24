import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.evaluate import router as evaluate_router
import re

load_dotenv()

app = FastAPI(
    title="AI Hiring Evaluator (NLP Base)",
    description="An API that uses traditional NLP (TF-IDF, Spacy, Keyword Mapping) to evaluate candidates.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def sanitize_json_request(request: Request, call_next):
    """
    Middleware that intercepts raw JSON requests and cleans invalid control characters
    (like literal newlines and tabs) BEFORE they reach the JSON parser and cause
    a 422 Unprocessable Content error.
    """
    if request.method in ["POST", "PUT", "PATCH"] and "application/json" in request.headers.get("content-type", ""):
        try:
            body_bytes = await request.body()
            if body_bytes:
                # Decode the raw bytes to string
                body_str = body_bytes.decode('utf-8')
                
                # Replace actual literal control characters (newline, carriage return, tab)
                # with spaces, which prevents the JSON decode error.
                cleaned_body_str = body_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                
                cleaned_bytes = cleaned_body_str.encode('utf-8')
                
                # Overwrite both the cached body and the receive stream
                # because Starlette caches await request.body() internally in request._body
                request._body = cleaned_bytes
                
                async def receive():
                    return {"type": "http.request", "body": cleaned_bytes}
                request._receive = receive
        except Exception:
            pass # Pass through to the default error handlers

    return await call_next(request)

@app.get("/")
def root():
    return {
        "message": "Welcome to the AI Hiring Evaluator API.",
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Hiring Evaluation Service is running"}

app.include_router(evaluate_router, tags=["Evaluaton"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    print(f"Server is running on port {port}")
    print(f"Swagger Documentation: http://localhost:{port}/docs")
    print(f"Health check: http://localhost:{port}/health")
    print(f"Evaluation Endpoint: POST http://localhost:{port}/generate-report")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
