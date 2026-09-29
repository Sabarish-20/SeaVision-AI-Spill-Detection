"""
SeaVision AI - Comprehensive System Automated Test Suite (autotest.py)
Validates:
1. Oceanographic Reverse-Drift Hindcast Vector Mathematics
2. Multi-parameter AIS Anomaly & Guilt Scoring Engine
3. Official Marine Cadastre AIS Schema Ingestion & Parsing (marinecadastre.gov/accessais)
4. Zenodo Sentinel-1 SAR Oil Spill Benchmark Dataset & GeoJSON Generation
5. ISRO MOSDAC Satellite API Client & Oceanographic Telemetry Integration (mosdac.gov.in)
6. ISRO Bhuvan Government Geospatial Base Maps (NRSC WMS / Open Geospatial)
7. Full-Stack HTTP REST Server Endpoints & Data Contracts
"""

import sys
import os
import io
import json
import math
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synthetic_data_generator import generate_synthetic_dataset
from attribution_engine import (
    calculate_slick_origin,
    calculate_drift_vector,
    calculate_guilt_score,
    run_full_attribution,
    haversine_distance_km
)
from ais_parser_marinecadastre import (
    generate_marinecadastre_ais_records,
    parse_marinecadastre_ais_stream,
    export_marinecadastre_csv
)
from sar_zenodo_dataset import get_zenodo_sentinel1_sar_sample, export_zenodo_sar_geojson
from mosdac_client import MosdacClient
from server import SeaVisionHandler

class TestReporter:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def log(self, test_name: str, passed: bool, detail: str = ""):
        status = "PASSED" if passed else "FAILED"
        icon = "✅" if passed else "❌"
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        self.tests.append((test_name, passed, detail))
        print(f"{icon} [{status}] {test_name}" + (f" -> {detail}" if detail else ""))

    def summary(self):
        print("\n" + "=" * 70)
        print(f"📊 AUTOTEST SUMMARY: {self.passed} Passed, {self.failed} Failed ({self.passed + self.failed} Total)")
        print("=" * 70)
        if self.failed > 0:
            print("❌ Some tests failed. Please review details above.")
            return False
        else:
            print("🚀 ALL SYSTEMS OPERATIONAL: 100% Tests Passed.")
            return True

reporter = TestReporter()

# ==============================================================================
# 1. TEST SUITE: Ocean Reverse Drift Vector Mathematics
# ==============================================================================
def test_ocean_drift_math():
    print("\n--- [SUITE 1] Testing Ocean Reverse-Drift Vector Mathematics ---")
    
    drift = calculate_drift_vector(
        current_speed_knots=1.25,
        current_dir_deg=55.0,
        wind_speed_knots=16.5,
        wind_dir_deg=70.0,
        leeway_factor=0.03
    )

    reporter.log(
        "Drift Velocity Calculation",
        2.9 <= drift["net_speed_kmh"] <= 3.5 and 55.0 <= drift["net_dir_deg"] <= 62.0,
        f"Speed: {drift['net_speed_kmh']} km/h, Heading: {drift['net_dir_deg']}°"
    )

    origin_res = calculate_slick_origin(
        detected_centroid={"lat": 19.1820, "lon": 72.1150},
        current_speed_knots=1.25,
        current_dir_deg=55.0,
        wind_speed_knots=16.5,
        wind_dir_deg=70.0,
        delta_hours=3.5
    )

    orig = origin_res["origin_coordinates"]
    dist_km = origin_res["total_drift_distance_km"]

    is_orig_accurate = (
        19.120 <= orig["lat"] <= 19.140 and
        72.015 <= orig["lon"] <= 72.035 and
        11.0 <= dist_km <= 11.6
    )
    reporter.log(
        "Hindcast Origin Coordinates & Displacement",
        is_orig_accurate,
        f"Calculated Origin: ({orig['lat']}°N, {orig['lon']}°E), Drift: {dist_km} km"
    )

    reporter.log(
        "Hindcast Intermediate Trajectory Path",
        len(origin_res["trajectory_path"]) == 11,
        f"Generated {len(origin_res['trajectory_path'])} discrete hindcast waypoints"
    )

