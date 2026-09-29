# SeaVision AI: Catching Spills with ML & AIS Data
**Full-Stack Maritime Domain Awareness (MDA) Oil Spill Hindcast & Vessel Attribution System**  
*(Problem Statement: SIH26143)*

---

## 1. System Overview & Architecture

SeaVision AI detects ocean oil spills from Synthetic Aperture Radar (SAR) imagery and correlates them with Automatic Identification System (AIS) vessel trajectories using reverse ocean-drift modeling to identify polluters in real-time.

```
+--------------------------+        +---------------------------+
|  SAR Satellite Imagery   |        |   Live AIS Vessel Feed    |
| (Sentinel-1 Dark Patch)  |        | (Positions, COG, SOG, Gap)|
+------------+-------------+        +-------------+-------------+
             |                                    |
             v                                    v
+---------------------------------------------------------------+
|             REVERSE DRIFT HINDCAST VECTOR ENGINE              |
|   P_origin = P_detected - (V_current + 0.03 * V_wind) * Δt    |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|             AIS ANOMALY & CORRELATION ENGINE                  |
|    Guilt_Score = 0.40 * S_d + 0.30 * S_t + 0.30 * S_g         |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|       TACTICAL MARITIME COMMAND CENTER (React + Leaflet)      |
|  - Real-time Hindcast Simulation Controls                     |
|  - Historical Time Scrubber (T_origin to T_detect)            |
|  - Color-Coded Vessel Tracks & AIS Blackout Warning Markers   |
|  - MARPOL Annex I Legal Evidence Dossier Modal (Print / PDF)  |
+---------------------------------------------------------------+
```

---

## 2. Core Mathematical Models

### A. Ocean Reverse Drift Hindcast Model
$$\vec{P}_{\text{origin}} = \vec{P}_{\text{detected}} - \left( \vec{V}_{\text{current}} + 0.03 \cdot \vec{V}_{\text{wind}} \right) \times \Delta t$$
- **Surface Ocean Current:** Oil moves at 100% velocity vector.
- **Surface Atmospheric Wind:** Carries oil at a 3% leeway transfer coefficient.
- **Geodesic Coordinate Shift:** Integrated over $\Delta t$ hours using great-circle geometry.

### B. Weighted 3-Factor Vessel Guilt Score
$$\text{Guilt\_Probability\_Score} = 0.40 \cdot S_d + 0.30 \cdot S_t + 0.30 \cdot S_g$$
1. **$S_d$ Spatial Proximity (40%):** Distance between interpolated vessel track and calculated spill origin $\vec{P}_{\text{origin}}$ at $T_{\text{spill}}$.
2. **$S_t$ Trajectory Alignment (30%):** Angular cosine similarity between vessel course over ground (COG) and the linear axis of the oil slick.
3. **$S_g$ AIS Gap Anomaly (30%):** Anomaly score triggered when a vessel deliberately turns off its AIS transponder within 15 km of the spill origin.

---

## 3. Real-World Datasets & Mapping Services

- **CARTO Basemaps API Key:** Integrated authenticated dark matter tiles (`cb1_3xoj_1_f33b361506cf6c1f100c6055`).
- **Marine Cadastre AIS Data Standard:** Bureau of Ocean Energy Management (BOEM) & NOAA schema (`marinecadastre.gov/accessais`) supporting 17 standard AIS columns.
- **Zenodo Sentinel-1 SAR Oil Spill Benchmark:** C-SAR IW GRDH Scene (10m resolution, VV+VH polarizations, multi-class segmentation mask for oil, look-alikes, and ships).

---

## 4. Automated Test Suite (`autotest.py`)
Run the comprehensive 24-point automated test suite:
```bash
python3 autotest.py
```

---

## 5. Full-Stack Project Structure

- `server.py`: Complete Zero-Dependency Full-Stack HTTP + REST API Server. Serves the REST API and the live Tactical Command Center Web UI.
- `static/index.html`: Production-ready, dark-mode Maritime Operations UI with authenticated CARTO basemaps, Leaflet map, time-slider, hindcast sliders, and live API fetch.
- `Dashboard.jsx`: Standalone React + Tailwind + Leaflet Component with CARTO API key integration.
- `autotest.py`: Comprehensive 24-point automated test suite.
- `ais_parser_marinecadastre.py`: Marine Cadastre AIS schema parser & generator (`marinecadastre.gov/accessais`).
- `sar_zenodo_dataset.py`: Zenodo Sentinel-1 SAR Oil Spill benchmark dataset parser & GeoJSON exporter.
- `synthetic_data_generator.py`: Generates SAR detection metadata & vessel tracks in the Indian EEZ (Mumbai Offshore).
- `attribution_engine.py`: Reverse-drift calculation & 3-factor guilt scoring pipeline.
- `main_api.py`: FastAPI REST backend for ASGI deployment.
- `start.sh`: 1-Click launcher script.
- `requirements.txt`: Python package requirements.

---

## 6. How to Run the Website (1-Command Startup)

### Method 1: Using the 1-Click Launcher (Recommended)
```bash
./start.sh
```
*This starts the server on port `8000` and automatically opens `http://localhost:8000/` in your default browser.*

### Method 2: Running via Python Directly
```bash
python3 server.py 8000
```
Open **`http://localhost:8000/`** to view the live tactical interface.

### Method 3: Running via FastAPI & Uvicorn
```bash
pip install -r requirements.txt
uvicorn main_api:app --reload --port 8000
```

---

## 7. Live REST API Endpoints

- `GET http://localhost:8000/api/v1/spill-analysis` — Returns detected SAR dark patch polygon, centroid, environmental vectors, and calculated drift line.
- `GET http://localhost:8000/api/v1/correlated-vessels` — Returns vessels ranked by `Guilt_Probability_Score`.
- `POST http://localhost:8000/api/v1/simulate-drift` — Recalculates backwards drift origin and vessel correlation live based on customized wind/current parameters.
- `POST http://localhost:8000/api/v1/generate-report` — Formats an official MARPOL Annex I violation dossier for Coast Guard enforcement.
- `GET http://localhost:8000/api/health` — Backend service health check.
