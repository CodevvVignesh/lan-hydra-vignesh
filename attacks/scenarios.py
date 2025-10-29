# attacks/scenarios.py
"""
Predefined attack scenarios for realistic red-team testing.
Based on common automotive attack vectors and MITRE ATT&CK for ICS.
"""
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class AttackScenario:
    """Represents a complete attack scenario"""
    name: str
    description: str
    category: str
    difficulty: str
    duration: int
    config: Dict[str, Any]
    prerequisites: List[str]
    expected_impact: str

class ScenarioLibrary:
    """Library of predefined attack scenarios"""
    
    def __init__(self):
        self.scenarios = self._load_scenarios()
    
    def _load_scenarios(self) -> Dict[str, AttackScenario]:
        """Load all predefined scenarios"""
        scenarios = {}
        
        # Speed Sensor Attacks
        scenarios["speed_spoofing"] = AttackScenario(
            name="Speed Sensor Spoofing",
            description="Spoof speed sensor readings to manipulate vehicle speed display",
            category="Sensor Spoofing",
            difficulty="Easy",
            duration=30,
            config={
                "attack_type": "spoofing",
                "target_id": 0x100,
                "original_value": 50,
                "spoofed_value": 255,
                "interval": 0.1
            },
            prerequisites=["Speed ECU running"],
            expected_impact="Incorrect speed readings, potential safety issues"
        )
        
        scenarios["speed_flooding"] = AttackScenario(
            name="Speed Sensor Flooding",
            description="Flood speed sensor with high-rate messages to cause DoS",
            category="Denial of Service",
            difficulty="Easy",
            duration=15,
            config={
                "attack_type": "flooding",
                "target_id": 0x100,
                "rate": 500.0,
                "interval": 0.002
            },
            prerequisites=["Speed ECU running"],
            expected_impact="ECU overload, potential system freeze"
        )
        
        # Lateral Movement Scenarios
        scenarios["ecu_lateral_movement"] = AttackScenario(
            name="ECU Lateral Movement",
            description="Progressive attack across multiple ECUs to establish persistence",
            category="Lateral Movement",
            difficulty="Medium",
            duration=60,
            config={
                "attack_type": "lateral_movement",
                "target_ids": [0x100, 0x200, 0x300, 0x400],
                "pattern": "escalate",
                "interval": 0.5
            },
            prerequisites=["Multiple ECUs running"],
            expected_impact="Compromise of multiple vehicle systems"
        )
        
        # Replay Attacks
        scenarios["message_replay"] = AttackScenario(
            name="Message Replay Attack",
            description="Replay captured legitimate messages to bypass authentication",
            category="Replay Attack",
            difficulty="Medium",
            duration=45,
            config={
                "attack_type": "replay",
                "log_file": "data/monitor.log",
                "speed_multiplier": 1.5,
                "target_ids": [0x100, 0x200]
            },
            prerequisites=["Captured message log"],
            expected_impact="Bypass security controls, unauthorized actions"
        )
        
        # Advanced Persistent Threat (APT) Simulation
        scenarios["apt_simulation"] = AttackScenario(
            name="APT Simulation",
            description="Simulate advanced persistent threat with multiple attack phases",
            category="Advanced Persistent Threat",
            difficulty="Hard",
            duration=300,
            config={
                "attack_type": "multi_phase",
                "phases": [
                    {"type": "reconnaissance", "duration": 30, "target_ids": [0x100, 0x200, 0x300]},
                    {"type": "initial_access", "duration": 60, "target_id": 0x100, "value": 220},
                    {"type": "lateral_movement", "duration": 120, "target_ids": [0x200, 0x300, 0x400]},
                    {"type": "persistence", "duration": 90, "target_id": 0x500, "interval": 5.0}
                ]
            },
            prerequisites=["Full ECU simulation", "Network monitoring"],
            expected_impact="Complete vehicle system compromise"
        )
        
        # Safety System Attacks
        scenarios["brake_system_attack"] = AttackScenario(
            name="Brake System Manipulation",
            description="Attempt to manipulate brake system messages",
            category="Safety System Attack",
            difficulty="Hard",
            duration=20,
            config={
                "attack_type": "spoofing",
                "target_id": 0x002,  # Brake system ID
                "original_value": 0,
                "spoofed_value": 1,
                "interval": 0.05,
                "safety_warning": True
            },
            prerequisites=["Brake ECU simulation"],
            expected_impact="CRITICAL: Potential brake system compromise"
        )
        
        # Network Segmentation Testing
        scenarios["segmentation_test"] = AttackScenario(
            name="Network Segmentation Test",
            description="Test network segmentation by attempting cross-domain communication",
            category="Network Segmentation",
            difficulty="Medium",
            duration=90,
            config={
                "attack_type": "segmentation_test",
                "domains": [
                    {"name": "powertrain", "ids": [0x100, 0x101, 0x102]},
                    {"name": "body", "ids": [0x200, 0x201, 0x202]},
                    {"name": "infotainment", "ids": [0x300, 0x301, 0x302]}
                ],
                "cross_domain_attempts": True
            },
            prerequisites=["Multi-domain ECU simulation"],
            expected_impact="Validation of network segmentation effectiveness"
        )
        
        return scenarios
    
    def get_scenario(self, name: str) -> AttackScenario:
        """Get a specific scenario by name"""
        if name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {name}")
        return self.scenarios[name]
    
    def list_scenarios(self, category: str = None, difficulty: str = None) -> List[AttackScenario]:
        """List scenarios with optional filtering"""
        filtered = []
        for scenario in self.scenarios.values():
            if category and scenario.category != category:
                continue
            if difficulty and scenario.difficulty != difficulty:
                continue
            filtered.append(scenario)
        return filtered
    
    def get_scenario_info(self, name: str) -> Dict[str, Any]:
        """Get detailed scenario information"""
        scenario = self.get_scenario(name)
        return {
            "name": scenario.name,
            "description": scenario.description,
            "category": scenario.category,
            "difficulty": scenario.difficulty,
            "duration": scenario.duration,
            "prerequisites": scenario.prerequisites,
            "expected_impact": scenario.expected_impact,
            "config": scenario.config
        } 