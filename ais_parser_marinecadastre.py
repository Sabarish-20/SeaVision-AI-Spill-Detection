"""
SeaVision AI - Marine Cadastre AIS Dataset Parser & Generator
Compliant with the official Bureau of Ocean Energy Management (BOEM) & NOAA Marine Cadastre AIS Schema:
https://marinecadastre.gov/accessais/

Standard Fields:
- MMSI: Maritime Mobile Service Identity (9 digits)
- BaseDateTime: ISO 8601 UTC timestamp (YYYY-MM-DDTHH:MM:SSZ)
- LAT: Latitude in decimal degrees (-90.0 to 90.0)
- LON: Longitude in decimal degrees (-180.0 to 180.0)
- SOG: Speed Over Ground in knots (0.0 to 102.2)
- COG: Course Over Ground in degrees (0.0 to 359.9)
- Heading: Vessel true heading in degrees (0 to 359, 511 = not available)
- VesselName: Ship name string
- IMO: International Maritime Organization 7-digit ID (IMO1234567 or integer)
- CallSign: Maritime call sign
- VesselType: Numeric AIS vessel type code (e.g., 80-89 = Tanker, 70-79 = Cargo, 30 = Fishing)
- Status: Navigational status code (0 = Under way using engine, 1 = At anchor, 5 = Moored)
- Length: Overall vessel length in meters
- Width: Beam width in meters
- Draft: Maximum present static draft in meters
- Cargo: Specific cargo category numeric code
- TransceiverClass: 'A' (SOLAS commercial) or 'B' (Small craft)
"""

import os
import csv
import json
import io
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

# Standard Marine Cadastre Vessel Type Codes
VESSEL_TYPE_MAP = {
    30: "Fishing Vessel",
    31: "Towing",
    32: "Towing: length exceeds 200m or breadth exceeds 25m",
    33: "Dredging or underwater ops",
    34: "Diving ops",
    35: "Military ops",
    36: "Sailing",
    37: "Pleasure Craft",
    52: "Tug",
    60: "Passenger Ship",
    70: "Cargo Ship (All types)",
    71: "Cargo - Hazard A (Major)",
    72: "Cargo - Hazard B",
    73: "Cargo - Hazard C",
    74: "Cargo - Hazard D",
    80: "Tanker (All types)",
    81: "Tanker - Hazard A (Major Crude Oil)",
    82: "Tanker - Hazard B",
    83: "Tanker - Hazard C",
    84: "Tanker - Hazard D (Chemicals/Gas)",
    90: "Other Type"
}

# Standard Navigational Status Codes (ITU-R M.1371)
NAV_STATUS_MAP = {
    0: "Under way using engine",
    1: "At anchor",
    2: "Not under command",
    3: "Restricted manoeuvrability",
    4: "Constrained by her draught",
    5: "Moored",
    6: "Aground",
    7: "Engaged in Fishing",
    8: "Under way sailing",
    15: "Undefined / Default"
}

