# CARLA Dataset Creation for XAI Autonomous Driving Research

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![CARLA 0.9.16](https://img.shields.io/badge/CARLA-0.9.16-green.svg)](https://carla.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Research Objective

This repository contains tools for creating autonomous driving datasets using CARLA simulator, specifically designed for **Explainable AI (XAI) research**. The goal is to collect human driving demonstrations and use them to fine-tune language models that can drive autonomously while providing human-like explanations for their decisions.

## 🧠 Research Approach

### **Phase 1: Human Demonstration Collection**
- Record human driving sessions in CARLA simulator
- Capture synchronized video, actions, and timestamps
- Collect diverse driving scenarios naturally through extended sessions

### **Phase 2: LLM Fine-tuning** 
- Process collected data into training samples
- Fine-tune Phi-3-Vision model on human driving patterns
- Train model to predict actions + generate explanations

### **Phase 3: Autonomous Testing**
- Deploy fine-tuned LLM as CARLA driving agent
- Compare LLM driving behavior to original human demonstrations
- Evaluate explanation quality and driving performance

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- CARLA 0.9.16 simulator
- Python 3.12.7
- GTX 1650 or better GPU (see [hardware optimization guide](docs/hardware_optimization.md))

### 1. Clone Repository
```bash
# In your CARLA installation directory
cd CARLA_0.9.16/PythonAPI/examples
git clone https://github.com/MaheAlif/carla-dataset-creation.git .
```

### 2. Setup Environment
```powershell
# Create Python virtual environment
py -3.12 -m venv carla_env

# Activate environment
.\carla_env\Scripts\Activate.ps1

# Install CARLA Python API
pip install path/to/CARLA_0.9.16/PythonAPI/carla/dist/carla-0.9.16-py3.7-win-amd64.egg

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Data Collection
```powershell
# Terminal 1: Start CARLA server
.\CarlaUE4.exe

# Terminal 2: Start recording
.\carla_env\Scripts\Activate.ps1
cd PythonAPI\examples
python record_driving_session.py
```

## 📁 Repository Structure

```
carla-dataset-creation/
├── 📄 README.md                     # This file
├── 📄 requirements.txt              # Python dependencies
├── 📄 config.py                     # Centralized configuration
├── 📄 .gitignore                    # Git ignore rules
├── 🐍 record_driving_session.py     # Main data collection script
├── 🐍 simple_drive.py               # Basic driving script
├── 📄 CARLA_Setup_Guide.md          # Complete setup instructions
├── 📄 conversation_history.md       # Full development conversation
├── 📁 docs/                         # Documentation
│   ├── 📄 research_methodology.md   # Detailed research approach
│   └── 📄 hardware_optimization.md  # Performance optimization
├── 📁 examples/                     # Example outputs
│   └── 📄 sample_output/           # Sample generated files
└── 📁 configs/                      # Additional configurations
```

## 🎮 Usage Guide

### Data Collection Controls
- **W/S**: Throttle/Brake
- **A/D**: Steer left/right  
- **X**: Reverse
- **Space**: Handbrake
- **R**: Start/Stop recording
- **C**: Toggle camera view
- **ESC**: Exit

### Recording Process
1. Start CARLA server
2. Run `record_driving_session.py`
3. Drive around naturally for 30-60 minutes
4. Press 'R' to start/stop recording segments
5. Files automatically saved with sequential naming

### Output Files
Each recording session generates:
- `recording_drive-N.mp4` - Video footage
- `actions_drive-N.json` - Timestamped actions  
- `audio_drive-N.wav` - Audio placeholder

## 🔧 Configuration

### Default Settings
```python
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
NUM_NPC_VEHICLES = 50
NUM_NPC_PEDESTRIANS = 30
FRAME_RATE = 20
```

### GTX 1650 Optimization
```python
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768  
NUM_NPC_VEHICLES = 25
NUM_NPC_PEDESTRIANS = 15
FRAME_RATE = 15
```

See [`config.py`](config.py) for all available settings.

## 📊 Dataset Specifications

- **Target Size**: 200 samples for XAI training
- **Sample Duration**: 5-30 seconds each
- **Video Format**: MP4, 15-20 FPS
- **Action Sampling**: 20Hz (50ms intervals)
- **Data Types**: Video, timestamped actions, metadata

## 🎓 Research Context

This work is part of autonomous driving XAI research focused on:
- **Behavioral Cloning**: Learning from human demonstrations
- **Explainable Decisions**: AI that can reason about its actions
- **Natural Language Explanations**: Human-understandable AI reasoning
- **Temporal Understanding**: Sequential decision-making patterns

## 📚 Documentation

- **[Setup Guide](CARLA_Setup_Guide.md)** - Complete installation and usage
- **[Research Methodology](docs/research_methodology.md)** - Detailed approach
- **[Hardware Optimization](docs/hardware_optimization.md)** - Performance tuning
- **[Conversation History](conversation_history.md)** - Full development context

## 🤝 Reproducibility

This repository is designed for complete reproducibility:
- All dependencies specified in `requirements.txt`
- Configuration centralized in `config.py`
- Complete setup instructions included
- Development history preserved in `conversation_history.md`

### On a New PC:
1. Download CARLA 0.9.16
2. Clone this repository
3. Follow `CARLA_Setup_Guide.md`
4. Start collecting data immediately

## 💡 Key Features

### ✅ **Human-Centered Data Collection**
- Natural driving scenarios (no scripted behaviors)
- Continuous recording for rich temporal data
- Automatic timestamping and action logging

### ✅ **Research-Ready Output**
- Synchronized video and action data
- JSON format for easy processing
- Sequential file naming for organization

### ✅ **Hardware Optimized**
- GTX 1650 compatible settings
- Configurable performance parameters
- Real-time performance monitoring

### ✅ **Professional Development**
- Version controlled research code
- Complete documentation
- Reproducible environment setup

## 🔬 Next Steps

1. **Data Collection**: Record 30-60 minute driving sessions
2. **Data Processing**: Segment recordings into training samples
3. **Model Training**: Fine-tune Phi-3-Vision on collected data
4. **Autonomous Testing**: Deploy trained model in CARLA
5. **Evaluation**: Compare AI vs human driving patterns

## 📈 Expected Contributions

- **Novel XAI Dataset**: Human driving with natural explanations
- **Behavioral Cloning Pipeline**: End-to-end autonomous driving training
- **Explainable AI Driver**: Language model that reasons about driving
- **Open Research Tools**: Reproducible CARLA-based data collection

## 🐛 Troubleshooting

### Common Issues:
- **"No module named carla"**: Activate carla_env first
- **Low FPS**: Reduce NPCs and resolution in config.py
- **Connection timeout**: Ensure CARLA server is fully loaded
- **Black pygame window**: Click on window and check it's in foreground

See [CARLA_Setup_Guide.md](CARLA_Setup_Guide.md) for detailed troubleshooting.

## 📧 Contact

For questions about this research or collaboration opportunities, please open an issue or refer to the conversation history for development context.

## 📜 License

MIT License - See LICENSE file for details.

---

**Happy Researching!** 🚗🤖 This toolset is designed to make autonomous driving XAI research accessible and reproducible. Drive safely (even in simulation)!