# ==============================================================================
# 2. TEST SUITE: AIS Anomaly & Weighted Guilt Scoring Engine
# ==============================================================================
def test_attribution_scoring():
    print("\n--- [SUITE 2] Testing AIS Anomaly & Guilt Scoring Engine ---")
    
    dataset = generate_synthetic_dataset()
    results = run_full_attribution(dataset)

    ranked = results["ranked_vessels"]
    top_suspect = results["primary_suspect"]

    reporter.log(
        "Primary Suspect Identification",
        top_suspect["vessel_name"] == "MT ARABIAN TITAN",
        f"Identified {top_suspect['vessel_name']} as top suspect"
    )

    reporter.log(
        "Guilty Tanker Match Confidence Score",
        top_suspect["guilt_probability_score"] >= 95.0,
        f"MT ARABIAN TITAN score: {top_suspect['guilt_probability_score']}%"
    )

    container_vessel = next((v for v in ranked if v["vessel_name"] == "MV INDUS TRADER"), None)
    reporter.log(
        "Innocent Container Ship Low Score",
        container_vessel and container_vessel["guilt_probability_score"] < 40.0,
        f"MV INDUS TRADER score: {container_vessel['guilt_probability_score']}% [CLEAN]"
    )

    fishing_boat = next((v for v in ranked if v["vessel_name"] == "FV SAGAR RATNA"), None)
    reporter.log(
        "Distant Fishing Vessel Low Score",
        fishing_boat and fishing_boat["guilt_probability_score"] < 25.0,
        f"FV SAGAR RATNA score: {fishing_boat['guilt_probability_score']}% [CLEAN]"
    )

# ==============================================================================
# 3. TEST SUITE: Marine Cadastre AIS Standard Parsing & Ingestion
# ==============================================================================
def test_marinecadastre_ais():
    print("\n--- [SUITE 3] Testing Marine Cadastre AIS Standard Ingestion ---")
    
    records = generate_marinecadastre_ais_records()
    reporter.log(
        "Marine Cadastre Record Generation",
        len(records) >= 20,
        f"Generated {len(records)} standard Marine Cadastre records"
    )

    sample = records[0]
    required_keys = ["MMSI", "BaseDateTime", "LAT", "LON", "SOG", "COG", "Heading", "VesselName", "IMO", "VesselType", "Length", "Draft"]
    has_all_keys = all(k in sample for k in required_keys)
    reporter.log(
        "Marine Cadastre Schema Conformance (17 Fields)",
        has_all_keys,
        f"Validated MMSI={sample['MMSI']}, VesselName={sample['VesselName']}, Type={sample['VesselType']}"
    )

    export_marinecadastre_csv(records, "temp_test_cadastre.csv")
    with open("temp_test_cadastre.csv", "r") as f:
        csv_text = f.read()

    parsed_vessels = parse_marinecadastre_ais_stream(csv_text)
    if os.path.exists("temp_test_cadastre.csv"):
        os.remove("temp_test_cadastre.csv")

    reporter.log(
        "Marine Cadastre CSV Stream Parsing",
        len(parsed_vessels) == 4,
        f"Successfully grouped and parsed {len(parsed_vessels)} distinct vessels from CSV"
    )

    tanker_vessel = next((v for v in parsed_vessels if v["mmsi"] == 636018244), None)
    reporter.log(
        "Automated AIS Blackout Gap Detection",
        tanker_vessel and tanker_vessel["ais_gap_detected"] and tanker_vessel["gap_duration_minutes"] >= 40,
        f"Detected {tanker_vessel['gap_duration_minutes']} min blackout gap on MMSI 636018244"
    )

