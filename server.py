"""
SeaVision AI - Full-Stack Production HTTP & REST API Server
Zero-dependency, high-performance Python HTTP server serving both the REST API
and the Tactical Maritime Command Center frontend.
"""

import os
import sys
import json
import mimetypes
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Core attribution engine, Marine Cadastre AIS & Zenodo SAR datasets
from synthetic_data_generator import generate_synthetic_dataset, get_scenario_dataset
from attribution_engine import (
    calculate_slick_origin,
    calculate_guilt_score,
    run_full_attribution,
    calculate_drift_vector
)
from ais_parser_marinecadastre import (
    generate_marinecadastre_ais_records,
    parse_marinecadastre_ais_stream,
    VESSEL_TYPE_MAP,
    NAV_STATUS_MAP
)
from sar_zenodo_dataset import get_zenodo_sentinel1_sar_sample
from mosdac_client import MosdacClient

PORT = int(os.environ.get("PORT", 8000))
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# In-memory dataset instance & MOSDAC Client
CURRENT_SCENARIO_ID = "mumbai_high"
CURRENT_DATASET = get_scenario_dataset("mumbai_high")
MOSDAC_CLIENT = MosdacClient()


class SeaVisionHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status_code=200):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _serve_file(self, filepath, content_type="text/html"):
        if not os.path.exists(filepath):
            self.send_error(404, f"File {os.path.basename(filepath)} not found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/api/health":
            self._send_json({"status": "healthy", "service": "seavision-ai-backend", "port": PORT})
            return

        elif path == "/api/v1/spill-analysis":
            try:
                full_analysis = run_full_attribution(CURRENT_DATASET)
                spill_meta = CURRENT_DATASET["spill_metadata"]
                data = {
                    "status": "success",
                    "incident_id": spill_meta["incident_id"],
                    "satellite_sensor": spill_meta["satellite_sensor"],
                    "detection_timestamp": spill_meta["detection_timestamp"],
                    "estimated_spill_timestamp": spill_meta["estimated_spill_timestamp"],
                    "estimated_area_sq_km": spill_meta["estimated_area_sq_km"],
                    "estimated_volume_bbls": spill_meta["estimated_volume_bbls"],
                    "sar_confidence_score": spill_meta["sar_confidence_score"],
                    "slick_axis_heading_deg": spill_meta["slick_axis_heading_deg"],
                    "bounding_box": spill_meta["bounding_box"],
                    "detected_centroid": spill_meta["detected_centroid"],
                    "polygon_geojson": spill_meta["polygon_geojson"],
                    "environmental_vectors": CURRENT_DATASET["environmental_vectors"],
                    "calculated_origin": full_analysis["drift_origin"],
                    "drift_trajectory": full_analysis["drift_analysis"]["trajectory_path"],
                    "drift_summary": {
                        "total_drift_distance_km": full_analysis["drift_analysis"]["total_drift_distance_km"],
                        "drift_speed_kmh": full_analysis["drift_analysis"]["drift_velocity_kmh"],
                        "drift_direction_deg": full_analysis["drift_analysis"]["drift_direction_deg"],
                        "delta_hours": full_analysis["drift_analysis"]["delta_hours"]
                    }
                }
                self._send_json(data)
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/correlated-vessels":
            try:
                full_analysis = run_full_attribution(CURRENT_DATASET)
                min_score = float(params.get("min_score", [0.0])[0])
                ranked = [
                    v for v in full_analysis["ranked_vessels"]
                    if v["guilt_probability_score"] >= min_score
                ]
                data = {
                    "status": "success",
                    "incident_id": full_analysis["incident_id"],
                    "total_vessels_tracked": len(CURRENT_DATASET["vessels"]),
                    "correlated_count": len(ranked),
                    "primary_suspect": ranked[0] if ranked else None,
                    "ranked_vessels": ranked
                }
                self._send_json(data)
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/mosdac/datasets":
            try:
                datasets = MOSDAC_CLIENT.get_catalog_datasets()
                self._send_json({"status": "success", "provider": "ISRO MOSDAC", "datasets": datasets})
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/mosdac/telemetry":
            try:
                telemetry = MOSDAC_CLIENT.fetch_ocean_environmental_telemetry()
                self._send_json({"status": "success", "telemetry": telemetry})
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/gov-map/config":
            try:
                gov_maps = MOSDAC_CLIENT.get_government_map_services()
                self._send_json({"status": "success", "government_map_services": gov_maps})
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/datasets/zenodo-sar":
            try:
                sar_sample = get_zenodo_sentinel1_sar_sample()
                self._send_json({"status": "success", "zenodo_sar_dataset": sar_sample})
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/datasets/marinecadastre-ais":
            try:
                records = generate_marinecadastre_ais_records()
                self._send_json({
                    "status": "success",
                    "format": "Marine Cadastre AIS (marinecadastre.gov/accessais)",
                    "record_count": len(records),
                    "records": records
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/incidents":
            try:
                incidents = [
                    {
                        "scenario_id": "mumbai_high",
                        "scenario_title": "Mumbai High Offshore Basin (Arabian Sea)",
                        "incident_id": "SV-IND-2026-0929-01",
                        "region": "Indian EEZ - Mumbai High Sector",
                        "detected_centroid": {"lat": 19.1820, "lon": 72.1150},
                        "estimated_area_sq_km": 14.82,
                        "satellite_sensor": "Sentinel-1C C-SAR",
                        "suspect_vessel": "MT ARABIAN TITAN (VLCC Tanker)",
                        "guilt_probability": "100%",
                        "status": "CRITICAL ACTIVE ALERT"
                    },
                    {
                        "scenario_id": "gulf_of_kachchh",
                        "scenario_title": "Gulf of Kachchh Tanker Fairway (Gujarat)",
                        "incident_id": "SV-IND-2026-GOK-02",
                        "region": "Indian EEZ - Kandla Shipping Approaches",
                        "detected_centroid": {"lat": 22.5120, "lon": 69.2450},
                        "estimated_area_sq_km": 8.45,
                        "satellite_sensor": "Sentinel-1B C-SAR",
                        "suspect_vessel": "MT OCEANIC GLORY (Chemical Tanker)",
                        "guilt_probability": "96%",
                        "status": "ACTIVE ALERT"
                    },
                    {
                        "scenario_id": "bay_of_bengal",
                        "scenario_title": "Bay of Bengal Approaches (Paradip Basin)",
                        "incident_id": "SV-IND-2026-BOB-03",
                        "region": "Indian EEZ - Odisha Deepwater Sector",
                        "detected_centroid": {"lat": 20.1450, "lon": 86.8210},
                        "estimated_area_sq_km": 19.30,
                        "satellite_sensor": "Sentinel-1A C-SAR",
                        "suspect_vessel": "MV BENGAL STAR (Ore-Bulk-Oil)",
                        "guilt_probability": "94%",
                        "status": "ACTIVE ALERT"
                    }
                ]
                self._send_json({"status": "success", "active_scenario": CURRENT_SCENARIO_ID, "incidents": incidents})
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/live-alerts":
            try:
                full_analysis = run_full_attribution(CURRENT_DATASET)
                spill = CURRENT_DATASET["spill_metadata"]
                suspect = full_analysis["ranked_vessels"][0] if full_analysis["ranked_vessels"] else None
                now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

                alerts = [
                    {
                        "id": f"ALT-{int(datetime.now(timezone.utc).timestamp())}-01",
                        "time": now_str,
                        "level": "CRITICAL",
                        "badge": "MARPOL ANNEX I VIOLATION",
                        "title": f"High-Confidence Polluter Identified: {suspect['vessel_name'] if suspect else 'UNKNOWN'}",
                        "message": f"Kinematic reverse-drift match calculated at {suspect['guilt_probability_score']}% probability with a deliberate {suspect['metrics']['gap_duration_minutes']} min AIS blackout at discharge centroid.",
                        "action_required": "Immediate Indian Coast Guard Intercept & PSC Bilge Tank Sampling",
                        "target_vessel": suspect["vessel_name"] if suspect else "N/A",
                        "mmsi": suspect["mmsi"] if suspect else 0,
                        "coordinates": f"{spill['detected_centroid']['lat']}°N, {spill['detected_centroid']['lon']}°E"
                    },
                    {
                        "id": f"ALT-{int(datetime.now(timezone.utc).timestamp())}-02",
                        "time": now_str,
                        "level": "WARNING",
                        "badge": "SAR SEGMENTATION",
                        "title": f"Sentinel-1 SAR Slick Detected ({spill['estimated_area_sq_km']} km²)",
                        "message": f"Granule processed with U-Net dark-patch segmentation. High-density crude slick axis heading {spill['slick_axis_heading_deg']}°.",
                        "satellite": spill["satellite_sensor"],
                        "confidence": f"{spill['sar_confidence_score'] * 100}%"
                    },
                    {
                        "id": f"ALT-{int(datetime.now(timezone.utc).timestamp())}-03",
                        "time": now_str,
                        "level": "INFO",
                        "badge": "MOSDAC TELEMETRY",
                        "title": "ISRO Oceansat-3 & SARAL Ocean Vectors Assimilated",
                        "message": f"Hydrodynamic drift force vector: Current {CURRENT_DATASET['environmental_vectors']['current']['speed_knots']} kts @ {CURRENT_DATASET['environmental_vectors']['current']['direction_deg']}° + Wind {CURRENT_DATASET['environmental_vectors']['wind']['speed_knots']} kts @ {CURRENT_DATASET['environmental_vectors']['wind']['direction_deg']}°."
                    }
                ]
                self._send_json({"status": "success", "scenario": CURRENT_SCENARIO_ID, "alerts": alerts})
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return

        elif path == "/api/v1/incident-summary":
            try:
                analysis = run_full_attribution(CURRENT_DATASET)
                data = {
                    "status": "success",
                    "dataset_info": {
                        "scenario_id": CURRENT_DATASET.get("scenario_id", "mumbai_high"),
                        "region": CURRENT_DATASET["region"],
                        "version": CURRENT_DATASET["dataset_version"],
                        "generated_at": CURRENT_DATASET["generated_at"]
                    },
                    "spill_data": CURRENT_DATASET["spill_metadata"],
                    "environmental_vectors": CURRENT_DATASET["environmental_vectors"],
                    "drift_origin": analysis["drift_origin"],
                    "drift_analysis": analysis["drift_analysis"],
                    "vessels": analysis["ranked_vessels"]
                }
                self._send_json(data)
            except Exception as e:
                self._send_json({"error": str(e)}, status_code=500)
            return


        # Serve static UI (index.html or assets)
        if path in ["/", "/index.html"]:
            index_path = os.path.join(STATIC_DIR, "index.html")
            self._serve_file(index_path, "text/html")
            return

        # Clean subpath asset serving
        rel_path = path.lstrip("/")
        target_file = os.path.join(STATIC_DIR, rel_path)
        if os.path.exists(target_file) and not os.path.isdir(target_file):
            ctype, _ = mimetypes.guess_type(target_file)
            self._serve_file(target_file, ctype or "application/octet-stream")
            return

        # Fallback to index.html for SPA routing
        self._serve_file(os.path.join(STATIC_DIR, "index.html"), "text/html")

    def do_POST(self):
        global CURRENT_DATASET, CURRENT_SCENARIO_ID
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            self._send_json({"error": "Invalid JSON in request body"}, status_code=400)
            return

        if path == "/api/v1/simulate-drift":
            try:
                delta_h = float(payload.get("delta_hours", 3.5))
                cur_spd = float(payload.get("current_speed_knots", 1.25))
                cur_dir = float(payload.get("current_dir_deg", 55.0))
                w_spd = float(payload.get("wind_speed_knots", 16.5))
                w_dir = float(payload.get("wind_dir_deg", 70.0))
                leeway = float(payload.get("leeway_factor", 0.03))

                custom_env = {
                    "current": {
                        "speed_knots": cur_spd,
                        "direction_deg": cur_dir,
                        "description": "User Simulated Current"
                    },
                    "wind": {
                        "speed_knots": w_spd,
                        "direction_deg": w_dir,
                        "leeway_factor": leeway,
                        "description": "User Simulated Wind"
                    }
                }

                analysis = run_full_attribution(
                    dataset=CURRENT_DATASET,
                    custom_env=custom_env,
                    custom_delta_hours=delta_h
                )

                response_data = {
                    "status": "success",
                    "simulation_parameters": payload,
                    "calculated_origin": analysis["drift_origin"],
                    "drift_summary": analysis["drift_analysis"],
                    "primary_suspect": analysis["primary_suspect"],
                    "ranked_vessels": analysis["ranked_vessels"]
                }
                self._send_json(response_data)
            except Exception as e:
                self._send_json({"error": f"Simulation failed: {str(e)}"}, status_code=400)
            return

        elif path == "/api/v1/upload-ais":
            try:
                raw_ais = payload.get("raw_ais_data", "")
                if not raw_ais:
                    self._send_json({"error": "No raw_ais_data provided"}, status_code=400)
                    return

                parsed_vessels = parse_marinecadastre_ais_stream(raw_ais)
                if not parsed_vessels:
                    self._send_json({"error": "No valid vessel tracks could be parsed from input"}, status_code=400)
                    return

                # Update current dataset with custom ingested vessels
                custom_dataset = {
                    **CURRENT_DATASET,
                    "vessels": parsed_vessels
                }

                analysis = run_full_attribution(custom_dataset)

                self._send_json({
                    "status": "success",
                    "parsed_vessel_count": len(parsed_vessels),
                    "primary_suspect": analysis["primary_suspect"],
                    "ranked_vessels": analysis["ranked_vessels"],
                    "drift_origin": analysis["drift_origin"]
                })
            except Exception as e:
                self._send_json({"error": f"Failed to parse AIS dataset: {str(e)}"}, status_code=400)
            return

        elif path == "/api/v1/generate-report":
            try:
                target_id = payload.get("target_vessel_id", "VESSEL-002")
                agency = payload.get("investigator_agency", "Directorate General of Shipping / Indian Coast Guard")
                notes = payload.get("notes", "Formal MARPOL Annex I violation referral dossier.")

                full_analysis = run_full_attribution(CURRENT_DATASET)
                target = next((v for v in full_analysis["ranked_vessels"] if v["vessel_id"] == target_id), None)

                if not target:
                    self._send_json({"error": f"Vessel {target_id} not found"}, status_code=404)
                    return

                spill = CURRENT_DATASET["spill_metadata"]
                dossier = {
                    "report_id": f"REP-{spill['incident_id']}-{target['imo'] or target['mmsi']}",
                    "filing_timestamp": datetime.now(timezone.utc).isoformat(),
                    "authority": agency,
                    "incident_id": spill["incident_id"],
                    "sar_detection": {
                        "satellite": spill["satellite_sensor"],
                        "slick_area_sq_km": spill["estimated_area_sq_km"],
                        "estimated_volume_bbls": spill["estimated_volume_bbls"],
                        "detection_coordinates": spill["detected_centroid"]
                    },
                    "hindcast_origin": full_analysis["drift_origin"],
                    "suspect_vessel": {
                        "name": target["vessel_name"],
                        "imo": target["imo"],
                        "mmsi": target["mmsi"],
                        "flag": target["flag"],
                        "type": target["type"],
                        "guilt_probability_score": target["guilt_probability_score"],
                        "classification": target["classification"]
                    },
                    "forensic_evidence_summary": {
                        "spatial_proximity": f"{target['metrics']['distance_at_spill_km']} km CPA at estimated spill time",
                        "trajectory_alignment": f"{target['metrics']['heading_deviation_deg']}° angular deviation from slick axis",
                        "ais_transponder_anomalies": f"Transponder disabled for {target['metrics']['gap_duration_minutes']} min within {target['metrics']['gap_distance_to_origin_km']} km of origin" if target['metrics']['ais_gap_detected'] else "Continuous signal logged",
                        "reason_codes": target["reason_codes"]
                    },
                    "legal_recommendation": (
                        "SUBSTANTIAL EVIDENCE OF MARPOL ANNEX I DISCHARGE: Request Port State Control inspection upon berth, "
                        "sampling of bilge / slop tanks, and detention of vessel for oil fingerprinting gas chromatography."
                        if target["guilt_probability_score"] >= 80.0 else
                        "INSUFFICIENT CORRELATION: Vessel cleared of immediate suspicion based on kinematic trajectory."
                    ),
                    "officer_notes": notes
                }
                self._send_json({"status": "success", "evidence_dossier": dossier})
            except Exception as e:
                self._send_json({"error": f"Report generation failed: {str(e)}"}, status_code=500)
            return

        elif path == "/api/v1/incidents/select":
            try:
                scen_id = payload.get("scenario_id", "mumbai_high")
                CURRENT_SCENARIO_ID = scen_id
                CURRENT_DATASET = get_scenario_dataset(scen_id)
                full_analysis = run_full_attribution(CURRENT_DATASET)
                self._send_json({
                    "status": "success",
                    "scenario_id": CURRENT_SCENARIO_ID,
                    "incident_id": CURRENT_DATASET["spill_metadata"]["incident_id"],
                    "region": CURRENT_DATASET["region"],
                    "spill_metadata": CURRENT_DATASET["spill_metadata"],
                    "environmental_vectors": CURRENT_DATASET["environmental_vectors"],
                    "analysis": full_analysis
                })
            except Exception as e:
                self._send_json({"error": f"Failed to select scenario: {str(e)}"}, status_code=500)
            return

        elif path == "/api/v1/dispatch-action":
            try:
                target_name = payload.get("vessel_name", "MT ARABIAN TITAN")
                mmsi = payload.get("mmsi", 636018244)
                action_type = payload.get("action_type", "COAST_GUARD_INTERCEPT")
                now_str = datetime.now(timezone.utc).isoformat()
                
                dispatch_record = {
                    "dispatch_id": f"DSP-ICG-{int(datetime.now(timezone.utc).timestamp())}",
                    "timestamp": now_str,
                    "priority": "FLASH IMMEDIATE",
                    "issuing_authority": "Maritime Rescue Coordination Centre (MRCC) Mumbai",
                    "target_vessel": target_name,
                    "target_mmsi": mmsi,
                    "action": "Dispatch Fast Patrol Vessel (FPV) & Dornier 228 Maritime Surveillance Aircraft",
                    "directives": [
                        "1. Intercept suspect vessel in Indian EEZ corridor",
                        "2. Deploy Aerial FLIR / SLAR pollution sensor pod",
                        "3. Collect physical ocean surface grab samples for GC-MS fingerprinting",
                        "4. Issue immediate MARPOL Form B Notice of Violation to Master"
                    ],
                    "status": "ORDER TRANSMITTED TO COAST GUARD REGIONAL HQ"
                }
                self._send_json({"status": "success", "dispatch_record": dispatch_record})
            except Exception as e:
                self._send_json({"error": f"Dispatch failed: {str(e)}"}, status_code=500)
            return


        self._send_json({"error": "Endpoint not found"}, status_code=404)

def run_server(port=PORT):
    os.makedirs(STATIC_DIR, exist_ok=True)
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SeaVisionHandler)
    print("=" * 70)
    print(f"🌊 SeaVision AI Full-Stack Platform is LIVE")
    print(f"🛰️  Maritime Command Center UI:  http://localhost:{port}/")
    print(f"📡 REST API Root:                http://localhost:{port}/api/v1/spill-analysis")
    print(f"⚓ Health Check:                 http://localhost:{port}/api/health")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down SeaVision AI server gracefully...")
        httpd.server_close()

if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port_arg)
