# Network Dashboards

![node](https://img.shields.io/badge/node-javascript-339933?style=flat-square) ![python](https://img.shields.io/badge/python-3.x-3776AB?style=flat-square)

A comprehensive network monitoring solution with a FastAPI backend and Vue.js frontend dashboard for real-time network metrics visualization.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Features
- Real-time monitoring of network interfaces (bandwidth, latency, errors)
- Interactive dashboard with multiple views:
  - Global overview with aggregated metrics
  - Detailed interface-specific statistics
  - Error tracking and anomaly detection
  - Latency measurement to configurable targets
- Configurable alert thresholds for key metrics
- Historical data visualization with time-based filtering
- Dark/light mode support
- Export capabilities for error logs

## Tech Stack
**Backend:**
- Python 3.x
- FastAPI (REST API)
- Uvicorn (ASGI server)
- psutil (system monitoring)
- ping3 (latency measurement)
- netifaces (interface detection)

**Frontend:**
- Vue.js 3 (Composition API)
- Pinia (state management)
- Vue Router
- ApexCharts (data visualization)
- Tailwind CSS (styling)
- Vite (build tool)

## Installation

### Backend Setup
1. Clone the repository:
```bash
git clone https://github.com/RaBYho/network-dashboards.git
cd network-dashboards/backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd ../frontend/network-dashboard
```

2. Install dependencies:
```bash
npm install
```

## Configuration

### Backend
The backend runs on port 8000 by default. To change this, modify the `uvicorn.run()` call in `backend/main.py`.

### Frontend
The frontend expects the backend API to be available at `http://localhost:8000`. To change this:
1. Create a `.env` file in `frontend/network-dashboard`
2. Add:
```bash
VITE_API_BASE_URL=http://your-backend-url:port
```

## Usage

### Start the Backend
From the backend directory:
```bash
python main.py
```

### Start the Frontend
From the frontend directory:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:5173` (or the port Vite assigns).

## Project Structure
```
network-dashboards/
├── backend/               # FastAPI application
│   ├── collectors/        # Network metric collection modules
│   ├── main.py            # API entry point
│   └── requirements.txt   # Python dependencies
└── frontend/
    ├── network-dashboard/ # Vue.js application
    │   ├── public/        # Static assets
    │   ├── src/           # Application source
    │   │   ├── components # Vue components
    │   │   ├── pages/     # Route views
    │   │   ├── router/    # Vue Router configuration
    │   │   ├── stores/    # Pinia state management
    │   │   └── main.js    # App entry point
    │   ├── package.json   # Frontend dependencies
    │   └── vite.config.js # Vite configuration
    └── mockup/            # HTML mockups (reference only)
```

## Contributing
Contributions are welcome! Please open an issue to discuss proposed changes before submitting a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request