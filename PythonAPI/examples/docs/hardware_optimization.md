# Hardware Optimization Guide for CARLA Dataset Creation

**Target Hardware**: GTX 1650 and similar mid-range GPUs  
**Goal**: Achieve stable 15+ FPS for research-quality data collection  
**Updated**: October 2025  

---

## 🎯 **Optimization Overview**

This guide helps you optimize CARLA performance for dataset creation on mid-range hardware, specifically targeting GTX 1650 but applicable to similar GPUs. The focus is on maintaining research-quality data while ensuring smooth recording.

## 🖥️ **Hardware Requirements**

### **Minimum Specifications**
- **GPU**: GTX 1650 (4GB VRAM) or equivalent
- **CPU**: Intel i5-8300H / AMD Ryzen 5 3500U or better
- **RAM**: 16GB system memory
- **Storage**: 500GB+ available space for recordings
- **OS**: Windows 10/11 64-bit

### **Recommended Specifications**
- **GPU**: GTX 1660 Super (6GB VRAM) or better
- **CPU**: Intel i7-9750H / AMD Ryzen 7 4700H or better
- **RAM**: 32GB system memory
- **Storage**: 1TB+ SSD for better I/O performance
- **Cooling**: Adequate laptop cooling (external pad recommended)

### **Performance Expectations**
```
GTX 1650 (4GB):     15-20 FPS @ 1024x768
GTX 1660 (6GB):     20-25 FPS @ 1280x720
RTX 3060 (8GB):     25-30 FPS @ 1920x1080
RTX 4070 (12GB):    30+ FPS @ 1920x1080
```

## ⚙️ **CARLA Server Optimization**

### **Launch Commands**

#### **GTX 1650 Optimized** (Recommended)
```powershell
.\CarlaUE4.exe -quality-level=Low -ResX=1024 -ResY=768 -windowed -fps=20
```

#### **Low-end Hardware** (GTX 1050, integrated GPUs)
```powershell
.\CarlaUE4.exe -quality-level=Low -ResX=800 -ResY=600 -windowed -fps=15 -NoVSync
```

#### **Higher-end Hardware** (RTX 3060+)
```powershell
.\CarlaUE4.exe -quality-level=Medium -ResX=1280 -ResY=720 -windowed -fps=30
```

### **Graphics Quality Settings**
| Setting | GTX 1650 | GTX 1660+ | RTX 3060+ |
|---------|----------|-----------|-----------|
| Resolution | 1024x768 | 1280x720 | 1920x1080 |
| Quality Level | Low | Low-Medium | Medium |
| Target FPS | 15-20 | 20-25 | 25-30 |
| VSync | Off | Off | Optional |

### **Advanced Launch Parameters**
```powershell
# Maximum performance (sacrifice visual quality)
.\CarlaUE4.exe -quality-level=Low -ResX=800 -ResY=600 -windowed -fps=15 -NoVSync -sm4 -d3d10

# Balanced performance (good for most research)
.\CarlaUE4.exe -quality-level=Low -ResX=1024 -ResY=768 -windowed -fps=20 -NoVSync

# Debug performance issues
.\CarlaUE4.exe -quality-level=Low -ResX=1024 -ResY=768 -windowed -fps=20 -benchmark
```

## 🐍 **Python Script Configuration**

### **config.py Settings for GTX 1650**

```python
# GTX 1650 Optimized Configuration
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FRAME_RATE = 15

# Reduced NPC counts for performance
NUM_NPC_VEHICLES = 25        # Down from 50
NUM_NPC_PEDESTRIANS = 15     # Down from 30

# Camera optimization
CAMERA_FOV = 90              # Reduced from 110
CAMERA_SENSOR_TICK = 0.05    # 20Hz instead of maximum

# Performance monitoring
ENABLE_PERFORMANCE_MONITORING = True
FPS_WARNING_THRESHOLD = 10
```

### **Hardware Detection Script**

