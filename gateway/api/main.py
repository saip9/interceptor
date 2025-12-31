from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import os

# Set up logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the FastAPI
app = FastAPI(title="Interceptor",
              description="API Security Gateway with Behavior Analysis",
              version="1.0.0",
              docs_url="/api/docs",
)

# Add the CORS middleware (allows dashboard to connect)
app.add_middleware(
    CORSMiddleware,
    # React dashboard
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Starting up and shutting down interceptor tool

@app.on_event("startup")
async def startup_event():
    """Run when the application starts"""
    logger.info("=" * 50)
    logger.info("Interceptor Gateway Starting Up")
    logger.info("=" * 50)
    # TODO: Initialize database connections
    logger.info("Gateway ready to accept requests")

@app.on_event("shutdown")
async def shutdown_event():
    """Run when the application shuts down"""
    logger.info("Interceptor Gateway Shutting Down")
    # TODO: Close database connections


# Basic Endpoint

@app.get("/")
async def root():
    """Root endpoint - welcome message"""
    return {
        "message": "Welcome to Interceptor Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "interceptor-gateway",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/test")
async def test_endpoint(request: Request):
    """Test endpoint to verify gateway is working"""
    return {
        "message": "Gateway is working!",
        "client_ip": request.client.host,
        "path": request.url.path,
        "method": request.method,
        "timestamp": datetime.utcnow().isoformat()
    }