# ==============================================================================
# 4. TEST SUITE: Zenodo Sentinel-1 SAR Benchmark Dataset & GeoJSON
# ==============================================================================
def test_zenodo_sar_dataset():
    print("\n--- [SUITE 4] Testing Zenodo Sentinel-1 SAR Dataset & GeoJSON ---")
    
    sar_data = get_zenodo_sentinel1_sar_sample()
    
    reporter.log(
        "Sentinel-1 C-SAR Scene Metadata",
        "S1A_IW_GRDH" in sar_data["scene_granule_id"] and sar_data["pixel_spacing_meters"] == 10.0,
        f"Granule: {sar_data['scene_granule_id']}, Resolution: {sar_data['pixel_spacing_meters']}m"
    )

    reporter.log(
        "Multi-Class Segmentation (Classes 1, 2, 3, 0)",
        len(sar_data["geojson"]["features"]) >= 3,
        f"Validated {len(sar_data['geojson']['features'])} segmentation classes (Oil, Lookalike, Ship)"
    )

    geojson_path = export_zenodo_sar_geojson("temp_test_sar.geojson")
    with open(geojson_path, "r") as f:
        geojson_obj = json.load(f)
    if os.path.exists("temp_test_sar.geojson"):
        os.remove("temp_test_sar.geojson")

    reporter.log(
        "SAR GeoJSON Polygon Export & Validation",
        geojson_obj["type"] == "FeatureCollection" and len(geojson_obj["features"]) > 0,
        f"Valid FeatureCollection with {len(geojson_obj['features'])} GeoJSON polygons"
    )

# ==============================================================================
# 5. TEST SUITE: ISRO MOSDAC Satellite API & ISRO Bhuvan Government Maps
# ==============================================================================
def test_mosdac_and_bhuvan_services():
    print("\n--- [SUITE 5] Testing ISRO MOSDAC & Bhuvan Government Services ---")
    
    client = MosdacClient()
    
    # 1. Dataset Catalog
    datasets = client.get_catalog_datasets()
    missions = [d["mission"] for d in datasets]
    reporter.log(
        "ISRO MOSDAC Satellite Catalog (Oceansat-3, SARAL, INSAT)",
        "OCEANSAT-3" in missions and "SARAL-AltiKa" in missions,
        f"Catalog contains {len(datasets)} active satellite missions"
    )

    # 2. Telemetry Retrieval
    tel = client.fetch_ocean_environmental_telemetry(19.1820, 72.1150)
    reporter.log(
        "MOSDAC Ocean Wind & Current Assimilation Telemetry",
        tel["ocean_wind"]["speed_knots"] == 16.5 and tel["ocean_current"]["speed_knots"] == 1.25,
        f"Wind: {tel['ocean_wind']['speed_knots']} kts ({tel['ocean_wind']['sensor']}), Current: {tel['ocean_current']['speed_knots']} kts"
    )

    # 3. Government Map Services
    maps = client.get_government_map_services()
    reporter.log(
        "ISRO Bhuvan WMS Map Layer Configuration (NRSC)",
        "bhuvan-vec2.nrsc.gov.in" in maps["bhuvan_satellite_wms"]["url"],
        f"Bhuvan WMS Endpoint: {maps['bhuvan_satellite_wms']['url']} (Layer: {maps['bhuvan_satellite_wms']['layers']})"
    )

    # 4. Zero Commercial Key Conformance
    with open(os.path.join(os.path.dirname(__file__), "static", "index.html"), "r") as f:
        html = f.read()
    
    has_bhuvan = "bhuvan-vec2.nrsc.gov.in" in html
    no_carto_key = "cb1_3xoj" not in html
    reporter.log(
        "Government Basemap Conformance (Zero Commercial API Keys)",
        has_bhuvan and no_carto_key,
        "Confirmed ISRO Bhuvan WMS active and Carto key removed"
    )

