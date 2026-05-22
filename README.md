# AI-CAD 🏗️

**AI-Powered CAD Platform — Intelligent Floor Plan Generation, DXF Export, Real-Time Collaboration**

[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI](https://img.shields.io/badge/AI-Powered-purple.svg)](https://github.com/ishan-parihar/AI-CAD)

AI-CAD is a generative design platform that converts natural language descriptions into production-ready CAD floor plans. By combining LLM-powered spatial reasoning with precise programmatic CAD generation, it bridges the gap between conceptual design intent and editable engineering drawings.

---

## 🚩 The Problem

Traditional CAD workflows require significant manual effort: every wall, door, window, and annotation must be placed individually. Architectural concept iteration is slow, and non-technical stakeholders cannot participate in the spatial design process without a CAD operator.

## 💡 The Solution

AI-CAD accepts high-level spatial descriptions and generates complete floor plans with:

- **AI-Driven Layout Generation**: LLM interprets spatial requirements and produces dimensionally accurate layouts
- **DXF Export**: Production-ready DXF files compatible with AutoCAD, LibreCAD, and BIM tools
- **Real-Time Collaboration**: WebSocket-enabled live editing for team workflows
- **Scalable Architecture**: FastAPI backend with async task processing for handling complex designs

---

## ✨ Features

- **Natural Language Input**: Describe spaces conversationally — "a 3-bedroom apartment with open kitchen and 2 bathrooms"
- **Programmatic CAD**: ezdxf-powered precision geometry generation
- **Web Interface**: Clean, responsive UI with live preview
- **REST API**: Programmatic access for integration into design pipelines
- **Session Persistence**: Save, load, and iterate on designs

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/ishan-parihar/AI-CAD.git
cd AI-CAD
pip install -r requirements.txt
```

### Running

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Usage

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Open plan living room with kitchen island, 400 sq ft"}'
```

---

## 🛠 Tech Stack

- **Backend**: Python, FastAPI
- **CAD Engine**: ezdxf
- **AI**: LLM-powered spatial reasoning
- **Real-Time**: WebSocket
- **Frontend**: HTML/CSS/JS

---

## 🗺 Roadmap

- [ ] 3D model generation (STEP/OBJ export)
- [ ] BIM integration (IFC format)
- [ ] Multi-user collaborative sessions
- [ ] Building code compliance checking
- [ ] VR/AR visualization export

---
Developed by [Ishan Parihar](https://github.com/ishan-parihar) — If you find this useful, [consider supporting](https://rzp.io/rzp/ishan-parihar)