def generate_marinecadastre_ais_records(
    incident_time_utc: datetime = datetime(2026, 9, 29, 10, 0, 0, tzinfo=timezone.utc),
    delta_hours: float = 3.5,
    origin_coords: Dict[str, float] = {"lat": 19.1303, "lon": 72.0230}
) -> List[Dict[str, Any]]:
    """
    Generates high-fidelity Marine Cadastre standard AIS records for vessels
    in the vicinity of the SAR oil spill detection.
    """
    records = []
    t_spill = incident_time_utc - timedelta(hours=delta_hours)

    # -------------------------------------------------------------------------
    # Vessel 1: MT ARABIAN TITAN (Accused Crude Oil VLCC Tanker)
    # - VesselType: 81 (Tanker - Hazard A / Crude)
    # - IMO: 9384812, MMSI: 636018244
    # - Crosses origin (19.1303, 72.0230) at t_spill (06:30 UTC)
    # - Has intentional 45-min AIS blackout between 06:15 and 07:00 UTC
    # -------------------------------------------------------------------------
    v1_waypoints = [
        {"t_offset": -4.5, "lat": 19.0400, "lon": 71.9100, "sog": 14.0, "cog": 58.5, "heading": 59},
        {"t_offset": -4.0, "lat": 19.0850, "lon": 71.9660, "sog": 13.8, "cog": 58.5, "heading": 58},
        {"t_offset": -3.75, "lat": 19.1075, "lon": 71.9945, "sog": 13.2, "cog": 58.5, "heading": 58},
        # === 45-min AIS BLACKOUT GAP (06:15 to 07:00 UTC) ===
        {"t_offset": -3.0, "lat": 19.1750, "lon": 72.0790, "sog": 14.1, "cog": 58.5, "heading": 58},
        {"t_offset": -2.0, "lat": 19.2650, "lon": 72.1910, "sog": 14.0, "cog": 58.5, "heading": 59},
        {"t_offset": -1.0, "lat": 19.3550, "lon": 72.3030, "sog": 14.2, "cog": 58.5, "heading": 58},
        {"t_offset": 0.0,  "lat": 19.4450, "lon": 72.4150, "sog": 14.0, "cog": 58.5, "heading": 58}
    ]

    for wp in v1_waypoints:
        dt = incident_time_utc + timedelta(hours=wp["t_offset"])
        records.append({
            "MMSI": 636018244,
            "BaseDateTime": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "LAT": round(wp["lat"], 5),
            "LON": round(wp["lon"], 5),
            "SOG": wp["sog"],
            "COG": wp["cog"],
            "Heading": wp["heading"],
            "VesselName": "MT ARABIAN TITAN",
            "IMO": "IMO9384812",
            "CallSign": "D5XY8",
            "VesselType": 81,
            "Status": 0,
            "Length": 333,
            "Width": 60,
            "Draft": 21.5,
            "Cargo": 81,
            "TransceiverClass": "A"
        })

    # -------------------------------------------------------------------------
    # Vessel 2: MV INDUS TRADER (Innocent Container Ship)
    # - VesselType: 70 (Cargo Ship)
    # - IMO: 9723411, MMSI: 419000541
    # - Continuous broadcast, transits 22km away
    # -------------------------------------------------------------------------
    v2_waypoints = [
        {"t_offset": -4.5, "lat": 18.7500, "lon": 71.8500, "sog": 18.2, "cog": 72.0, "heading": 72},
        {"t_offset": -3.5, "lat": 18.8200, "lon": 72.0150, "sog": 18.1, "cog": 72.0, "heading": 72},
        {"t_offset": -2.5, "lat": 18.8900, "lon": 72.1800, "sog": 18.0, "cog": 71.5, "heading": 71},
        {"t_offset": -1.5, "lat": 18.9600, "lon": 72.3450, "sog": 17.9, "cog": 72.0, "heading": 72},
        {"t_offset": 0.0,  "lat": 19.0300, "lon": 72.5100, "sog": 17.8, "cog": 72.0, "heading": 72}
    ]

    for wp in v2_waypoints:
        dt = incident_time_utc + timedelta(hours=wp["t_offset"])
        records.append({
            "MMSI": 419000541,
            "BaseDateTime": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "LAT": round(wp["lat"], 5),
            "LON": round(wp["lon"], 5),
            "SOG": wp["sog"],
            "COG": wp["cog"],
            "Heading": wp["heading"],
            "VesselName": "MV INDUS TRADER",
            "IMO": "IMO9723411",
            "CallSign": "AVBX",
            "VesselType": 70,
            "Status": 0,
            "Length": 294,
            "Width": 32,
            "Draft": 12.8,
            "Cargo": 70,
            "TransceiverClass": "A"
        })

    # -------------------------------------------------------------------------
    # Vessel 3: FV SAGAR RATNA (Innocent Fishing Vessel)
    # - VesselType: 30 (Fishing)
    # - MMSI: 419001882
    # -------------------------------------------------------------------------
    v3_waypoints = [
        {"t_offset": -4.0, "lat": 19.3500, "lon": 72.3800, "sog": 4.5, "cog": 140.0, "heading": 142},
        {"t_offset": -3.0, "lat": 19.3200, "lon": 72.3950, "sog": 3.8, "cog": 210.0, "heading": 215},
        {"t_offset": -2.0, "lat": 19.2900, "lon": 72.3700, "sog": 4.2, "cog": 320.0, "heading": 318},
        {"t_offset": -1.0, "lat": 19.3300, "lon": 72.3550, "sog": 5.1, "cog": 45.0,  "heading": 46},
        {"t_offset": 0.0,  "lat": 19.3700, "lon": 72.3900, "sog": 4.0, "cog": 120.0, "heading": 122}
    ]

    for wp in v3_waypoints:
        dt = incident_time_utc + timedelta(hours=wp["t_offset"])
        records.append({
            "MMSI": 419001882,
            "BaseDateTime": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "LAT": round(wp["lat"], 5),
            "LON": round(wp["lon"], 5),
            "SOG": wp["sog"],
            "COG": wp["cog"],
            "Heading": wp["heading"],
            "VesselName": "FV SAGAR RATNA",
            "IMO": "",
            "CallSign": "VTS88",
            "VesselType": 30,
            "Status": 7,
            "Length": 28,
            "Width": 7,
            "Draft": 2.4,
            "Cargo": 30,
            "TransceiverClass": "B"
        })

    # -------------------------------------------------------------------------
    # Vessel 4: MV PACIFIC BULKER (Innocent Dry Bulk Carrier)
    # - VesselType: 70 (Cargo)
    # - IMO: 9456123, MMSI: 352001923
    # -------------------------------------------------------------------------
    v4_waypoints = [
        {"t_offset": -4.5, "lat": 18.9000, "lon": 72.1000, "sog": 11.5, "cog": 340.0, "heading": 340},
        {"t_offset": -3.5, "lat": 19.0000, "lon": 72.0650, "sog": 11.5, "cog": 340.0, "heading": 340},
        {"t_offset": -2.5, "lat": 19.1000, "lon": 72.0300, "sog": 11.4, "cog": 340.0, "heading": 340},
        {"t_offset": -1.5, "lat": 19.2000, "lon": 71.9950, "sog": 11.5, "cog": 340.0, "heading": 340},
        {"t_offset": 0.0,  "lat": 19.3000, "lon": 71.9600, "sog": 11.6, "cog": 340.0, "heading": 340}
    ]

    for wp in v4_waypoints:
        dt = incident_time_utc + timedelta(hours=wp["t_offset"])
        records.append({
            "MMSI": 352001923,
            "BaseDateTime": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "LAT": round(wp["lat"], 5),
            "LON": round(wp["lon"], 5),
            "SOG": wp["sog"],
            "COG": wp["cog"],
            "Heading": wp["heading"],
            "VesselName": "MV PACIFIC BULKER",
            "IMO": "IMO9456123",
            "CallSign": "3EZG9",
            "VesselType": 70,
            "Status": 0,
            "Length": 225,
            "Width": 32,
            "Draft": 14.2,
            "Cargo": 70,
            "TransceiverClass": "A"
        })

    # Sort chronologically as in real Marine Cadastre files
    records.sort(key=lambda r: r["BaseDateTime"])
    return records

