from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import init_databases, close_databases, get_redis_client



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
    
    try:
        # Initialize database connections
        init_databases()
        logger.info("Gateway ready to accept requests")
    except Exception as e:
        logger.error(f"Failed to start gateway: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Run when the application shuts down"""
    logger.info("Interceptor Gateway Shutting Down")
    close_databases()
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
    """Health check endpoint - tests all database connections"""
    health_status = {
        "status": "healthy",
        "service": "interceptor-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "databases": {}
    }
    
    # Check Redis (INSIDE the function)
    try:
        redis_client = get_redis_client()
        logging.debug("Pinging Redis...")
        redis_client.ping()
        health_status["databases"]["redis"] = "connected"   
    except Exception as e:
        health_status["databases"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check Cassandra
    try:
        from config.database import get_cassandra_session
        session = get_cassandra_session()
        session.execute("SELECT release_version FROM system.local")
        health_status["databases"]["cassandra"] = "connected"
    except Exception as e:
        health_status["databases"]["cassandra"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check MySQL

    try:
        from config.database import get_mysql_connection
        connection = get_mysql_connection
        #connection.close()
        health_status["databases"]["mysql"] = "connected"
    except Exception as e:
        health_status["databases"]["mysql"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Return at the end of the function
    return health_status


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