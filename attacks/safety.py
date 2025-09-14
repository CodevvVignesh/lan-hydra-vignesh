# attacks/safety.py
"""
Safety and validation module for LAN Hydra attacks.
Provides rate limiting, attack validation, and safety checks.
"""
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class SafetyLimits:
    """Safety limits for attack operations"""
    max_messages_per_second: int = 1000
    max_duration_minutes: int = 60
    max_concurrent_attacks: int = 5
    dangerous_can_ids: List[int] = None
    
    def __post_init__(self):
        if self.dangerous_can_ids is None:
            # Critical CAN IDs that should be protected
            self.dangerous_can_ids = [
                0x000,  # Engine control
                0x001,  # Transmission
                0x002,  # Brake system
                0x003,  # Steering
                0x100,  # Speed sensor
                0x200,  # Safety systems
            ]

class AttackValidator:
    """Validates attack parameters for safety"""
    
    def __init__(self, limits: SafetyLimits = None):
        self.limits = limits or SafetyLimits()
        self.active_attacks = {}
        
    def validate_attack(self, attack_config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate attack configuration for safety.
        Returns (is_valid, error_message)
        """
        # Check duration
        duration = attack_config.get("duration", 0)
        if duration > self.limits.max_duration_minutes * 60:
            return False, f"Duration {duration}s exceeds maximum {self.limits.max_duration_minutes} minutes"
            
        # Check CAN ID safety
        can_id = attack_config.get("id")
        if can_id and can_id in self.limits.dangerous_can_ids:
            return False, f"CAN ID 0x{can_id:x} is in dangerous IDs list"
            
        # Check message rate
        interval = attack_config.get("interval", 0.1)
        rate = 1.0 / interval if interval > 0 else 0
        if rate > self.limits.max_messages_per_second:
            return False, f"Message rate {rate:.1f} msg/s exceeds maximum {self.limits.max_messages_per_second}"
            
        # Check concurrent attacks
        if len(self.active_attacks) >= self.limits.max_concurrent_attacks:
            return False, f"Too many concurrent attacks ({len(self.active_attacks)}/{self.limits.max_concurrent_attacks})"
            
        return True, ""
    
    def register_attack(self, attack_id: str, config: Dict[str, Any]):
        """Register an active attack"""
        self.active_attacks[attack_id] = {
            "config": config,
            "start_time": time.time(),
            "thread": threading.current_thread()
        }
    
    def unregister_attack(self, attack_id: str):
        """Unregister a completed attack"""
        if attack_id in self.active_attacks:
            del self.active_attacks[attack_id]

class RateLimiter:
    """Rate limiter for CAN message injection"""
    
    def __init__(self, max_rate: float = 100.0):
        self.max_rate = max_rate
        self.last_send_time = 0
        self.min_interval = 1.0 / max_rate
        
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_send_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_send_time = time.time()

class AttackLogger:
    """Enhanced logging for attack analysis"""
    
    def __init__(self, log_file: str = "data/attack_log.json"):
        self.log_file = log_file
        self.session_id = int(time.time())
        
    def log_attack_start(self, attack_type: str, config: Dict[str, Any]):
        """Log attack start"""
        log_entry = {
            "session_id": self.session_id,
            "timestamp": time.time(),
            "event": "attack_start",
            "attack_type": attack_type,
            "config": config
        }
        self._write_log(log_entry)
        
    def log_attack_end(self, attack_type: str, success: bool, message_count: int = 0):
        """Log attack end"""
        log_entry = {
            "session_id": self.session_id,
            "timestamp": time.time(),
            "event": "attack_end",
            "attack_type": attack_type,
            "success": success,
            "message_count": message_count
        }
        self._write_log(log_entry)
        
    def log_message_sent(self, can_id: int, payload: bytes, success: bool):
        """Log individual message"""
        log_entry = {
            "session_id": self.session_id,
            "timestamp": time.time(),
            "event": "message_sent",
            "can_id": f"0x{can_id:x}",
            "payload": payload.hex(),
            "success": success
        }
        self._write_log(log_entry)
        
    def _write_log(self, log_entry: dict):
        """Write log entry to file"""
        import json
        import os
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

class SafetyManager:
    """Central safety management for all attacks"""
    
    def __init__(self):
        self.validator = AttackValidator()
        self.rate_limiter = RateLimiter()
        self.logger = AttackLogger()
        self.emergency_stop = threading.Event()
        
    def validate_and_log_attack(self, attack_type: str, config: Dict[str, Any]) -> tuple[bool, str]:
        """Validate attack and log start"""
        is_valid, error_msg = self.validator.validate_attack(config)
        
        if is_valid:
            attack_id = f"{attack_type}_{int(time.time())}"
            self.validator.register_attack(attack_id, config)
            self.logger.log_attack_start(attack_type, config)
            return True, attack_id
        else:
            return False, error_msg
            
    def log_attack_completion(self, attack_id: str, attack_type: str, success: bool, message_count: int = 0):
        """Log attack completion"""
        self.validator.unregister_attack(attack_id)
        self.logger.log_attack_end(attack_type, success, message_count)
        
    def emergency_stop_all(self):
        """Emergency stop all attacks"""
        self.emergency_stop.set()
        print("EMERGENCY STOP ACTIVATED - All attacks will be terminated")
        
    def is_emergency_stop(self) -> bool:
        """Check if emergency stop is active"""
        return self.emergency_stop.is_set() 