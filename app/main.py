from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from app.routers import assessment

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="O-1A Visa Qualification Assessment API",
    description="API for assessing O-1A visa qualification based on CV analysis",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assessment.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "O-1A Visa Qualification Assessment API",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    # In a real application, log the error here
    return JSONResponse(
        status_code=500,
        content={"message": f"An unexpected error occurred: {str(exc)}"},
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)