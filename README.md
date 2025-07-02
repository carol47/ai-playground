# 🚀 AI Playground

A collection of cutting-edge AI projects leveraging local models and hardware acceleration.

## 🎯 Current Projects

### 🎖️ Operation Transcription-Outpost
Real-time audio transcription service using local models (PaddleSpeech + LLaMA). See [project details](./transcription-outpost/README.md).

## 💻 Development Environment

### Hardware Specifications
- **CPU:** AMD Ryzen 9950X
  - High-performance multi-threading
  - Optimized for parallel processing
  - Excellent for concurrent model inference
- **RAM:** 64GB DDR5
  - High-speed memory access
  - Large model loading capacity
  - Efficient data streaming
- **GPU:** GeForce RTX 5070 Ti
  - CUDA-enabled for AI acceleration
  - Optimized for model inference
  - Excellent for real-time processing
- **Motherboard:** ASROCK X870E
  - High-speed PCIe lanes
  - Robust power delivery
  - Enhanced system stability

### Software Configuration
- Windows 10 Pro (build 26100)
- CUDA Toolkit
- Python 3.12
- Poetry for dependency management

## 🛠️ Model Optimization

### LLaMA Configuration
- Model: LLaMA-2-13B (GGUF format)
- GPU Layers: 35
- Batch Size: 512
- Processing Threads: 32
- Context Length: 2048

### PaddleSpeech Configuration
- Model: Conformer
- GPU Acceleration: Enabled
- CUDA Device: Primary GPU
- Optimized for real-time transcription

## 📚 Project Structure
```
ai-playground/
├── transcription-outpost/    # Audio transcription service
│   └── [See project README for details]
└── [Future projects]
```

## 🔧 Setup
Each project has its own setup instructions in its respective directory.

## 📝 License
TBD

## 🤝 Contributing
Feel free to open issues or submit pull requests!
