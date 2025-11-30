# LAN Hydra - Internal Threat Simulation Toolkit for Vehicle Networks

![LAN Hydra](https://img.shields.io/badge/LAN%20Hydra-CAN%20Security-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Security](https://img.shields.io/badge/Security-Red%20Team-orange)

## 🚗 Overview

LAN Hydra is a comprehensive red-team toolkit designed to simulate internal attacks on vehicle networks, specifically targeting CAN (Controller Area Network) systems. This toolkit helps Original Equipment Manufacturers (OEMs) and security researchers validate internal network segmentation and intrusion response capabilities.

## 🎯 Problem Statement

Internal vehicle networks (CAN, LIN, automotive Ethernet) operate under a "trusted" assumption but often lack strong segmentation or encryption. This makes them vulnerable to:

- **Lateral movement** attacks
- **Spoofing** of sensor data  
- **Replay attacks** on captured messages
- **MITM (Man-in-the-Middle)** attacks

## ✨ Features

### Advanced Attack Capabilities
- **CAN Injection**: Multiple injection patterns and payload variations
- **Spoofing Attacks**: Replace legitimate values with malicious ones
- **Replay Attacks**: Replay captured CAN messages to bypass authentication
- **Lateral Movement**: Progressive attacks across multiple ECUs
- **Flooding Attacks**: High-rate message injection for DoS scenarios
- **Fuzzing**: Randomized payload testing

### Safety & Validation
- **Dry-run Mode**: Test attacks safely without sending actual messages
- **Rate Limiting**: Prevent bus overload (max 1000 msg/s)
- **Attack Validation**: Check for dangerous CAN IDs and parameters
- **Emergency Stop**: Immediate termination capability
- **Comprehensive Logging**: Detailed JSON logs for analysis

### Professional CLI Interface
- **Predefined Attack Profiles**: Easy-to-use scenarios for common attacks
- **Advanced Argument Parsing**: Support for complex attack configurations
- **Multiple Attack Types**: Basic, advanced, flooding, fuzzing
- **Real-time Monitoring**: Enhanced CAN bus monitoring with attack detection

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/nithinj25/lan-hydra.git
cd lan-hydra

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install python-can cantools
```

### Basic Usage

```bash
# List available attack profiles
python lanhydra.py list-profiles

# Test safely with dry-run
python lanhydra.py attack --type advanced --attack basic --id 0x100 --value 220 --duration 5 --dry-run

# Run ECU simulation
python lanhydra.py ecu --bustype virtual --interval 1.0

# Monitor CAN bus
python lanhydra.py monitor --bustype virtual

# Execute attack profile
python lanhydra.py profile --name speed_spoof --duration 30
```

## 🎮 Attack Examples

### Speed Sensor Spoofing
```bash
python lanhydra.py attack --type advanced --attack spoof --id 0x100 --spoof-value 255 --original-value 50 --duration 30
```

### Lateral Movement Attack
```bash
python lanhydra.py attack --type advanced --attack lateral --targets 0x100,0x200,0x300 --duration 45 --pattern escalate
```

### Replay Attack
```bash
python lanhydra.py attack --type advanced --attack replay --log-file data/monitor.log --duration 20 --speed 2.0
```

### Flooding Attack
```bash
python lanhydra.py attack --type flooding --id 0x100 --duration 15
```

### Fuzzing Attack
```bash
python lanhydra.py attack --type fuzzing --id 0x100 --duration 20 --interval 0.1
```

## �� Project Structure

```
lan-hydra/
├── lanhydra.py              # Main CLI interface
├── attacks/
│   ├── injection.py         # Advanced injection capabilities
│   ├── safety.py           # Safety and validation
│   ├── scenarios.py        # Predefined attack scenarios
│   └── plugins/            # Attack plugins
├── monitor/
│   └── monitor_bus.py      # CAN bus monitoring
├── ecus/
│   └── speed_ecu.py       # ECU simulation
├── utils/
│   └── can_bus.py         # CAN bus utilities
├── third_party/            # Third-party tools and references
│   └── canbus/            # CAN bus simulator
└── data/                  # Log files and data
```

## 🛠️ Third-Party Tools Integration

### CAN Bus Simulator
LAN Hydra includes a comprehensive CAN bus simulator in the `third_party/canbus/` directory:

```bash
# Setup CAN bus simulator
cd third_party/canbus
sudo ./canup.sh  # Initialize virtual CAN interface
python src/main.py  # Start simulator

# Use with LAN Hydra
cd ../../
python lanhydra.py monitor --bustype socketcan --channel vcan0
python lanhydra.py attack --type advanced --attack basic --id 0x100 --value 220 --duration 10
```

**Features:**
- Multiple ECU node simulation
- Configurable network parameters
- Message signing capabilities
- DDoS attack simulation
- Real-time monitoring

**Integration Benefits:**
- Realistic target network for attack testing
- Validates attack effectiveness
- Provides controlled testing environment
- Supports various attack scenarios

## 🔧 Advanced Usage

### Custom Attack Scenarios
Create custom scenarios by modifying `attacks/scenarios.py`:

```python
custom_scenario = AttackScenario(
    name="Custom Attack",
    description="Your custom attack description",
    category="Custom",
    difficulty="Medium",
    duration=30,
    config={
        "attack_type": "basic",
        "target_id": 0x400,
        "value": 128,
        "interval": 0.1
    },
    prerequisites=["Custom ECU"],
    expected_impact="Custom impact description"
)
```

### Integration with External Tools
The enhanced logging format allows integration with:
- SIEM systems
- Network analysis tools
- Custom monitoring solutions

## 📈 Logging and Analysis

All attacks are logged to `data/injection.log` with:
- Timestamp
- Attack type
- CAN ID and payload
- Success/failure status

Enhanced monitoring logs to `data/enhanced_monitor.log` with:
- All CAN messages
- Attack detection results
- Statistical analysis

## 📚 Third-Party References

### Core Dependencies
- **[python-can](https://github.com/hardbyte/python-can)**: Core CAN bus communication library
- **[cantools](https://github.com/cantools/cantools)**: CAN message parsing and database handling

### Security Research
- **[MITRE ATT&CK for ICS](https://attack.mitre.org/matrices/ics/)**: Industrial Control Systems attack framework
- **[CVE Database](https://cve.mitre.org/)**: Common Vulnerabilities and Exposures database

### Automotive Security Research
- **[Charlie Miller & Chris Valasek](https://illmatics.com/car_hacking.html)**: Pioneering automotive security research
- **[Koscher et al.](https://www.autosec.org/pubs/cars-oakland2010.pdf)**: Foundational automotive security research
- **[Checkoway et al.](https://www.autosec.org/pubs/cars-usenixsec2011.pdf)**: Comprehensive automotive attack analysis

### Tools and Frameworks
- **[CANtact](https://github.com/linklayer/cantact-hw)**: Open-source CAN adapter hardware
- **[SavvyCAN](https://github.com/collin80/SavvyCAN)**: CAN bus analysis and reverse engineering tool
- **[Wireshark](https://www.wireshark.org/)**: Network protocol analyzer

### Standards and Specifications
- **[ISO 11898](https://www.iso.org/standard/63648.html)**: CAN Protocol specification
- **[ISO 21434](https://www.iso.org/standard/70918.html)**: Automotive cybersecurity engineering standard
- **[SAE J3061](https://www.sae.org/standards/content/j3061/)**: Cybersecurity guidebook for cyber-physical vehicle systems

## 🚨 Complete Demo Workflow

### Terminal 1: ECU Simulation
```bash
# Activate virtual environment
source venv/bin/activate

# Start ECU simulation
python lanhydra.py ecu --bustype virtual --interval 1.0
```

### Terminal 2: Monitoring
```bash
# Activate virtual environment
source venv/bin/activate

# Start monitoring
python lanhydra.py monitor --bustype virtual
```

### Terminal 3: Attack Execution
```bash
# Activate virtual environment
source venv/bin/activate

# Run attack
python lanhydra.py attack --type advanced --attack spoof --id 0x100 --spoof-value 255 --original-value 50 --duration 30
```

## 🔍 Attack Scenarios

### Scenario 1: Speed Sensor Spoofing
1. **Setup**: Start ECU simulation with speed sensor (ID 0x100)
2. **Baseline**: Monitor normal speed readings
3. **Attack**: Run spoofing attack with malicious values
4. **Validation**: Verify speed readings are manipulated

### Scenario 2: ECU Flooding
1. **Setup**: Start multiple ECU simulations
2. **Baseline**: Monitor normal message rates
3. **Attack**: Run flooding attack with high-rate messages
4. **Validation**: Check for DoS effects on ECUs

### Scenario 3: Lateral Movement
1. **Setup**: Configure multiple ECU domains
2. **Baseline**: Monitor inter-domain communication
3. **Attack**: Run lateral movement attack
4. **Validation**: Verify cross-domain compromise

## 🤝 Contributing

This project evolved through collaborative feature development. Contributions followed this workflow:

1. **Feature Planning** - Discussed features and architecture
2. **Development** - Create feature branch (`git checkout -b feature/feature-name`)
3. **Implementation** - Build and test the feature
4. **Code Review** - Submit pull request for review
5. **Integration** - Merge approved features into main branch

### Key Contributions Included:
- CAN bus injection core functionality
- Attack module plugins (flooding, fuzzing, injection)
- Docker containerization support  
- Network monitoring capabilities
- ECU simulation tools
- Comprehensive testing suite
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is designed for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before testing any systems. The authors are not responsible for any misuse of this tool.

## 🙏 Acknowledgments

### Research Community
- **Charlie Miller & Chris Valasek** - Pioneering automotive security research
- **Stefan Savage & team** - Comprehensive automotive attack surface analysis
- **Koscher et al.** - Foundational automotive security research
- **Checkoway et al.** - Multi-vector attack analysis

### Open Source Community
- **python-can contributors** - Excellent CAN communication library
- **cantools developers** - Comprehensive CAN message handling
- **CANtact team** - Open-source CAN hardware
- **SavvyCAN developers** - CAN analysis and reverse engineering tools

### Industry Standards
- **ISO/TC 22/SC 32** - Automotive cybersecurity standards
- **SAE International** - Automotive engineering standards
- **NIST Cybersecurity Framework** - Security best practices

## 📞 Contact

- GitHub: [CodevvVignesh](https://github.com/CodevvVignesh)
- Project Link: [https://github.com/CodevvVignesh/lan-hydra-vignesh](https://github.com/CodevvVignesh/lan-hydra-vignesh)

## 🏷️ Repository Topics

- `can-security`
- `automotive-security`
- `red-team`
- `penetration-testing`
- `vehicle-networks`
- `cybersecurity`
- `python`
- `mitre-attack`
- `automotive-research`

---

**⚠️ Use responsibly and only on systems you own or have explicit permission to test.**

**📚 This project builds upon the excellent work of the automotive security research community. Please refer to the third-party references for detailed information about the underlying research and tools.**

**🔒 Always prioritize safety and use dry-run mode extensively before live testing.**

## 📋 **How to Use This Content**

1. **Copy the entire content above**
2. **Create/Edit your README.md file**:
   ```bash
   nano README.md
   ```
3. **Paste the content** (Ctrl+V)
4. **Save and exit** (Ctrl+X, Y, Enter)
5. **Commit to Git**:
   ```bash
   git add README.md
   git commit -m "Add comprehensive README with third-party references and usage examples"
   git push origin main
   ```

## 🎯 **What This README Includes**

✅ **Professional project overview**  
✅ **Complete feature list with safety considerations**  
✅ **Step-by-step installation and usage guide**  
✅ **Comprehensive attack examples**  
✅ **Third-party tools integration**  
✅ **Complete demo workflow**  
✅ **Attack scenarios and validation**  
✅ **Proper attribution to research and tools**  
✅ **Safety warnings and disclaimers**  
✅ **Professional formatting with badges**  
✅ **Repository topics for discoverability**

This README will make your LAN Hydra repository look professional and comprehensive, properly crediting all the third-party tools and research that influenced your project! 🚗🔒📚
