"""
SeaVision AI - Maritime Domain Awareness (MDA) Synthetic Data Generator
Generates realistic SAR satellite metadata, detected oil slick geometries,
oceanographic/meteorological environmental vectors, and multi-vessel AIS trajectories
within the Indian Exclusive Economic Zone (EEZ) off the coast of Mumbai (Arabian Sea).
"""

import json
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

def generate_synthetic_dataset() -> Dict[str, Any]:
    """
    Creates a benchmark synthetic dataset for oil spill hindcast drift correlation.
    Detection Location: Mumbai High Offshore Basin (~19.12° N, 71.95° E)
    Detection Time: T_detect (Base reference time)
    Estimated Spill Event: 3.5 hours prior to SAR pass
    """
    t_detect = datetime(2026, 9, 29, 10, 0, 0, tzinfo=timezone.utc)
    delta_hours = 3.5
    t_spill = t_detect - timedelta(hours=delta_hours)

    # 1. Environmental Vectors (Current & Wind)
    # Wind: 16.5 knots blowing TOWARDS 070° (from 250° WSW)
    # Current: 1.25 knots flowing TOWARDS 055° (ENE)
    environmental_data = {
        "current": {
            "speed_knots": 1.25,
            "direction_deg": 55.0,  # Direction towards which ocean current flows (degrees from North)
            "description": "Northeast Arabian Sea surface current"
        },
        "wind": {
            "speed_knots": 16.5,
            "direction_deg": 70.0,  # Direction towards which wind pushes (leeway vector)
            "leeway_factor": 0.03,  # Standard 3% wind leeway for oil slicks
            "description": "Moderate South-Westerly Monsoon Wind"
        }
    }

    # 2. Detected Spill Observation (SAR Dark-patch Detection)
    # Centroid of the slick as detected by SAR at t_detect
    detected_centroid = [72.1150, 19.1820]  # [Lon, Lat]

    # Geometric polygon for an elongated slick (major axis oriented along ~060 deg)
    # Generated with offset coordinates simulating an aged, spreading oil plume
    slick_coordinates = [
        [
            [72.1020, 19.1710],
            [72.1105, 19.1765],
            [72.1220, 19.1860],
            [72.1280, 19.1915],
            [72.1250, 19.1940],
            [72.1140, 19.1870],
            [72.1060, 19.1790],
            [72.0980, 19.1730],
            [72.1020, 19.1710]
        ]
    ]

    spill_metadata = {
        "incident_id": "SV-IND-2026-0929-01",
        "detection_timestamp": t_detect.isoformat(),
        "estimated_spill_timestamp": t_spill.isoformat(),
        "estimated_drift_duration_hours": delta_hours,
        "satellite_sensor": "Sentinel-1C C-SAR (Interferometric Wide Swath)",
        "polarization": "VV + VH",
        "spatial_resolution_meters": 10.0,
        "bounding_box": {
            "min_lon": 72.08,
            "min_lat": 19.15,
            "max_lon": 72.15,
            "max_lat": 19.22
        },
        "estimated_area_sq_km": 14.82,
        "estimated_volume_bbls": 850,
        "slick_axis_heading_deg": 58.5,
        "sar_confidence_score": 0.962,
        "polygon_geojson": {
            "type": "Polygon",
            "coordinates": slick_coordinates
        },
        "detected_centroid": {
            "lon": detected_centroid[0],
            "lat": detected_centroid[1]
        }
    }

    # 3. AIS Trajectories (50 km bounding radius)
    # Vessel B: Guilty crude oil tanker (MT ARABIAN TITAN) - deliberate AIS blackout at spill origin
    # Vessel A: Innocent container ship (MV INDUS TRADER) - normal continuous transit 22 km south
    # Vessel C: Small coastal fishing trawler (FV SAGAR RATNA) - erratic pattern 35 km away

    # Timesteps from T-4.5h to T+0.5h in 15-min intervals
    timestamps = [t_detect - timedelta(minutes=15 * i) for i in range(20, -3, -1)]

    # Vessel B (Guilty Tanker - IMO 9384812)
    # Physical origin of spill is calculated at [72.023, 19.130] at T-3.5h (06:30 UTC)
    # The vessel crosses this exact point during an intentional 45-minute AIS blackout
    vessel_b_points = [
        {"time": (t_detect - timedelta(hours=4.5)).isoformat(), "lon": 71.9100, "lat": 19.0400, "sog": 14.0, "cog": 58.5, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=4.0)).isoformat(), "lon": 71.9660, "lat": 19.0850, "sog": 13.8, "cog": 58.5, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=3.75)).isoformat(), "lon": 71.9945, "lat": 19.1075, "sog": 13.2, "cog": 58.5, "status": "Underway using engine", "ais_active": True},
        
        # --- AIS BLACKOUT GAP INITIATED HERE (06:15 to 07:00 UTC) ---
        # Vessel transits silently through [72.0230, 19.1300] at T-3.5h (06:30 UTC)
        
        # --- AIS RESTORED ---
        {"time": (t_detect - timedelta(hours=3.0)).isoformat(), "lon": 72.0790, "lat": 19.1750, "sog": 14.1, "cog": 58.5, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=2.0)).isoformat(), "lon": 72.1910, "lat": 19.2650, "sog": 14.0, "cog": 58.5, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=1.0)).isoformat(), "lon": 72.3030, "lat": 19.3550, "sog": 14.2, "cog": 58.5, "status": "Underway using engine", "ais_active": True},
        {"time": t_detect.isoformat(), "lon": 72.4150, "lat": 19.4450, "sog": 14.0, "cog": 58.5, "status": "Underway using engine", "ais_active": True}
    ]

    # Vessel A (Innocent Container Ship - IMO 9723411)
    vessel_a_points = [
        {"time": (t_detect - timedelta(hours=4.5)).isoformat(), "lon": 71.8500, "lat": 18.7500, "sog": 18.2, "cog": 72.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=3.5)).isoformat(), "lon": 72.0150, "lat": 18.8200, "sog": 18.1, "cog": 72.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=2.5)).isoformat(), "lon": 72.1800, "lat": 18.8900, "sog": 18.0, "cog": 71.5, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=1.5)).isoformat(), "lon": 72.3450, "lat": 18.9600, "sog": 17.9, "cog": 72.0, "status": "Underway", "ais_active": True},
        {"time": t_detect.isoformat(), "lon": 72.5100, "lat": 19.0300, "sog": 17.8, "cog": 72.0, "status": "Underway", "ais_active": True}
    ]

    # Vessel C (Innocent Fishing Vessel - MMSI 419001882)
    vessel_c_points = [
        {"time": (t_detect - timedelta(hours=4.0)).isoformat(), "lon": 72.3800, "lat": 19.3500, "sog": 4.5, "cog": 140.0, "status": "Engaged in fishing", "ais_active": True},
        {"time": (t_detect - timedelta(hours=3.0)).isoformat(), "lon": 72.3950, "lat": 19.3200, "sog": 3.8, "cog": 210.0, "status": "Engaged in fishing", "ais_active": True},
        {"time": (t_detect - timedelta(hours=2.0)).isoformat(), "lon": 72.3700, "lat": 19.2900, "sog": 4.2, "cog": 320.0, "status": "Engaged in fishing", "ais_active": True},
        {"time": (t_detect - timedelta(hours=1.0)).isoformat(), "lon": 72.3550, "lat": 19.3300, "sog": 5.1, "cog": 045.0, "status": "Engaged in fishing", "ais_active": True},
        {"time": t_detect.isoformat(), "lon": 72.3900, "lat": 19.3700, "sog": 4.0, "cog": 120.0, "status": "Engaged in fishing", "ais_active": True}
    ]

    # Vessel D (Bulk Carrier - IMO 9456123, Medium proximity, normal passage, no AIS gap)
    vessel_d_points = [
        {"time": (t_detect - timedelta(hours=4.5)).isoformat(), "lon": 72.1000, "lat": 18.9000, "sog": 11.5, "cog": 340.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=3.5)).isoformat(), "lon": 72.0650, "lat": 19.0000, "sog": 11.5, "cog": 340.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=2.5)).isoformat(), "lon": 72.0300, "lat": 19.1000, "sog": 11.4, "cog": 340.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=1.5)).isoformat(), "lon": 71.9950, "lat": 19.2000, "sog": 11.5, "cog": 340.0, "status": "Underway", "ais_active": True},
        {"time": t_detect.isoformat(), "lon": 71.9600, "lat": 19.3000, "sog": 11.6, "cog": 340.0, "status": "Underway", "ais_active": True}
    ]

    vessels = [
        {
            "id": "VESSEL-002",
            "name": "MT ARABIAN TITAN",
            "imo": 9384812,
            "mmsi": 636018244,
            "flag": "Liberia (Flag of Convenience)",
            "type": "Crude Oil Tanker (VLCC)",
            "length_m": 333,
            "deadweight_tonnage": 305000,
            "cargo": "Heavy Crude Oil (Iranian Light Blend)",
            "destination": "JNPT Port, Mumbai",
            "risk_profile": "High Risk - Previous MARPOL Annex I Deficiencies",
            "ais_gap_detected": True,
            "gap_duration_minutes": 45,
            "gap_location_approx": [72.0230, 19.1300],
            "track": vessel_b_points
        },
        {
            "id": "VESSEL-001",
            "name": "MV INDUS TRADER",
            "imo": 9723411,
            "mmsi": 419000541,
            "flag": "India",
            "type": "Container Ship (Post-Panamax)",
            "length_m": 294,
            "deadweight_tonnage": 68000,
            "cargo": "Standard Containerized Cargo",
            "destination": "Pipavav Port, Gujarat",
            "risk_profile": "Low Risk - Fully Compliant",
            "ais_gap_detected": False,
            "gap_duration_minutes": 0,
            "gap_location_approx": None,
            "track": vessel_a_points
        },
        {
            "id": "VESSEL-003",
            "name": "FV SAGAR RATNA",
            "imo": None,
            "mmsi": 419001882,
            "flag": "India",
            "type": "Mechanized Fishing Trawler",
            "length_m": 28,
            "deadweight_tonnage": 180,
            "cargo": "Fishery Catch",
            "destination": "Sassoon Docks, Mumbai",
            "risk_profile": "Low Risk - Artisanal Vessel",
            "ais_gap_detected": False,
            "gap_duration_minutes": 0,
            "gap_location_approx": None,
            "track": vessel_c_points
        },
        {
            "id": "VESSEL-004",
            "name": "MV PACIFIC BULKER",
            "imo": 9456123,
            "mmsi": 352001923,
            "flag": "Panama",
            "type": "Dry Bulk Carrier",
            "length_m": 225,
            "deadweight_tonnage": 76000,
            "cargo": "Iron Ore Pellets",
            "destination": "Mormugao Port, Goa",
            "risk_profile": "Low Risk - Regular Liner Route",
            "ais_gap_detected": False,
            "gap_duration_minutes": 0,
            "gap_location_approx": None,
            "track": vessel_d_points
        }
    ]

    return {
        "status": "success",
        "dataset_version": "2.4-mda-sar",
        "scenario_id": "mumbai_high",
        "scenario_title": "Mumbai High Offshore Basin (Arabian Sea)",
        "region": "Indian EEZ - Mumbai Offshore Basin, Arabian Sea",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environmental_vectors": environmental_data,
        "spill_metadata": spill_metadata,
        "vessels": vessels
    }