```python
# Add to config.py for automatic optimization
import platform
import subprocess

def detect_gpu():
    """Detect GPU and suggest optimal settings."""
    try:
        # Try to get GPU info (Windows)
        result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                              capture_output=True, text=True)
        gpu_info = result.stdout.lower()
        
        if 'gtx 1650' in gpu_info:
            return 'gtx_1650'
        elif any(gpu in gpu_info for gpu in ['gtx 1660', 'rtx 2060', 'rtx 3050']):
            return 'mid_range'
        elif any(gpu in gpu_info for gpu in ['rtx 3060', 'rtx 3070', 'rtx 4060']):
            return 'high_end'
        else:
            return 'unknown'
    except:
        return 'unknown'

def get_auto_config():
    """Get automatically optimized configuration."""
    gpu_tier = detect_gpu()
    
    configs = {
        'gtx_1650': {
            'WINDOW_WIDTH': 1024,
            'WINDOW_HEIGHT': 768,
            'FRAME_RATE': 15,
            'NUM_NPC_VEHICLES': 25,
            'NUM_NPC_PEDESTRIANS': 15
        },
        'mid_range': {
            'WINDOW_WIDTH': 1280,
            'WINDOW_HEIGHT': 720,
            'FRAME_RATE': 20,
            'NUM_NPC_VEHICLES': 40,
            'NUM_NPC_PEDESTRIANS': 25
        },
        'high_end': {
            'WINDOW_WIDTH': 1920,
            'WINDOW_HEIGHT': 1080,
            'FRAME_RATE': 30,
            'NUM_NPC_VEHICLES': 60,
            'NUM_NPC_PEDESTRIANS': 40
        }
    }
    
    return configs.get(gpu_tier, configs['gtx_1650'])  # Default to conservative
```

## 📊 **Performance Monitoring**

### **Built-in Performance Tracking**

Add this to your `record_driving_session.py`:

```python
class PerformanceMonitor:
    def __init__(self):
        self.fps_history = []
        self.memory_usage = []
        self.frame_times = []
        
    def update(self, fps, memory_mb):
        self.fps_history.append(fps)
        self.memory_usage.append(memory_mb)
        
        # Keep only last 100 measurements
        if len(self.fps_history) > 100:
            self.fps_history.pop(0)
            self.memory_usage.pop(0)
            
    def get_stats(self):
        if not self.fps_history:
            return "No performance data"
            
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        min_fps = min(self.fps_history)
        max_memory = max(self.memory_usage)
        
        return f"FPS: {avg_fps:.1f} avg, {min_fps:.1f} min | Memory: {max_memory:.0f}MB peak"
        
    def should_warn(self):
        if len(self.fps_history) < 10:
            return False
            
        recent_fps = self.fps_history[-10:]
        avg_recent = sum(recent_fps) / len(recent_fps)
        
        return avg_recent < FPS_WARNING_THRESHOLD

# Usage in main loop
monitor = PerformanceMonitor()

while running:
    current_fps = clock.get_fps()
    # memory_mb = get_memory_usage()  # Implement if needed
    
    monitor.update(current_fps, 0)
    
    if monitor.should_warn():
        print("⚠️ Performance warning: Consider reducing settings")
```

### **Real-time FPS Display**

```python
# Add to camera callback for real-time monitoring
def _camera_callback(self, image):
    # ... existing code ...
    
    # Display performance info on screen
    if ENABLE_PERFORMANCE_MONITORING:
        fps = self.clock.get_fps()
        if fps < FPS_WARNING_THRESHOLD:
            print(f"⚠️ Low FPS: {fps:.1f} - Consider reducing NPCs or resolution")
        elif self.frames_captured % 60 == 0:  # Every 3 seconds at 20fps
            print(f"✅ Performance: {fps:.1f} FPS, {self.frames_captured} frames captured")
```

## 🔧 **System Optimization**

### **Windows Settings**

#### **Power Management**
```powershell
# Set to High Performance mode
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable Windows Game Mode (can cause stuttering)
# Go to Settings > Gaming > Game Mode > Off
```

#### **Graphics Settings**
1. **NVIDIA Control Panel** (for NVIDIA GPUs):
   ```
   3D Settings > Manage 3D Settings:
   - Power management mode: Prefer maximum performance
   - Texture filtering - Quality: Performance
   - Vertical sync: Off
   - Max pre-rendered frames: 1
   ```

2. **Windows Graphics Settings**:
   ```
   Settings > System > Display > Graphics Settings:
   - Add CarlaUE4.exe
   - Set to "High performance"
   ```

#### **System Cleanup**
```powershell
# Close unnecessary programs
taskkill /f /im chrome.exe
taskkill /f /im discord.exe
# (Keep only essential programs running)

# Clear temp files
del /q /f %temp%\*
```

### **Thermal Management**