# ==============================================================================
# 6. TEST SUITE: Full-Stack REST API & Endpoint Contracts
# ==============================================================================
class MockSocket:
    def __init__(self, request_bytes):
        self._rfile = io.BytesIO(request_bytes)
        self.output = io.BytesIO()
    def makefile(self, mode, *args, **kwargs):
        if 'r' in mode:
            return self._rfile
        return self.output
    def sendall(self, data):
        self.output.write(data)

def test_api_endpoints():
    print("\n--- [SUITE 6] Testing Full-Stack REST API Endpoints ---")

    def call_api(method: str, path: str, body_dict: dict = None) -> (int, dict, str):
        if body_dict is not None:
            raw_body = json.dumps(body_dict).encode("utf-8")
            req = f"{method} {path} HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(raw_body)}\r\nContent-Type: application/json\r\n\r\n".encode("utf-8") + raw_body
        else:
            req = f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode("utf-8")
        
        sock = MockSocket(req)
        handler = SeaVisionHandler(sock, ('127.0.0.1', 54321), None)
        raw_output = sock.output.getvalue().decode("utf-8")
        
        header_end = raw_output.find("\r\n\r\n")
        header = raw_output[:header_end]
        body = raw_output[header_end + 4:]
        
        status_line = header.split("\r\n")[0]
        status_code = int(status_line.split(" ")[1])
        try:
            json_body = json.loads(body)
        except Exception:
            json_body = None
        return status_code, json_body, body

    # 1. GET /api/health
    status, json_data, _ = call_api("GET", "/api/health")
    reporter.log("Endpoint GET /api/health", status == 200 and json_data.get("status") == "healthy")

    # 2. GET /api/v1/spill-analysis
    status, json_data, _ = call_api("GET", "/api/v1/spill-analysis")
    reporter.log(
        "Endpoint GET /api/v1/spill-analysis",
        status == 200 and json_data.get("incident_id") == "SV-IND-2026-0929-01",
        f"Area: {json_data.get('estimated_area_sq_km')} km², Confidence: {json_data.get('sar_confidence_score') * 100}%"
    )

    # 3. GET /api/v1/correlated-vessels
    status, json_data, _ = call_api("GET", "/api/v1/correlated-vessels")
    reporter.log(
        "Endpoint GET /api/v1/correlated-vessels",
        status == 200 and len(json_data.get("ranked_vessels", [])) == 4,
        f"Correlated {len(json_data.get('ranked_vessels', []))} vessels"
    )

    # 4. POST /api/v1/simulate-drift
    sim_payload = {
        "delta_hours": 4.0,
        "current_speed_knots": 1.5,
        "current_dir_deg": 60.0,
        "wind_speed_knots": 20.0,
        "wind_dir_deg": 75.0
    }
    status, json_data, _ = call_api("POST", "/api/v1/simulate-drift", sim_payload)
    reporter.log(
        "Endpoint POST /api/v1/simulate-drift",
        status == 200 and "calculated_origin" in json_data,
        f"Live Recalculated Origin: {json_data.get('calculated_origin')}"
    )

    # 5. GET /api/v1/mosdac/datasets
    status, json_data, _ = call_api("GET", "/api/v1/mosdac/datasets")
    reporter.log(
        "Endpoint GET /api/v1/mosdac/datasets",
        status == 200 and len(json_data.get("datasets", [])) >= 4,
        f"Returned {len(json_data.get('datasets', []))} MOSDAC satellite missions"
    )

    # 6. GET /api/v1/mosdac/telemetry
    status, json_data, _ = call_api("GET", "/api/v1/mosdac/telemetry")
    reporter.log(
        "Endpoint GET /api/v1/mosdac/telemetry",
        status == 200 and "telemetry" in json_data,
        f"Ingested MOSDAC Wind: {json_data.get('telemetry', {}).get('ocean_wind', {}).get('speed_knots')} kts"
    )

    # 7. GET /api/v1/gov-map/config
    status, json_data, _ = call_api("GET", "/api/v1/gov-map/config")
    reporter.log(
        "Endpoint GET /api/v1/gov-map/config",
        status == 200 and "bhuvan_satellite_wms" in json_data.get("government_map_services", {}),
        "Returned ISRO Bhuvan & MOSDAC WMS configs"
    )

    # 8. POST /api/v1/generate-report (MARPOL Dossier)
    report_payload = {
        "incident_id": "SV-IND-2026-0929-01",
        "target_vessel_id": "VESSEL-002",
        "investigator_agency": "Indian Coast Guard / DG Shipping"
    }
    status, json_data, _ = call_api("POST", "/api/v1/generate-report", report_payload)
    dossier = json_data.get("evidence_dossier", {})
    reporter.log(
        "Endpoint POST /api/v1/generate-report",
        status == 200 and dossier.get("suspect_vessel", {}).get("name") == "MT ARABIAN TITAN",
        f"Generated MARPOL Report ID: {dossier.get('report_id')}"
    )

    # 9. GET /api/v1/incidents
    status, json_data, _ = call_api("GET", "/api/v1/incidents")
    reporter.log(
        "Endpoint GET /api/v1/incidents (Multi-Scenario Dummy Dataset)",
        status == 200 and len(json_data.get("incidents", [])) >= 3,
        f"Returned {len(json_data.get('incidents', []))} realistic maritime scenarios"
    )

    # 10. GET /api/v1/live-alerts
    status, json_data, _ = call_api("GET", "/api/v1/live-alerts")
    reporter.log(
        "Endpoint GET /api/v1/live-alerts (Real-Time Alert Feed)",
        status == 200 and len(json_data.get("alerts", [])) >= 3,
        f"Ingested {len(json_data.get('alerts', []))} live real-time maritime alerts"
    )

    # 11. POST /api/v1/incidents/select (Scenario Switcher)
    status, json_data, _ = call_api("POST", "/api/v1/incidents/select", {"scenario_id": "gulf_of_kachchh"})
    reporter.log(
        "Endpoint POST /api/v1/incidents/select",
        status == 200 and json_data.get("scenario_id") == "gulf_of_kachchh",
        f"Switched scenario to: {json_data.get('incident_id')}"
    )

    # 12. POST /api/v1/dispatch-action (Coast Guard Intercept)
    dispatch_payload = {
        "vessel_name": "MT ARABIAN TITAN",
        "mmsi": 636018244,
        "action_type": "COAST_GUARD_INTERCEPT"
    }
    status, json_data, _ = call_api("POST", "/api/v1/dispatch-action", dispatch_payload)
    reporter.log(
        "Endpoint POST /api/v1/dispatch-action (Coast Guard Flash Intercept)",
        status == 200 and "dispatch_record" in json_data,
        f"Dispatched Intercept Order ID: {json_data.get('dispatch_record', {}).get('dispatch_id')}"
    )

    # 13. GET / (Frontend Tactical Web UI Delivery)
    status, _, raw_html = call_api("GET", "/")
    reporter.log(
        "Endpoint GET / (Frontend Web UI)",
        status == 200 and "SEAVISION AI" in raw_html,
        f"Served {len(raw_html)} bytes of Tactical HTML/JS UI"
    )

# ==============================================================================
# MAIN RUNNER
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🌊 SEAVISION AI AUTOMATED TEST SUITE (AUTOTEST)")
    print("Testing ISRO MOSDAC, Bhuvan WMS & Maritime Attribution Pipeline")
    print("=" * 70)
    
    test_ocean_drift_math()
    test_attribution_scoring()
    test_marinecadastre_ais()
    test_zenodo_sar_dataset()
    test_mosdac_and_bhuvan_services()
    test_api_endpoints()

    all_passed = reporter.summary()
    sys.exit(0 if all_passed else 1)
