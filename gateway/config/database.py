import os
from cassandra.cluster import Cluster
import redis
import logging

# Logger here is used throughout this file to record messages
# Each file needs its own logger instance (thats why you see it in other files)

logger = logging.getLogger(__name__)

# Global connection instances
redis_client = None
cassandra_session = None
cassandra_cluster = None


# Redis Connection

def get_redis_client():
    global redis_client

    if redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        logger.info(f"Connecting to Redis at {redis_url}")
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True, # By default returns bytes, we want strings
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test connection
        redis_client.ping()
        logger.info("Connected to Redis")
    return redis_client



# Cassandra Connection

def get_cassandra_session():
    """Get or create Cassandra session"""
    global cassandra_session, cassandra_cluster
    
    if cassandra_session is None:
        hosts = os.getenv("CASSANDRA_HOSTS", "localhost").split(",")
        
        cassandra_cluster = Cluster(
            contact_points=hosts,
            port=9042
        )
        cassandra_session = cassandra_cluster.connect()
        
        # Create keyspace if it doesn't exist
        cassandra_session.execute("""
            CREATE KEYSPACE IF NOT EXISTS interceptor
            WITH replication = {
                'class': 'SimpleStrategy',
                'replication_factor': 1
            }
        """)
        
        # Use the keyspace
        cassandra_session.set_keyspace("interceptor")
        
        logger.info("Connected to Cassandra")
    
    return cassandra_session


# Initialize Redis and Cassandra Connection

def init_databases():
    logger.info("Initializing database connections...")

    try:
        get_redis_client()
        get_cassandra_session()

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Cleanup and closures of database connections

def close_databases():
    """Close all database connections"""
    global redis_client, cassandra_session, cassandra_cluster
    
    if redis_client:
        redis_client.close()
        logger.info("Closed Redis connection")

    if cassandra_cluster:
        cassandra_cluster.shutdown()
        cassandra_session = None
        logger.info("Closed Cassandra connection")
