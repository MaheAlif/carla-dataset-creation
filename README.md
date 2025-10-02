# CARLA Dataset Creation for XAI Autonomous Driving Research

**🎯 Research Goal**: Create human driving demonstrations in CARLA simulator for fine-tuning explainable AI models that can drive autonomously while providing human-like reasoning.

## 🚀 Quick Setup on New PC

### 1. Download CARLA
```bash
# Download CARLA 0.9.16 from official website
# Extract to desired location (e.g., E:\CARLA_Latest)
```

### 2. Clone This Repository
```bash
# Navigate to your CARLA installation
cd E:\CARLA_Latest

# Clone research code directly into CARLA folder
git clone https://github.com/MaheAlif/carla-dataset-creation.git .
```

### 3. Follow Setup Guide
```bash
# Complete setup instructions are in:
# CARLA_Setup_Guide.md
```

## 📁 What You Get

After cloning, your CARLA folder will contain:

### **Original CARLA Files** (excluded from Git)
- `CarlaUE4.exe` - CARLA simulator
- `Engine/`, `HDMaps/` - CARLA assets
- `PythonAPI/carla/` - CARLA Python API

### **Research Code** (tracked in Git)
- `PythonAPI/examples/record_driving_session.py` - Main data collection script
- `PythonAPI/examples/config.py` - Hardware-optimized settings
- `PythonAPI/examples/setup_validation.py` - Environment verification
- `CARLA_Setup_Guide.md` - Complete setup instructions
- `docs/` - Research methodology and optimization guides

## 🎮 Usage

1. **Start CARLA Server**: `.\CarlaUE4.exe`
2. **Activate Environment**: `.\carla_env\Scripts\Activate.ps1`
3. **Start Recording**: `python PythonAPI\examples\record_driving_session.py`
4. **Drive & Record**: Use WASD to drive, R to start/stop recording

## 📊 Research Pipeline

### Phase 1: Data Collection *(Current)*
- Record human driving demonstrations
- Capture synchronized video + timestamped actions
- Generate 200+ training samples

### Phase 2: Model Training *(Next)*
- Fine-tune Phi-3-Vision on human demonstrations
- Train for action prediction + explanation generation

### Phase 3: Autonomous Testing *(Future)*
- Deploy trained model as CARLA driving agent
- Compare AI vs human driving patterns
- Evaluate explanation quality

## 🔧 Hardware Requirements

- **Minimum**: GTX 1650, 16GB RAM, Windows 10/11
- **Recommended**: GTX 1660+, 32GB RAM, SSD storage
- **Optimized**: Settings included for mid-range hardware

## 📚 Documentation

- **[Setup Guide](CARLA_Setup_Guide.md)** - Step-by-step installation
- **[Research Methodology](PythonAPI/examples/docs/research_methodology.md)** - Detailed approach
- **[Hardware Optimization](PythonAPI/examples/docs/hardware_optimization.md)** - Performance tuning
- **[Conversation History](PythonAPI/examples/conversation_history.md)** - Complete development context

## 🎓 Research Context

This repository enables reproduction of XAI autonomous driving research across different computers. The complete conversation history and methodology are preserved to ensure continuity and understanding of the research approach.

**Key Innovation**: Learning explainable driving decisions from natural human demonstrations rather than scripted scenarios.

---

**Ready to start collecting data for XAI autonomous driving research!** 🚗🤖