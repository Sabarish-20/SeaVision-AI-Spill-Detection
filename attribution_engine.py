"""
SeaVision AI - Reverse Drift & AIS Anomaly Attribution Engine
Computes oceanographic hindcast reverse-drift trajectory and evaluates multi-parameter
guilt probability scores for maritime vessels using spatial, temporal, and kinematic features.
"""

import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
try:
    from shapely.geometry import Point, LineString, Polygon
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False
    # Lightweight pure-Python geometry proxies for environments without shapely
    class Point:
        def __init__(self, x: float, y: float):
            self.x, self.y = x, y
    class LineString:
        def __init__(self, coords: List[Tuple[float, float]]):
            self.coords = coords
    class Polygon:
        def __init__(self, shell: List[Tuple[float, float]]):
            self.exterior = shell

KM_PER_LAT_DEGREE = 111.139
KNOTS_TO_KMH = 1.852

def haversine_distance_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Computes Great-Circle (geodesic) distance in kilometers between two coordinates.
    """
    r = 6371.0  # Earth's mean radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c

def calculate_drift_vector(
    current_speed_knots: float,
    current_dir_deg: float,
    wind_speed_knots: float,
    wind_dir_deg: float,
    leeway_factor: float = 0.03
) -> Dict[str, float]:
    """
    Decomposes ocean surface current and atmospheric wind leeway into orthogonal
    velocity components (u: Eastward, v: Northward) in knots and km/h.
    """
    rad_c = math.radians(current_dir_deg)
    u_current = current_speed_knots * math.sin(rad_c)
    v_current = current_speed_knots * math.cos(rad_c)

    rad_w = math.radians(wind_dir_deg)
    u_wind = (wind_speed_knots * leeway_factor) * math.sin(rad_w)
    v_wind = (wind_speed_knots * leeway_factor) * math.cos(rad_w)

    u_total_knots = u_current + u_wind
    v_total_knots = v_current + v_wind

    net_speed_knots = math.hypot(u_total_knots, v_total_knots)
    net_speed_kmh = net_speed_knots * KNOTS_TO_KMH
    
    # Net drift direction in nautical degrees (0° = North, 90° = East)
    net_dir_deg = (math.degrees(math.atan2(u_total_knots, v_total_knots)) + 360.0) % 360.0

    return {
        "u_knots": u_total_knots,
        "v_knots": v_total_knots,
        "net_speed_knots": round(net_speed_knots, 3),
        "net_speed_kmh": round(net_speed_kmh, 3),
        "net_dir_deg": round(net_dir_deg, 2)
    }

def calculate_slick_origin(
    detected_centroid: Dict[str, float],
    current_speed_knots: float,
    current_dir_deg: float,
    wind_speed_knots: float,
    wind_dir_deg: float,
    delta_hours: float,
    leeway_factor: float = 0.03,
    steps: int = 10
) -> Dict[str, Any]:
    """
    Hindcasts backwards in time from detection location to estimated discharge origin:
    P_origin = P_detected - (V_current + 0.03 * V_wind) * delta_t
    """
    drift = calculate_drift_vector(
        current_speed_knots=current_speed_knots,
        current_dir_deg=current_dir_deg,
        wind_speed_knots=wind_speed_knots,
        wind_dir_deg=wind_dir_deg,
        leeway_factor=leeway_factor
    )

    det_lon = detected_centroid["lon"]
    det_lat = detected_centroid["lat"]

    # Total distance displaced by drift over delta_hours (in km)
    total_dx_km = drift["u_knots"] * delta_hours * KNOTS_TO_KMH
    total_dy_km = drift["v_knots"] * delta_hours * KNOTS_TO_KMH
    total_drift_distance_km = math.hypot(total_dx_km, total_dy_km)

    # Convert km displacement to latitude/longitude offsets
    mean_lat_rad = math.radians(det_lat)
    km_per_lon_degree = KM_PER_LAT_DEGREE * math.cos(mean_lat_rad)

    delta_lat = total_dy_km / KM_PER_LAT_DEGREE
    delta_lon = total_dx_km / km_per_lon_degree

    # Origin point (subtract displacement to go back in time)
    origin_lat = det_lat - delta_lat
    origin_lon = det_lon - delta_lon

    # Build intermediate backwards drift trajectory line
    trajectory_points = []
    for i in range(steps + 1):
        fraction = i / steps
        t_offset = fraction * delta_hours
        step_dx = drift["u_knots"] * t_offset * KNOTS_TO_KMH
        step_dy = drift["v_knots"] * t_offset * KNOTS_TO_KMH
        
        pt_lat = det_lat - (step_dy / KM_PER_LAT_DEGREE)
        pt_lon = det_lon - (step_dx / km_per_lon_degree)
        
        trajectory_points.append({
            "step": i,
            "hours_before_detection": round(t_offset, 2),
            "lon": round(pt_lon, 5),
            "lat": round(pt_lat, 5)
        })

    return {
        "origin_coordinates": {
            "lon": round(origin_lon, 5),
            "lat": round(origin_lat, 5)
        },
        "total_drift_distance_km": round(total_drift_distance_km, 3),
        "delta_hours": delta_hours,
        "drift_velocity_kmh": drift["net_speed_kmh"],
        "drift_direction_deg": drift["net_dir_deg"],
        "trajectory_path": trajectory_points
    }

def interpolate_vessel_position_at_time(
    track: List[Dict[str, Any]],
    target_time_iso: str
) -> Optional[Dict[str, float]]:
    """
    Interpolates vessel latitude, longitude, and course over ground (COG) at target timestamp.
    """
    target_dt = datetime.fromisoformat(target_time_iso.replace("Z", "+00:00"))
    
    parsed_track = []
    for pt in track:
        dt = datetime.fromisoformat(pt["time"].replace("Z", "+00:00"))
        parsed_track.append((dt, pt))

    parsed_track.sort(key=lambda x: x[0])

    # Check boundaries
    if target_dt <= parsed_track[0][0]:
        return {"lon": parsed_track[0][1]["lon"], "lat": parsed_track[0][1]["lat"], "cog": parsed_track[0][1]["cog"]}
    if target_dt >= parsed_track[-1][0]:
        return {"lon": parsed_track[-1][1]["lon"], "lat": parsed_track[-1][1]["lat"], "cog": parsed_track[-1][1]["cog"]}

    # Linear interpolation between nearest bounding points
    for i in range(len(parsed_track) - 1):
        t1, p1 = parsed_track[i]
        t2, p2 = parsed_track[i + 1]
        if t1 <= target_dt <= t2:
            duration = (t2 - t1).total_seconds()
            if duration == 0:
                return {"lon": p1["lon"], "lat": p1["lat"], "cog": p1["cog"]}
            fraction = (target_dt - t1).total_seconds() / duration
            interp_lon = p1["lon"] + fraction * (p2["lon"] - p1["lon"])
            interp_lat = p1["lat"] + fraction * (p2["lat"] - p1["lat"])
            interp_cog = p1["cog"] + fraction * (p2["cog"] - p1["cog"])
            return {"lon": round(interp_lon, 5), "lat": round(interp_lat, 5), "cog": round(interp_cog, 1)}

    return None

def calculate_guilt_score(
    vessel: Dict[str, Any],
    spill_origin: Dict[str, float],
    spill_time_iso: str,
    slick_axis_heading: float = 58.5
) -> Dict[str, Any]:
    """
    Calculates Guilt_Probability_Score (0 to 100%) using 3 weighted metrics:
    1. Spatial Proximity Score (S_d - 40%): Distance to P_origin at estimated spill time T_spill.
    2. Trajectory Alignment Score (S_t - 30%): Heading alignment relative to slick axis.
    3. AIS Gap Anomaly Score (S_g - 30%): Presence and proximity of AIS blackout gap to spill origin.
    """
    track = vessel.get("track", [])
    if not track:
        return {
            "vessel_id": vessel.get("id"),
            "guilt_probability_score": 0.0,
            "classification": "NO_DATA",
            "scores": {"spatial_proximity": 0, "trajectory_alignment": 0, "ais_gap_anomaly": 0},
            "reason_codes": ["No AIS track history available"]
        }

    # 1. Spatial Proximity Calculation (S_d)
    interp_pos = interpolate_vessel_position_at_time(track, spill_time_iso)
    if interp_pos:
        dist_at_spill_km = haversine_distance_km(
            interp_pos["lon"], interp_pos["lat"],
            spill_origin["lon"], spill_origin["lat"]
        )
    else:
        # Fallback to closest point on track
        min_d = min(
            haversine_distance_km(pt["lon"], pt["lat"], spill_origin["lon"], spill_origin["lat"])
            for pt in track
        )
        dist_at_spill_km = min_d

    # Spatial Proximity Score curve: 100% at <0.8 km, decays smoothly up to 50 km
    if dist_at_spill_km <= 0.8:
        s_d = 100.0
    elif dist_at_spill_km <= 50.0:
        # Smooth exponential decay
        s_d = max(0.0, 100.0 * math.exp(-0.5 * (dist_at_spill_km / 4.8) ** 2))
    else:
        s_d = 0.0

    # 2. Trajectory Alignment Calculation (S_t)
    # Compare vessel course over ground with the slick linear streak axis
    vessel_cog = interp_pos["cog"] if interp_pos else track[0]["cog"]
    heading_diff = abs((vessel_cog - slick_axis_heading + 180.0) % 360.0 - 180.0)
    # Also check reciprocal heading (if ship travelled in reverse parallel corridor)
    reciprocal_diff = abs(((vessel_cog + 180.0) - slick_axis_heading + 180.0) % 360.0 - 180.0)
    effective_angle_diff = min(heading_diff, reciprocal_diff)

    # Alignment score: 100% when collinear (0 deg diff), 0% when perpendicular (90 deg diff)
    s_t = max(0.0, 100.0 * math.cos(math.radians(min(effective_angle_diff, 90.0))))

    # 3. AIS Gap Anomaly Calculation (S_g)
    has_gap = vessel.get("ais_gap_detected", False)
    gap_loc = vessel.get("gap_location_approx")
    gap_duration = vessel.get("gap_duration_minutes", 0)

    s_g = 0.0
    gap_dist_km = 999.0
    if has_gap and gap_loc:
        gap_dist_km = haversine_distance_km(
            gap_loc[0], gap_loc[1],
            spill_origin["lon"], spill_origin["lat"]
        )
        # Check if gap is within 15 km of origin
        if gap_dist_km <= 15.0:
            proximity_factor = max(0.2, (15.0 - gap_dist_km) / 15.0)
            duration_factor = min(1.0, gap_duration / 30.0)  # max weight at >=30 mins
            s_g = min(100.0, 70.0 + 30.0 * proximity_factor * duration_factor)
        else:
            s_g = 25.0
    elif has_gap:
        s_g = 35.0
    else:
        s_g = 5.0  # Clean continuous transponder

    # Composite Weighted Guilt Probability Score
    guilt_score = (0.40 * s_d) + (0.30 * s_t) + (0.30 * s_g)
    guilt_score = round(min(100.0, max(0.0, guilt_score)), 1)

    # Classification & Reasoning
    reason_codes = []
    if dist_at_spill_km < 1.5:
        reason_codes.append(f"Direct spatial intersection with estimated discharge origin ({dist_at_spill_km:.2f} km CPA)")
    elif dist_at_spill_km < 10.0:
        reason_codes.append(f"Close spatial proximity to origin corridor ({dist_at_spill_km:.1f} km)")
    else:
        reason_codes.append(f"Distant transit path ({dist_at_spill_km:.1f} km from spill origin)")

    if effective_angle_diff < 15.0:
        reason_codes.append(f"Trajectory parallel to slick linear axis (Δθ: {effective_angle_diff:.1f}°)")
    elif effective_angle_diff > 60.0:
        reason_codes.append(f"Trajectory perpendicular/divergent from slick axis (Δθ: {effective_angle_diff:.1f}°)")

    if has_gap and gap_dist_km <= 15.0:
        reason_codes.append(f"CRITICAL: AIS transponder disabled for {gap_duration}m within {gap_dist_km:.1f}km of spill origin")
    elif has_gap:
        reason_codes.append(f"Notice: Minor AIS blackout logged ({gap_duration}m) distant from spill site")
    else:
        reason_codes.append("Continuous verified AIS broadcast (No transponder gap)")

    if vessel.get("type", "").lower().startswith("crude") or "tanker" in vessel.get("type", "").lower():
        reason_codes.append("Vessel Type: Bulk Liquid Hydrocarbon Carrier (High Cargo Risk)")

    if guilt_score >= 80.0:
        classification = "HIGH SUSPECT (PRIMARY TARGET)"
        badge_color = "red"
    elif guilt_score >= 45.0:
        classification = "MODERATE SUSPECT"
        badge_color = "amber"
    else:
        classification = "CLEAN / UNCORRELATED"
        badge_color = "emerald"

    return {
        "vessel_id": vessel["id"],
        "vessel_name": vessel["name"],
        "imo": vessel["imo"],
        "mmsi": vessel["mmsi"],
        "flag": vessel["flag"],
        "type": vessel["type"],
        "dwt": vessel["deadweight_tonnage"],
        "guilt_probability_score": guilt_score,
        "classification": classification,
        "badge_color": badge_color,
        "metrics": {
            "spatial_proximity_score": round(s_d, 1),
            "distance_at_spill_km": round(dist_at_spill_km, 2),
            "trajectory_alignment_score": round(s_t, 1),
            "heading_deviation_deg": round(effective_angle_diff, 1),
            "ais_gap_anomaly_score": round(s_g, 1),
            "ais_gap_detected": has_gap,
            "gap_distance_to_origin_km": round(gap_dist_km, 2) if gap_dist_km != 999.0 else None,
            "gap_duration_minutes": gap_duration
        },
        "interpolated_position_at_spill": interp_pos,
        "reason_codes": reason_codes,
        "track": vessel["track"]
    }

def run_full_attribution(
    dataset: Dict[str, Any],
    custom_env: Optional[Dict[str, Any]] = None,
    custom_delta_hours: Optional[float] = None
) -> Dict[str, Any]:
    """
    Orchestrates end-to-end attribution analysis:
    1. Extracts environmental conditions & spill geometry.
    2. Calculates reverse hindcast drift line and origin point.
    3. Evaluates all vessels within range and returns sorted ranking.
    """
    env = custom_env or dataset["environmental_vectors"]
    spill_meta = dataset["spill_metadata"]
    
    current_speed = env["current"]["speed_knots"]
    current_dir = env["current"]["direction_deg"]
    wind_speed = env["wind"]["speed_knots"]
    wind_dir = env["wind"]["direction_deg"]
    leeway = env["wind"].get("leeway_factor", 0.03)
    
    delta_hours = custom_delta_hours if custom_delta_hours is not None else spill_meta["estimated_drift_duration_hours"]

    # 1. Reverse Drift Hindcast
    drift_result = calculate_slick_origin(
        detected_centroid=spill_meta["detected_centroid"],
        current_speed_knots=current_speed,
        current_dir_deg=current_dir,
        wind_speed_knots=wind_speed,
        wind_dir_deg=wind_dir,
        delta_hours=delta_hours,
        leeway_factor=leeway
    )

    origin_coord = drift_result["origin_coordinates"]
    spill_time = spill_meta["estimated_spill_timestamp"]
    slick_axis = spill_meta.get("slick_axis_heading_deg", 58.5)

    # 2. Correlate with each AIS track
    ranked_vessels = []
    for vessel in dataset["vessels"]:
        score_data = calculate_guilt_score(
            vessel=vessel,
            spill_origin=origin_coord,
            spill_time_iso=spill_time,
            slick_axis_heading=slick_axis
        )
        ranked_vessels.append(score_data)

    # Sort descending by guilt probability
    ranked_vessels.sort(key=lambda x: x["guilt_probability_score"], reverse=True)

    return {
        "incident_id": spill_meta["incident_id"],
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "spill_detected_centroid": spill_meta["detected_centroid"],
        "spill_polygon": spill_meta["polygon_geojson"],
        "drift_origin": origin_coord,
        "drift_analysis": drift_result,
        "environmental_vectors": env,
        "vessels_evaluated_count": len(ranked_vessels),
        "primary_suspect": ranked_vessels[0] if ranked_vessels else None,
        "ranked_vessels": ranked_vessels
    }

if __name__ == "__main__":
    from synthetic_data_generator import generate_synthetic_dataset
    dataset = generate_synthetic_dataset()
    results = run_full_attribution(dataset)
    print("=== SEAVISION ATTRIBUTION RESULTS ===")
    print(f"Incident: {results['incident_id']}")
    print(f"Drift Origin: {results['drift_origin']}")
    print("\nVessel Rankings:")
    for v in results["ranked_vessels"]:
        print(f"- {v['vessel_name']} ({v['type']}): {v['guilt_probability_score']}% [{v['classification']}]")
