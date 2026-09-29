"""
SeaVision AI - Maritime Domain Awareness (MDA) FastAPI Backend Service
Provides RESTful APIs for SAR oil spill detection analysis, reverse drift simulation,
and multi-vessel AIS correlation scoring for maritime law enforcement & environmental protection.
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uvicorn

from synthetic_data_generator import generate_synthetic_dataset
from attribution_engine import (
    calculate_slick_origin,
    calculate_guilt_score,
    run_full_attribution,
    calculate_drift_vector
)
from ais_parser_marinecadastre import (
    generate_marinecadastre_ais_records,
    parse_marinecadastre_ais_stream
)
from sar_zenodo_dataset import get_zenodo_sentinel1_sar_sample
from mosdac_client import MosdacClient

app = FastAPI(
    title="SeaVision AI - Maritime Oil Spill Attribution Engine",
    description="SAR Dark-Patch Detection, Reverse Ocean Drift Hindcast & AIS Vessel Attribution API",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cached dataset state & MOSDAC Client
DATASET_CACHE = generate_synthetic_dataset()
MOSDAC_CLIENT = MosdacClient()

# ============================================================================
# Pydantic Request/Response Models
# ============================================================================

class DriftSimulationRequest(BaseModel):
    delta_hours: float = Field(3.5, ge=0.1, le=48.0, description="Hours before SAR detection to trace backward")
    current_speed_knots: float = Field(1.25, ge=0.0, le=10.0, description="Surface ocean current speed in knots")
    current_dir_deg: float = Field(55.0, ge=0.0, le=360.0, description="Surface current heading (degrees towards)")
    wind_speed_knots: float = Field(16.5, ge=0.0, le=75.0, description="Surface wind speed in knots")
    wind_dir_deg: float = Field(70.0, ge=0.0, le=360.0, description="Wind leeway direction (degrees towards)")
    leeway_factor: float = Field(0.03, ge=0.01, le=0.06, description="Wind leeway transfer coefficient (typically 3%)")

class ReportGenerationRequest(BaseModel):
    incident_id: str
    target_vessel_id: str
    investigator_agency: str = "Indian Coast Guard / Directorate General of Shipping"
    notes: Optional[str] = "Formal MARPOL Annex I violation referral dossier."

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def root():
    return {
        "service": "SeaVision AI API",
        "status": "OPERATIONAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "spill_analysis": "/api/v1/spill-analysis",
            "correlated_vessels": "/api/v1/correlated-vessels",
            "simulate_drift": "/api/v1/simulate-drift",
            "full_incident": "/api/v1/incident-summary"
        }
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "seavision-ai-backend"}

@app.get("/api/v1/spill-analysis")
def get_spill_analysis():
    """
    Returns detected SAR spill mask polygon, centroid, environmental vectors,
    and backward drift trajectory to the origin point.
    """
    try:
        full_analysis = run_full_attribution(DATASET_CACHE)
        spill_meta = DATASET_CACHE["spill_metadata"]
        
        return {
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
            "environmental_vectors": DATASET_CACHE["environmental_vectors"],
            "calculated_origin": full_analysis["drift_origin"],
            "drift_trajectory": full_analysis["drift_analysis"]["trajectory_path"],
            "drift_summary": {
                "total_drift_distance_km": full_analysis["drift_analysis"]["total_drift_distance_km"],
                "drift_speed_kmh": full_analysis["drift_analysis"]["drift_velocity_kmh"],
                "drift_direction_deg": full_analysis["drift_analysis"]["drift_direction_deg"],
                "delta_hours": full_analysis["drift_analysis"]["delta_hours"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute spill analysis: {str(e)}")

@app.get("/api/v1/correlated-vessels")
def get_correlated_vessels(
    min_score: float = Query(0.0, ge=0.0, le=100.0, description="Minimum guilt score filter")
):
    """
    Returns the ranked list of all vessels within the 50km surveillance radius,
    scored on Spatial Proximity (40%), Trajectory Alignment (30%), and AIS Gap Anomaly (30%).
    """
    try:
        full_analysis = run_full_attribution(DATASET_CACHE)
        ranked = [
            v for v in full_analysis["ranked_vessels"]
            if v["guilt_probability_score"] >= min_score
        ]
        
        return {
            "status": "success",
            "incident_id": full_analysis["incident_id"],
            "total_vessels_tracked": len(DATASET_CACHE["vessels"]),
            "correlated_count": len(ranked),
            "primary_suspect": ranked[0] if ranked else None,
            "ranked_vessels": ranked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to correlate vessels: {str(e)}")

@app.post("/api/v1/simulate-drift")
def simulate_drift(params: DriftSimulationRequest):
    """
    Interactive Hindcast Simulator: Accepts custom wind, current, or delta-time parameters
    and recalculates the drift trajectory and real-time vessel attribution scores.
    """
    try:
        custom_env = {
            "current": {
                "speed_knots": params.current_speed_knots,
                "direction_deg": params.current_dir_deg,
                "description": "User Simulated Current"
            },
            "wind": {
                "speed_knots": params.wind_speed_knots,
                "direction_deg": params.wind_dir_deg,
                "leeway_factor": params.leeway_factor,
                "description": "User Simulated Wind"
            }
        }

        analysis = run_full_attribution(
            dataset=DATASET_CACHE,
            custom_env=custom_env,
            custom_delta_hours=params.delta_hours
        )

        return {
            "status": "success",
            "simulation_parameters": params.model_dump(),
            "calculated_origin": analysis["drift_origin"],
            "drift_summary": analysis["drift_analysis"],
            "primary_suspect": analysis["primary_suspect"],
            "ranked_vessels": analysis["ranked_vessels"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Simulation failed: {str(e)}")

class AisUploadRequest(BaseModel):
    raw_ais_data: str

@app.get("/api/v1/mosdac/datasets")
def get_mosdac_datasets():
    """Lists official ISRO MOSDAC oceanographic satellite datasets."""
    return {"status": "success", "provider": "ISRO MOSDAC", "datasets": MOSDAC_CLIENT.get_catalog_datasets()}

@app.get("/api/v1/mosdac/telemetry")
def get_mosdac_telemetry():
    """Fetches calibrated ocean wind/current telemetry from ISRO MOSDAC."""
    return {"status": "success", "telemetry": MOSDAC_CLIENT.fetch_ocean_environmental_telemetry()}

@app.get("/api/v1/gov-map/config")
def get_government_map_config():
    """Returns official ISRO Bhuvan (NRSC) & MOSDAC Government Map Service URLs."""
    return {"status": "success", "government_map_services": MOSDAC_CLIENT.get_government_map_services()}

@app.get("/api/v1/datasets/zenodo-sar")
def get_zenodo_sar_dataset():
    """Returns official Zenodo Sentinel-1 SAR Oil Spill benchmark dataset sample & GeoJSON."""
    return {"status": "success", "zenodo_sar_dataset": get_zenodo_sentinel1_sar_sample()}

@app.get("/api/v1/datasets/marinecadastre-ais")
def get_marinecadastre_ais_dataset():
    """Returns official Marine Cadastre standard AIS records (marinecadastre.gov/accessais)."""
    records = generate_marinecadastre_ais_records()
    return {
        "status": "success",
        "format": "Marine Cadastre AIS (marinecadastre.gov/accessais)",
        "record_count": len(records),
        "records": records
    }

@app.post("/api/v1/upload-ais")
def upload_ais_dataset(payload: AisUploadRequest):
    """Parses raw Marine Cadastre AIS CSV / JSON text and correlates vessels with SAR spill."""
    parsed_vessels = parse_marinecadastre_ais_stream(payload.raw_ais_data)
    if not parsed_vessels:
        raise HTTPException(status_code=400, detail="No valid vessel records could be parsed")
    
    custom_dataset = {
        **DATASET_CACHE,
        "vessels": parsed_vessels
    }
    analysis = run_full_attribution(custom_dataset)
    return {
        "status": "success",
        "parsed_vessel_count": len(parsed_vessels),
        "primary_suspect": analysis["primary_suspect"],
        "ranked_vessels": analysis["ranked_vessels"],
        "drift_origin": analysis["drift_origin"]
    }

@app.get("/api/v1/incident-summary")
def get_incident_summary():
    """
    Consolidated payload containing the complete state for mission dashboard initialization.
    """
    analysis = run_full_attribution(DATASET_CACHE)
    return {
        "status": "success",
        "dataset_info": {
            "region": DATASET_CACHE["region"],
            "version": DATASET_CACHE["dataset_version"],
            "generated_at": DATASET_CACHE["generated_at"]
        },
        "spill_data": DATASET_CACHE["spill_metadata"],
        "environmental_vectors": DATASET_CACHE["environmental_vectors"],
        "drift_origin": analysis["drift_origin"],
        "drift_analysis": analysis["drift_analysis"],
        "vessels": analysis["ranked_vessels"]
    }

@app.post("/api/v1/generate-report")
def generate_evidence_report(payload: ReportGenerationRequest):
    """
    Generates a structured MARPOL / Coast Guard legal evidence package for the target vessel.
    """
    target = None
    full_analysis = run_full_attribution(DATASET_CACHE)
    for v in full_analysis["ranked_vessels"]:
        if v["vessel_id"] == payload.target_vessel_id:
            target = v
            break

    if not target:
        raise HTTPException(status_code=404, detail=f"Vessel {payload.target_vessel_id} not found")

    spill = DATASET_CACHE["spill_metadata"]

    dossier = {
        "report_id": f"REP-{spill['incident_id']}-{target['imo'] or target['mmsi']}",
        "filing_timestamp": datetime.now(timezone.utc).isoformat(),
        "authority": payload.investigator_agency,
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
        "officer_notes": payload.notes
    }

    return {"status": "success", "evidence_dossier": dossier}

if __name__ == "__main__":
    print("Starting SeaVision AI FastAPI Backend Service on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