def generate_gulf_of_kachchh_dataset() -> Dict[str, Any]:
    """
    Scenario 2: Gulf of Kachchh / Kandla Crude Corridor (Gujarat)
    Chemical Tanker MT OCEANIC GLORY (MMSI: 419001234)
    """
    t_detect = datetime.now(timezone.utc)
    delta_hours = 2.5
    t_spill = t_detect - timedelta(hours=delta_hours)

    environmental_data = {
        "current": {
            "speed_knots": 1.80,
            "direction_deg": 80.0,
            "description": "High-velocity tidal current - Gulf of Kachchh"
        },
        "wind": {
            "speed_knots": 14.0,
            "direction_deg": 95.0,
            "leeway_factor": 0.03,
            "description": "North-Westerly Coastal Breeze"
        }
    }

    slick_coordinates = [
        [
            [69.2300, 22.5050],
            [69.2420, 22.5100],
            [69.2550, 22.5180],
            [69.2600, 22.5240],
            [69.2520, 22.5260],
            [69.2400, 22.5190],
            [69.2310, 22.5120],
            [69.2300, 22.5050]
        ]
    ]

    spill_metadata = {
        "incident_id": "SV-IND-2026-GOK-02",
        "detection_timestamp": t_detect.isoformat(),
        "estimated_spill_timestamp": t_spill.isoformat(),
        "estimated_drift_duration_hours": delta_hours,
        "satellite_sensor": "Sentinel-1B C-SAR (Stripmap Mode)",
        "polarization": "VV + VH",
        "spatial_resolution_meters": 10.0,
        "bounding_box": {"min_lon": 69.20, "min_lat": 22.48, "max_lon": 69.28, "max_lat": 22.55},
        "estimated_area_sq_km": 8.45,
        "estimated_volume_bbls": 420,
        "slick_axis_heading_deg": 82.0,
        "sar_confidence_score": 0.948,
        "polygon_geojson": {"type": "Polygon", "coordinates": slick_coordinates},
        "detected_centroid": {"lon": 69.2450, "lat": 22.5120}
    }

    vessel_b_points = [
        {"time": (t_detect - timedelta(hours=3.5)).isoformat(), "lon": 69.1100, "lat": 22.4600, "sog": 12.0, "cog": 75.0, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=3.0)).isoformat(), "lon": 69.1350, "lat": 22.4750, "sog": 12.1, "cog": 76.0, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=2.75)).isoformat(), "lon": 69.1550, "lat": 22.4860, "sog": 11.9, "cog": 75.0, "status": "Underway using engine", "ais_active": True},
        # AIS gap near 69.1750, 22.4980 (35 min blackout)
        {"time": (t_detect - timedelta(hours=2.0)).isoformat(), "lon": 69.2100, "lat": 22.5200, "sog": 12.2, "cog": 77.0, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=1.0)).isoformat(), "lon": 69.2600, "lat": 22.5500, "sog": 12.0, "cog": 76.0, "status": "Underway using engine", "ais_active": True},
        {"time": t_detect.isoformat(), "lon": 69.3100, "lat": 22.5800, "sog": 12.0, "cog": 76.0, "status": "Underway using engine", "ais_active": True}
    ]

    vessel_a_points = [
        {"time": (t_detect - timedelta(hours=3.5)).isoformat(), "lon": 69.3200, "lat": 22.6200, "sog": 15.0, "cog": 150.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=2.5)).isoformat(), "lon": 69.3400, "lat": 22.5800, "sog": 15.0, "cog": 150.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=1.5)).isoformat(), "lon": 69.3600, "lat": 22.5400, "sog": 15.0, "cog": 150.0, "status": "Underway", "ais_active": True},
        {"time": t_detect.isoformat(), "lon": 69.3800, "lat": 22.5000, "sog": 15.0, "cog": 150.0, "status": "Underway", "ais_active": True}
    ]

    vessels = [
        {
            "id": "VESSEL-GOK-01",
            "name": "MT OCEANIC GLORY",
            "imo": 9411223,
            "mmsi": 419001234,
            "flag": "Marshall Islands",
            "type": "Chemical & Product Tanker",
            "length_m": 183,
            "deadweight_tonnage": 46000,
            "cargo": "High Density Fuel Oil (Bunker C)",
            "destination": "Deendayal Port (Kandla), India",
            "risk_profile": "High Risk - Flag of Convenience",
            "ais_gap_detected": True,
            "gap_duration_minutes": 35,
            "gap_location_approx": [69.1750, 22.4980],
            "track": vessel_b_points
        },
        {
            "id": "VESSEL-GOK-02",
            "name": "MV GUJARAT EXPRESS",
            "imo": 9308871,
            "mmsi": 419003322,
            "flag": "India",
            "type": "General Cargo Liner",
            "length_m": 160,
            "deadweight_tonnage": 22000,
            "cargo": "Containerized Goods",
            "destination": "Mundra Port, Gujarat",
            "risk_profile": "Low Risk - Regular Liner",
            "ais_gap_detected": False,
            "gap_duration_minutes": 0,
            "gap_location_approx": None,
            "track": vessel_a_points
        }
    ]

    return {
        "status": "success",
        "dataset_version": "2.4-mda-sar",
        "scenario_id": "gulf_of_kachchh",
        "scenario_title": "Gulf of Kachchh Tanker Fairway (Gujarat)",
        "region": "Indian EEZ - Gulf of Kachchh, Arabian Sea",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environmental_vectors": environmental_data,
        "spill_metadata": spill_metadata,
        "vessels": vessels
    }