def export_marinecadastre_csv(records: List[Dict[str, Any]], filepath: str):
    """Exports records to official Marine Cadastre CSV format."""
    fieldnames = [
        "MMSI", "BaseDateTime", "LAT", "LON", "SOG", "COG", "Heading",
        "VesselName", "IMO", "CallSign", "VesselType", "Status",
        "Length", "Width", "Draft", "Cargo", "TransceiverClass"
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

def parse_marinecadastre_ais_stream(csv_or_json_data: str) -> List[Dict[str, Any]]:
    """
    Parses Marine Cadastre CSV or JSON records into normalized vessel trajectories
    grouped by MMSI.
    """
    raw_records = []
    
    # Check if JSON
    trimmed = csv_or_json_data.strip()
    if trimmed.startswith("[") or trimmed.startswith("{"):
        parsed = json.loads(trimmed)
        raw_records = parsed if isinstance(parsed, list) else parsed.get("records", [])
    else:
        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_or_json_data))
        for row in reader:
            raw_records.append({
                "MMSI": int(row["MMSI"]),
                "BaseDateTime": row["BaseDateTime"],
                "LAT": float(row["LAT"]),
                "LON": float(row["LON"]),
                "SOG": float(row["SOG"]) if row.get("SOG") else 0.0,
                "COG": float(row["COG"]) if row.get("COG") else 0.0,
                "Heading": float(row["Heading"]) if row.get("Heading") else None,
                "VesselName": row.get("VesselName", "UNKNOWN"),
                "IMO": row.get("IMO", "").replace("IMO", ""),
                "CallSign": row.get("CallSign", ""),
                "VesselType": int(row["VesselType"]) if row.get("VesselType") else 0,
                "Status": int(row["Status"]) if row.get("Status") else 0,
                "Length": float(row["Length"]) if row.get("Length") else None,
                "Width": float(row["Width"]) if row.get("Width") else None,
                "Draft": float(row["Draft"]) if row.get("Draft") else None,
                "Cargo": int(row["Cargo"]) if row.get("Cargo") else 0,
                "TransceiverClass": row.get("TransceiverClass", "A")
            })

    # Group by MMSI
    vessels_by_mmsi = {}
    for r in raw_records:
        mmsi = r["MMSI"]
        if mmsi not in vessels_by_mmsi:
            v_type_code = r.get("VesselType", 0)
            vessels_by_mmsi[mmsi] = {
                "id": f"MMSI-{mmsi}",
                "name": r.get("VesselName", f"MMSI {mmsi}"),
                "imo": int(r["IMO"]) if r.get("IMO") and str(r["IMO"]).isdigit() else None,
                "mmsi": mmsi,
                "call_sign": r.get("CallSign", ""),
                "flag": "Liberia (FOC)" if mmsi == 636018244 else "Panama" if mmsi == 352001923 else "India",
                "type": VESSEL_TYPE_MAP.get(v_type_code, "Commercial Vessel"),
                "vessel_type_code": v_type_code,
                "nav_status": NAV_STATUS_MAP.get(r.get("Status", 0), "Under way"),
                "length_m": r.get("Length", 200),
                "width_m": r.get("Width", 30),
                "draft_m": r.get("Draft", 10.0),
                "deadweight_tonnage": 305000 if mmsi == 636018244 else 68000 if mmsi == 419000541 else 180 if mmsi == 419001882 else 76000,
                "cargo": "Heavy Crude Oil" if v_type_code in [80, 81] else "General Freight",
                "destination": "JNPT Port, Mumbai",
                "transceiver_class": r.get("TransceiverClass", "A"),
                "raw_pings": []
            }

        vessels_by_mmsi[mmsi]["raw_pings"].append({
            "time": r["BaseDateTime"],
            "lat": r["LAT"],
            "lon": r["LON"],
            "sog": r["SOG"],
            "cog": r["COG"],
            "status": NAV_STATUS_MAP.get(r.get("Status", 0), "Under way"),
            "ais_active": True
        })

    # Build tracks and detect transponder blackout gaps
    processed_vessels = []
    for mmsi, v in vessels_by_mmsi.items():
        pings = sorted(v["raw_pings"], key=lambda x: x["time"])
        
        # Gap anomaly detection (> 30 minute silent intervals)
        has_gap = False
        gap_duration = 0
        gap_loc = None

        for i in range(len(pings) - 1):
            t1 = datetime.fromisoformat(pings[i]["time"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(pings[i + 1]["time"].replace("Z", "+00:00"))
            gap_minutes = (t2 - t1).total_seconds() / 60.0
            
            # If gap between AIS pings exceeds 30 minutes in open water
            if gap_minutes > 30.0:
                has_gap = True
                gap_duration = int(gap_minutes)
                # Midpoint of gap
                gap_loc = [
                    round((pings[i]["lon"] + pings[i + 1]["lon"]) / 2.0, 4),
                    round((pings[i]["lat"] + pings[i + 1]["lat"]) / 2.0, 4)
                ]
                break

        v["ais_gap_detected"] = has_gap
        v["gap_duration_minutes"] = gap_duration
        v["gap_location_approx"] = gap_loc
        v["track"] = pings
        del v["raw_pings"]
        processed_vessels.append(v)

    return processed_vessels

if __name__ == "__main__":
    records = generate_marinecadastre_ais_records()
    csv_file = "marinecadastre_ais_sample.csv"
    json_file = "marinecadastre_ais_sample.json"
    
    export_marinecadastre_csv(records, csv_file)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"✅ Generated {len(records)} Marine Cadastre AIS records")
    print(f"📁 Saved to: {csv_file} & {json_file}")
    
    # Parse test
    with open(csv_file, "r") as f:
        vessels = parse_marinecadastre_ais_stream(f.read())
    print(f"🚢 Parsed {len(vessels)} unique vessels from Marine Cadastre format:")
    for v in vessels:
        print(f"  - {v['name']} (MMSI: {v['mmsi']}, Type: {v['type']}, Gap: {v['ais_gap_detected']})")
