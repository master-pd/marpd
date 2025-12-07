import time
from typing import Dict, List
from collections import defaultdict

class RateLimiter:
    """Rate limiting system"""
    
    def __init__(self):
        self.user_limits = defaultdict(list)
        self.ip_limits = defaultdict(list)
        
        # Rate limit configurations
        self.limits = {
            "messages": {
                "window": 60,  # 60 seconds
                "limit": 30    # 30 messages per minute
            },
            "commands": {
                "window": 60,  # 60 seconds
                "limit": 60    # 60 commands per minute
            },
            "games": {
                "window": 60,  # 60 seconds
                "limit": 20    # 20 games per minute
            },
            "deposits": {
                "window": 3600,  # 1 hour
                "limit": 10     # 10 deposits per hour
            },
            "withdrawals": {
                "window": 86400,  # 24 hours
                "limit": 5       # 5 withdrawals per day
            }
        }
        
        # Temporary bans for excessive violations
        self.temp_bans = {}
    
    def check_limit(self, user_id: int, limit_type: str, ip: str = None) -> Dict:
        """Check rate limit for user"""
        current_time = time.time()
        
        # Clean old entries
        self._clean_old_entries(user_id, limit_type, current_time)
        
        if ip:
            self._clean_old_entries_ip(ip, limit_type, current_time)
        
        # Get limit configuration
        config = self.limits.get(limit_type, {"window": 60, "limit": 30})
        window = config["window"]
        limit = config["limit"]
        
        # Check user limit
        user_key = f"{user_id}_{limit_type}"
        user_timestamps = self.user_limits[user_key]
        
        if len(user_timestamps) >= limit:
            # User exceeded limit
            oldest_request = min(user_timestamps)
            retry_after = int(window - (current_time - oldest_request))
            
            # Track violation
            self._track_violation(user_id, limit_type)
            
            return {
                "allowed": False,
                "limit_type": limit_type,
                "retry_after": retry_after,
                "message": f"⏳ রেট লিমিট! {retry_after} সেকেন্ড পরে চেষ্টা করুন।"
            }
        
        # Check IP limit if provided
        if ip:
            ip_key = f"{ip}_{limit_type}"
            ip_timestamps = self.ip_limits[ip_key]
            
            if len(ip_timestamps) >= limit:
                oldest_request = min(ip_timestamps)
                retry_after = int(window - (current_time - oldest_request))
                
                return {
                    "allowed": False,
                    "limit_type": f"ip_{limit_type}",
                    "retry_after": retry_after,
                    "message": f"⏳ IP রেট লিমিট! {retry_after} সেকেন্ড পরে চেষ্টা করুন।"
                }
        
        # Allow request
        user_timestamps.append(current_time)
        
        if ip:
            ip_timestamps.append(current_time)
        
        return {
            "allowed": True,
            "remaining": limit - len(user_timestamps),
            "reset_in": window
        }
    
    def _clean_old_entries(self, user_id: int, limit_type: str, current_time: float):
        """Clean old entries for user"""
        user_key = f"{user_id}_{limit_type}"
        if user_key in self.user_limits:
            config = self.limits.get(limit_type, {"window": 60, "limit": 30})
            window = config["window"]
            
            # Remove entries older than window
            self.user_limits[user_key] = [
                ts for ts in self.user_limits[user_key]
                if current_time - ts < window
            ]
    
    def _clean_old_entries_ip(self, ip: str, limit_type: str, current_time: float):
        """Clean old entries for IP"""
        ip_key = f"{ip}_{limit_type}"
        if ip_key in self.ip_limits:
            config = self.limits.get(limit_type, {"window": 60, "limit": 30})
            window = config["window"]
            
            # Remove entries older than window
            self.ip_limits[ip_key] = [
                ts for ts in self.ip_limits[ip_key]
                if current_time - ts < window
            ]
    
    def _track_violation(self, user_id: int, limit_type: str):
        """Track rate limit violations"""
        violation_key = f"{user_id}_violations"
        
        if violation_key not in self.temp_bans:
            self.temp_bans[violation_key] = {
                "count": 0,
                "last_violation": time.time(),
                "temp_banned_until": 0
            }
        
        violation_data = self.temp_bans[violation_key]
        current_time = time.time()
        
        # Reset count if last violation was more than 1 hour ago
        if current_time - violation_data["last_violation"] > 3600:
            violation_data["count"] = 1
        else:
            violation_data["count"] += 1
        
        violation_data["last_violation"] = current_time
        
        # Apply temporary ban for excessive violations
        if violation_data["count"] >= 5:
            ban_duration = min(3600 * (violation_data["count"] - 4), 86400)  # Max 24 hours
            violation_data["temp_banned_until"] = current_time + ban_duration
            
            print(f"🚨 Temp ban for {user_id}: {ban_duration} seconds")
    
    def is_temp_banned(self, user_id: int) -> Dict:
        """Check if user is temporarily banned"""
        violation_key = f"{user_id}_violations"
        
        if violation_key in self.temp_bans:
            ban_data = self.temp_bans[violation_key]
            current_time = time.time()
            
            if current_time < ban_data["temp_banned_until"]:
                time_left = int(ban_data["temp_banned_until"] - current_time)
                
                return {
                    "banned": True,
                    "time_left": time_left,
                    "message": f"🚫 টেম্পোরারি ব্যান! {time_left} সেকেন্ড পরে চেষ্টা করুন।"
                }
            else:
                # Ban expired, reset
                ban_data["count"] = 0
                ban_data["temp_banned_until"] = 0
        
        return {"banned": False, "time_left": 0}
    
    def clear_limits(self, user_id: int = None, ip: str = None):
        """Clear rate limits for user or IP"""
        if user_id:
            # Clear all limits for user
            keys_to_remove = [k for k in self.user_limits.keys() if k.startswith(f"{user_id}_")]
            for key in keys_to_remove:
                del self.user_limits[key]
            
            # Clear violations
            violation_key = f"{user_id}_violations"
            if violation_key in self.temp_bans:
                del self.temp_bans[violation_key]
            
            print(f"🧹 Cleared rate limits for user {user_id}")
        
        if ip:
            # Clear all limits for IP
            keys_to_remove = [k for k in self.ip_limits.keys() if k.startswith(f"{ip}_")]
            for key in keys_to_remove:
                del self.ip_limits[key]
            
            print(f"🧹 Cleared rate limits for IP {ip}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get rate limit statistics for user"""
        stats = {}
        
        for limit_type in self.limits:
            user_key = f"{user_id}_{limit_type}"
            
            if user_key in self.user_limits:
                config = self.limits[limit_type]
                current_count = len(self.user_limits[user_key])
                
                stats[limit_type] = {
                    "current": current_count,
                    "limit": config["limit"],
                    "remaining": config["limit"] - current_count,
                    "window": config["window"]
                }
        
        # Check temp ban status
        ban_status = self.is_temp_banned(user_id)
        if ban_status["banned"]:
            stats["temp_banned"] = {
                "time_left": ban_status["time_left"],
                "message": ban_status["message"]
            }
        
        return stats
    
    def update_limit(self, limit_type: str, window: int, limit: int):
        """Update rate limit configuration"""
        self.limits[limit_type] = {
            "window": window,
            "limit": limit
        }
        print(f"⚙️ Updated limit {limit_type}: {limit} per {window} seconds")
    
    def get_all_limits(self) -> Dict:
        """Get all rate limit configurations"""
        return self.limits.copy()