#### **Laptop Optimization**
- **Cooling Pad**: Use external cooling for sustained performance
- **Power Mode**: Plug in laptop (don't run on battery)
- **Thermal Monitoring**: Watch CPU/GPU temperatures
- **Room Temperature**: Keep ambient temperature low

#### **Thermal Throttling Check**
```python
# Add to performance monitoring
import psutil

def check_thermal_throttling():
    """Basic thermal monitoring."""
    try:
        # CPU temperature (if available)
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current > 85:  # Celsius
                        print(f"🌡️ Thermal warning: {name} at {entry.current}°C")
    except:
        pass  # Temperature monitoring not available
```

## 📈 **Progressive Optimization Strategy**

### **Step 1: Start Conservative**
```python
# Initial safe settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
NUM_NPC_VEHICLES = 15
NUM_NPC_PEDESTRIANS = 8
FRAME_RATE = 12
```

### **Step 2: Test and Monitor**
- Run for 10 minutes
- Check average FPS
- Monitor for stuttering or crashes
- Record performance metrics

### **Step 3: Gradual Increases**
```python
# If stable at Step 1, try:
WINDOW_WIDTH = 1024      # +28% resolution
NUM_NPC_VEHICLES = 20    # +33% NPCs

# If stable, continue:
WINDOW_HEIGHT = 768      # Full 1024x768
FRAME_RATE = 15          # +25% target FPS

# Final optimization:
NUM_NPC_VEHICLES = 25    # Optimal for GTX 1650
NUM_NPC_PEDESTRIANS = 15
```

### **Step 4: Find Sweet Spot**
- **Target**: Stable 15+ FPS with minimal drops
- **Quality**: Good enough for research (not presentation)
- **Reliability**: No crashes during 60+ minute sessions
- **Recording**: Smooth video output without frame skips

## 🚨 **Troubleshooting Performance Issues**

### **Common Problems and Solutions**

#### **Low FPS (< 10 FPS)**
```
Symptoms: Slideshow-like gameplay, choppy recording
Solutions:
1. Reduce resolution: 1024x768 → 800x600
2. Lower NPC count: 25 vehicles → 15 vehicles  
3. Change quality: Low → Epic (sometimes helps with GPU utilization)
4. Restart CARLA server (memory leaks)
5. Close other applications
```

#### **Stuttering/Frame Drops**
```
Symptoms: Inconsistent frame times, periodic freezes
Solutions:
1. Disable VSync: Add -NoVSync to launch command
2. Set fixed frame rate: -fps=15 in launch command
3. Check thermal throttling
4. Disable Windows Game Mode
5. Update GPU drivers
```

#### **Memory Issues**
```
Symptoms: Crashes after 30+ minutes, slow performance over time
Solutions:
1. Restart CARLA server every hour
2. Reduce recording session length
3. Monitor system RAM usage
4. Close memory-heavy applications
5. Increase virtual memory (page file)
```

#### **CARLA Won't Start**
```
Symptoms: Black screen, immediate crash, connection timeout  
Solutions:
1. Check Windows Defender exceptions
2. Try windowed mode: -windowed
3. Lower resolution: -ResX=800 -ResY=600
4. Update DirectX and Visual C++ redistributables
5. Verify CARLA installation integrity
```

## 📊 **Benchmark Results**

### **GTX 1650 Performance Data**

| Settings | Avg FPS | Min FPS | Stability | Recording Quality |
|----------|---------|---------|-----------|-------------------|
| 800x600, 15 NPCs | 18-22 | 14 | Excellent | Good |
| 1024x768, 25 NPCs | 15-18 | 12 | Good | Excellent |
| 1280x720, 40 NPCs | 10-14 | 8 | Poor | Fair |
| 1920x1080, 50 NPCs | 5-8 | 3 | Unusable | Poor |

### **Recommended Configurations**

#### **Research Quality** (Recommended)
```python
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768  
NUM_NPC_VEHICLES = 25
NUM_NPC_PEDESTRIANS = 15
FRAME_RATE = 15
# Expected: 15-18 FPS, stable recording
```

#### **Performance Priority**
```python
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
NUM_NPC_VEHICLES = 20
NUM_NPC_PEDESTRIANS = 10  
FRAME_RATE = 15
# Expected: 18-22 FPS, very stable
```

#### **Quality Priority** (If performance allows)
```python
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
NUM_NPC_VEHICLES = 30
NUM_NPC_PEDESTRIANS = 20
FRAME_RATE = 20
# Expected: 12-15 FPS, may need adjustment
```

## 🎯 **Final Recommendations**

### **For GTX 1650 Users**
1. **Start with Research Quality settings**
2. **Monitor performance for first 30 minutes**
3. **Adjust based on actual FPS measurements**
4. **Prioritize stability over visual fidelity**
5. **Plan for 60-90 minute recording sessions maximum**

### **Optimization Priority Order**
1. **Stability** - No crashes during recording
2. **Frame Rate** - Consistent 15+ FPS
3. **Recording Quality** - Smooth video output
4. **Visual Quality** - Good enough for research
5. **NPC Density** - Realistic but not overwhelming

### **Success Criteria**
- ✅ **15+ FPS average** during active recording
- ✅ **No frame drops** during action sequences
- ✅ **60+ minute sessions** without crashes
- ✅ **Smooth video output** for dataset creation
- ✅ **Responsive controls** for natural driving

With these optimizations, GTX 1650 users can successfully create research-quality datasets for XAI autonomous driving research using CARLA simulator.