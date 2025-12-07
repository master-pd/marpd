import time
from typing import Any, Dict, Optional
import threading

class Cache:
    """Simple in-memory cache system"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value"""
        with self.lock:
            expire_time = time.time() + (ttl or self.default_ttl)
            self.cache[key] = {
                "value": value,
                "expires": expire_time,
                "created": time.time()
            }
            return True
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                
                # Check if expired
                if time.time() > item["expires"]:
                    del self.cache[key]
                    return None
                
                return item["value"]
            
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache key"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        with self.lock:
            if key in self.cache:
                # Check if expired
                if time.time() > self.cache[key]["expires"]:
                    del self.cache[key]
                    return False
                return True
            return False
    
    def clear(self) -> int:
        """Clear all cache"""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            return count
    
    def ttl(self, key: str) -> Optional[float]:
        """Get remaining TTL for key"""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                remaining = item["expires"] - time.time()
                return max(0, remaining)
            return None
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            self._cleanup_expired()
            time.sleep(60)  # Cleanup every minute
    
    def _cleanup_expired(self):
        """Remove expired cache items"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, item in self.cache.items()
                if current_time > item["expires"]
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                print(f"🧹 Cleaned {len(expired_keys)} expired cache items")
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            current_time = time.time()
            active_items = 0
            expired_items = 0
            total_size = 0
            
            for item in self.cache.values():
                if current_time > item["expires"]:
                    expired_items += 1
                else:
                    active_items += 1
                    # Estimate size (rough)
                    total_size += len(str(item["value"]))
            
            return {
                "total_items": len(self.cache),
                "active_items": active_items,
                "expired_items": expired_items,
                "memory_usage_kb": total_size / 1024,
                "default_ttl": self.default_ttl
            }
    
    def get_or_set(self, key: str, getter_func, ttl: Optional[int] = None) -> Any:
        """Get value or set if not exists"""
        value = self.get(key)
        
        if value is None:
            value = getter_func()
            self.set(key, value, ttl)
        
        return value
    
    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Increment cache value"""
        with self.lock:
            current = self.get(key)
            
            if current is None:
                new_value = amount
            elif isinstance(current, (int, float)):
                new_value = current + amount
            else:
                raise ValueError("Cannot increment non-numeric value")
            
            self.set(key, new_value, ttl)
            return new_value
    
    def decrement(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Decrement cache value"""
        return self.increment(key, -amount, ttl)
    
    def keys(self, pattern: str = "*") -> list:
        """Get cache keys matching pattern"""
        with self.lock:
            all_keys = list(self.cache.keys())
            
            if pattern == "*":
                return all_keys
            
            # Simple pattern matching (supports * at end)
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                return [k for k in all_keys if k.startswith(prefix)]
            
            return [k for k in all_keys if k == pattern]