def generate_bay_of_bengal_dataset() -> Dict[str, Any]:
    """
    Scenario 3: Bay of Bengal / Paradip Basin (Odisha)
    Bulk Carrier MV BENGAL STAR (MMSI: 563009876)
    """
    t_detect = datetime.now(timezone.utc)
    delta_hours = 4.0
    t_spill = t_detect - timedelta(hours=delta_hours)

    environmental_data = {
        "current": {
            "speed_knots": 1.10,
            "direction_deg": 40.0,
            "description": "East India Coastal Current (EICC)"
        },
        "wind": {
            "speed_knots": 18.0,
            "direction_deg": 50.0,
            "leeway_factor": 0.03,
            "description": "South-West Bay of Bengal Wind"
        }
    }

    slick_coordinates = [
        [
            [86.8000, 20.1300],
            [86.8150, 20.1400],
            [86.8320, 20.1550],
            [86.8400, 20.1650],
            [86.8300, 20.1680],
            [86.8120, 20.1500],
            [86.8010, 20.1380],
            [86.8000, 20.1300]
        ]
    ]

    spill_metadata = {
        "incident_id": "SV-IND-2026-BOB-03",
        "detection_timestamp": t_detect.isoformat(),
        "estimated_spill_timestamp": t_spill.isoformat(),
        "estimated_drift_duration_hours": delta_hours,
        "satellite_sensor": "Sentinel-1A C-SAR (Interferometric Wide)",
        "polarization": "VV + VH",
        "spatial_resolution_meters": 10.0,
        "bounding_box": {"min_lon": 86.78, "min_lat": 20.10, "max_lon": 86.86, "max_lat": 20.18},
        "estimated_area_sq_km": 19.30,
        "estimated_volume_bbls": 1150,
        "slick_axis_heading_deg": 46.0,
        "sar_confidence_score": 0.974,
        "polygon_geojson": {"type": "Polygon", "coordinates": slick_coordinates},
        "detected_centroid": {"lon": 86.8210, "lat": 20.1450}
    }

    vessel_b_points = [
        {"time": (t_detect - timedelta(hours=5.0)).isoformat(), "lon": 86.7100, "lat": 20.0100, "sog": 11.5, "cog": 42.0, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=4.5)).isoformat(), "lon": 86.7320, "lat": 20.0350, "sog": 11.4, "cog": 43.0, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=4.2)).isoformat(), "lon": 86.7550, "lat": 20.0600, "sog": 11.6, "cog": 42.0, "status": "Underway using engine", "ais_active": True},
        # 50 min AIS gap near origin 86.7750, 20.0880
        {"time": (t_detect - timedelta(hours=3.0)).isoformat(), "lon": 86.8450, "lat": 20.1600, "sog": 11.8, "cog": 44.0, "status": "Underway using engine", "ais_active": True},
        {"time": (t_detect - timedelta(hours=1.5)).isoformat(), "lon": 86.8900, "lat": 20.2100, "sog": 11.6, "cog": 43.0, "status": "Underway using engine", "ais_active": True},
        {"time": t_detect.isoformat(), "lon": 86.9350, "lat": 20.2600, "sog": 11.5, "cog": 43.0, "status": "Underway using engine", "ais_active": True}
    ]

    vessel_a_points = [
        {"time": (t_detect - timedelta(hours=4.5)).isoformat(), "lon": 86.9500, "lat": 20.2500, "sog": 14.2, "cog": 210.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=3.0)).isoformat(), "lon": 86.9100, "lat": 20.1800, "sog": 14.2, "cog": 210.0, "status": "Underway", "ais_active": True},
        {"time": (t_detect - timedelta(hours=1.5)).isoformat(), "lon": 86.8700, "lat": 20.1100, "sog": 14.1, "cog": 210.0, "status": "Underway", "ais_active": True},
        {"time": t_detect.isoformat(), "lon": 86.8300, "lat": 20.0400, "sog": 14.0, "cog": 210.0, "status": "Underway", "ais_active": True}
    ]

    vessels = [
        {
            "id": "VESSEL-BOB-01",
            "name": "MV BENGAL STAR",
            "imo": 9518844,
            "mmsi": 563009876,
            "flag": "Singapore",
            "type": "Ore-Bulk-Oil Carrier (OBO)",
            "length_m": 260,
            "deadweight_tonnage": 115000,
            "cargo": "Crude Sludge / Oily Bilge",
            "destination": "Paradip Deep Water Port, Odisha",
            "risk_profile": "High Risk - Intentional Bilge Flush",
            "ais_gap_detected": True,
            "gap_duration_minutes": 50,
            "gap_location_approx": [86.7750, 20.0880],
            "track": vessel_b_points
        },
        {
            "id": "VESSEL-BOB-02",
            "name": "MV KALINGA EXPRESS",
            "imo": 9324567,
            "mmsi": 419008899,
            "flag": "India",
            "type": "Coastal Product Carrier",
            "length_m": 145,
            "deadweight_tonnage": 18500,
            "cargo": "Refined Petroleum",
            "destination": "Visakhapatnam Port, AP",
            "risk_profile": "Low Risk - Coastal Transshipment",
            "ais_gap_detected": False,
            "gap_duration_minutes": 0,
            "gap_location_approx": None,
            "track": vessel_a_points
        }
    ]

    return {
        "status": "success",
        "dataset_version": "2.4-mda-sar",
        "scenario_id": "bay_of_bengal",
        "scenario_title": "Bay of Bengal Approaches (Paradip Basin)",
        "region": "Indian EEZ - Bay of Bengal Offshore Odisha",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environmental_vectors": environmental_data,
        "spill_metadata": spill_metadata,
        "vessels": vessels
    }

def get_scenario_dataset(scenario_id: str = "mumbai_high") -> Dict[str, Any]:
    """Returns dataset for the specified scenario."""
    if scenario_id == "gulf_of_kachchh":
        return generate_gulf_of_kachchh_dataset()
    elif scenario_id == "bay_of_bengal":
        return generate_bay_of_bengal_dataset()
    return generate_synthetic_dataset()

if __name__ == "__main__":
    data = generate_synthetic_dataset()
    with open("synthetic_sar_ais_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated synthetic dataset with {len(data['vessels'])} vessels at {data['spill_metadata']['incident_id']}")
