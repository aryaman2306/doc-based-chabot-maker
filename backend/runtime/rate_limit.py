import time
from threading import Lock

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


# agent_id -> TokenBucket
_AGENT_BUCKETS = {}

def allow_request(agent_id: str,
                  capacity: int = 10,
                  refill_rate: float = 0.2) -> bool:
    """
    capacity=10  → burst
    refill_rate=0.2 → 1 request per 5 sec sustained
    """
    if agent_id not in _AGENT_BUCKETS:
        _AGENT_BUCKETS[agent_id] = TokenBucket(capacity, refill_rate)

    return _AGENT_BUCKETS[agent_id].consume()

