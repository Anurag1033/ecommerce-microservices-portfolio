import redis
from contextlib import contextmanager
from src.config import Config

# Initialize a singleton Redis client
redis_client = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)

@contextmanager
def acquire_product_lock(product_id: str, lock_timeout: int = 10):
    """
    Creates a distributed lock for a specific product ID.
    Prevents race conditions when multiple orders try to buy the same item simultaneously.
    """
    lock_name = f"lock:product:{product_id}"
    # Creates a lock object. If the process crashes, the lock auto-expires after 10 seconds.
    lock = redis_client.lock(lock_name, timeout=lock_timeout)
    
    # Block for up to 5 seconds waiting for the lock to become available
    acquired = lock.acquire(blocking=True, blocking_timeout=5)
    
    try:
        if not acquired:
            raise TimeoutError(f"Could not acquire lock for {product_id}. System is busy.")
        yield lock
    finally:
        if acquired:
            try:
                lock.release()
            except redis.exceptions.LockError:
                # Lock might have already expired, which is safe to ignore here
                pass