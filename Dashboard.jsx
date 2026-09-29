import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  AlertTriangle,
  Shield,
  Compass,
  Wind,
  Waves,
  Satellite,
  Navigation,
  FileText,
  Sliders,
  Play,
  Pause,
  RotateCcw,
  Eye,
  CheckCircle2,
  XCircle,
  Clock,
  Radio,
  ExternalLink,
  ChevronRight,
  Download,
  Crosshair,
  Printer
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

/**
 * Tactical Maritime Domain Awareness (MDA) Command Center
 * SeaVision AI: SAR Oil Spill Detection & Reverse-Drift AIS Vessel Attribution
 */

// --- Default Synthetic Incident Data ---
const DEFAULT_INCIDENT = {
  incident_id: "SV-IND-2026-0929-01",
  satellite_sensor: "Sentinel-1C C-SAR (IW Mode)",
  detection_time: "2026-09-29T10:00:00Z",
  estimated_spill_time: "2026-09-29T06:30:00Z",
  delta_hours: 3.5,
  area_sq_km: 14.82,
  volume_bbls: 850,
  confidence: 96.2,
  slick_heading: 58.5,
  detected_centroid: { lat: 19.1820, lon: 72.1150 },
  spill_polygon: [
    [19.1710, 72.1020],
    [19.1765, 72.1105],
    [19.1860, 72.1220],
    [19.1915, 72.1280],
    [19.1940, 72.1250],
    [19.1870, 72.1140],
    [19.1790, 72.1060],
    [19.1730, 72.0980],
    [19.1710, 72.1020]
  ]
};

const DEFAULT_ENV = {
  current_speed: 1.25, // knots
  current_dir: 55.0,   // degrees towards
  wind_speed: 16.5,    // knots
  wind_dir: 70.0,      // degrees towards
  leeway_factor: 0.03
};

const DEFAULT_VESSELS = [
  {
    id: "VESSEL-002",
    name: "MT ARABIAN TITAN",
    imo: 9384812,
    mmsi: 636018244,
    flag: "Liberia (FOC)",
    type: "Crude Oil Tanker (VLCC)",
    dwt: 305000,
    cargo: "Heavy Crude Oil (Iranian Light Blend)",
    destination: "JNPT Port, Mumbai",
    risk_level: "High Risk - Previous MARPOL Violations",
    ais_gap: {
      detected: true,
      duration_mins: 45,
      location: { lat: 19.1300, lon: 72.0230 },
      start_time: "06:15 UTC",
      end_time: "07:00 UTC"
    },
    track: [
      { t: 0.0, lat: 19.0400, lon: 71.9100, cog: 58.5, sog: 14.0, time: "05:30 UTC" },
      { t: 0.5, lat: 19.0850, lon: 71.9660, cog: 58.5, sog: 13.8, time: "06:00 UTC" },
      { t: 0.75, lat: 19.1075, lon: 71.9945, cog: 58.5, sog: 13.2, time: "06:15 UTC" },
      // Hidden gap transiting through (19.1300, 72.0230) at t=1.0 (06:30 UTC)
      { t: 1.5, lat: 19.1750, lon: 72.0790, cog: 58.5, sog: 14.1, time: "07:00 UTC" },
      { t: 2.5, lat: 19.2650, lon: 72.1910, cog: 58.5, sog: 14.0, time: "08:00 UTC" },
      { t: 3.5, lat: 19.3550, lon: 72.3030, cog: 58.5, sog: 14.2, time: "09:00 UTC" },
      { t: 4.5, lat: 19.4450, lon: 72.4150, cog: 58.5, sog: 14.0, time: "10:00 UTC" }
    ]
  },
  {
    id: "VESSEL-001",
    name: "MV INDUS TRADER",
    imo: 9723411,
    mmsi: 419000541,
    flag: "India",
    type: "Container Ship (Post-Panamax)",
    dwt: 68000,
    cargo: "General Containerized Freight",
    destination: "Pipavav Port, Gujarat",
    risk_level: "Low Risk - Fully Compliant",
    ais_gap: { detected: false },
    track: [
      { t: 0.0, lat: 18.7500, lon: 71.8500, cog: 72.0, sog: 18.2, time: "05:30 UTC" },
      { t: 1.0, lat: 18.8200, lon: 72.0150, cog: 72.0, sog: 18.1, time: "06:30 UTC" },
      { t: 2.0, lat: 18.8900, lon: 72.1800, cog: 71.5, sog: 18.0, time: "07:30 UTC" },
      { t: 3.0, lat: 18.9600, lon: 72.3450, cog: 72.0, sog: 17.9, time: "08:30 UTC" },
      { t: 4.5, lat: 19.0300, lon: 72.5100, cog: 72.0, sog: 17.8, time: "10:00 UTC" }
    ]
  },
  {
    id: "VESSEL-003",
    name: "FV SAGAR RATNA",
    imo: null,
    mmsi: 419001882,
    flag: "India",
    type: "Mechanized Fishing Trawler",
    dwt: 180,
    cargo: "Fresh Fish Catch",
    destination: "Sassoon Docks, Mumbai",
    risk_level: "Low Risk - Artisanal Craft",
    ais_gap: { detected: false },
    track: [
      { t: 0.5, lat: 19.3500, lon: 72.3800, cog: 140.0, sog: 4.5, time: "06:00 UTC" },
      { t: 1.5, lat: 19.3200, lon: 72.3950, cog: 210.0, sog: 3.8, time: "07:00 UTC" },
      { t: 2.5, lat: 19.2900, lon: 72.3700, cog: 320.0, sog: 4.2, time: "08:00 UTC" },
      { t: 3.5, lat: 19.3300, lon: 72.3550, cog: 45.0, sog: 5.1, time: "09:00 UTC" },
      { t: 4.5, lat: 19.3700, lon: 72.3900, cog: 120.0, sog: 4.0, time: "10:00 UTC" }
    ]
  },
  {
    id: "VESSEL-004",
    name: "MV PACIFIC BULKER",
    imo: 9456123,
    mmsi: 352001923,
    flag: "Panama",
    type: "Dry Bulk Carrier",
    dwt: 76000,
    cargo: "Iron Ore Pellets",
    destination: "Mormugao Port, Goa",
    risk_level: "Low Risk - Regular Route",
    ais_gap: { detected: false },
    track: [
      { t: 0.0, lat: 18.9000, lon: 72.1000, cog: 340.0, sog: 11.5, time: "05:30 UTC" },
      { t: 1.0, lat: 19.0000, lon: 72.0650, cog: 340.0, sog: 11.5, time: "06:30 UTC" },
      { t: 2.0, lat: 19.1000, lon: 72.0300, cog: 340.0, sog: 11.4, time: "07:30 UTC" },
      { t: 3.0, lat: 19.2000, lon: 71.9950, cog: 340.0, sog: 11.5, time: "08:30 UTC" },
      { t: 4.5, lat: 19.3000, lon: 71.9600, cog: 340.0, sog: 11.6, time: "10:00 UTC" }
    ]
  }
];

// --- Helper Functions for Ocean Drift Vector Math & Geodesics ---
function calculateDrift(detectedLat, detectedLon, curSpd, curDir, wSpd, wDir, deltaH, leeway = 0.03) {
  const radC = (curDir * Math.PI) / 180;
  const uC = curSpd * Math.sin(radC);
  const vC = curSpd * Math.cos(radC);

  const radW = (wDir * Math.PI) / 180;
  const uW = wSpd * leeway * Math.sin(radW);
  const vW = wSpd * leeway * Math.cos(radW);

  const uTotal = uC + uW;
  const vTotal = vC + vW;

  const netSpeedKmh = Math.hypot(uTotal, vTotal) * 1.852;
  const netDirDeg = ((Math.atan2(uTotal, vTotal) * 180) / Math.PI + 360) % 360;

  const totalDxKm = uTotal * deltaH * 1.852;
  const totalDyKm = vTotal * deltaH * 1.852;
  const totalDistKm = Math.hypot(totalDxKm, totalDyKm);

  const meanLatRad = (detectedLat * Math.PI) / 180;
  const kmPerLat = 111.139;
  const kmPerLon = 111.139 * Math.cos(meanLatRad);

  const originLat = detectedLat - totalDyKm / kmPerLat;
  const originLon = detectedLon - totalDxKm / kmPerLon;

  const steps = 10;
  const path = [];
  for (let i = 0; i <= steps; i++) {
    const fraction = i / steps;
    const tOffset = fraction * deltaH;
    const stepDx = uTotal * tOffset * 1.852;
    const stepDy = vTotal * tOffset * 1.852;
    path.push({
      step: i,
      hoursBefore: tOffset,
      lat: detectedLat - stepDy / kmPerLat,
      lon: detectedLon - stepDx / kmPerLon
    });
  }

  return {
    origin: { lat: originLat, lon: originLon },
    totalDistKm,
    netSpeedKmh,
    netDirDeg,
    path
  };
}

function haversineDist(lat1, lon1, lat2, lon2) {
  const R = 6371.0;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export default function SeaVisionDashboard() {
  // Environmental & Simulation state
  const [currentSpeed, setCurrentSpeed] = useState(DEFAULT_ENV.current_speed);
  const [currentDir, setCurrentDir] = useState(DEFAULT_ENV.current_dir);
  const [windSpeed, setWindSpeed] = useState(DEFAULT_ENV.wind_speed);
  const [windDir, setWindDir] = useState(DEFAULT_ENV.wind_dir);
  const [deltaHours, setDeltaHours] = useState(DEFAULT_INCIDENT.delta_hours);

  // Time scrubber state (0 = T_spill / 4.5h ago, 4.5 = T_detect / Now)
  const [timelineScrub, setTimelineScrub] = useState(4.5);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedVessel, setSelectedVessel] = useState(DEFAULT_VESSELS[0]);
  const [showReportModal, setShowReportModal] = useState(false);
  const [activeTab, setActiveTab] = useState('map'); // 'map' | 'analytics' | 'dossier'

  // Dynamic Hindcast Calculation
  const driftResult = useMemo(() => {
    return calculateDrift(
      DEFAULT_INCIDENT.detected_centroid.lat,
      DEFAULT_INCIDENT.detected_centroid.lon,
      currentSpeed,
      currentDir,
      windSpeed,
      windDir,
      deltaHours
    );
  }, [currentSpeed, currentDir, windSpeed, windDir, deltaHours]);

  // Dynamic Vessel Guilt Probability Scoring
  const rankedVessels = useMemo(() => {
    const origin = driftResult.origin;
    const slickAxis = DEFAULT_INCIDENT.slick_heading;

    return DEFAULT_VESSELS.map((v) => {
      // Find interpolated position at T_spill (1.0h into timeline or 3.5h before detection)
      const targetT = 4.5 - deltaHours;
      let pos = v.track[0];
      for (let i = 0; i < v.track.length - 1; i++) {
        if (v.track[i].t <= targetT && targetT <= v.track[i + 1].t) {
          const frac = (targetT - v.track[i].t) / (v.track[i + 1].t - v.track[i].t);
          pos = {
            lat: v.track[i].lat + frac * (v.track[i + 1].lat - v.track[i].lat),
            lon: v.track[i].lon + frac * (v.track[i + 1].lon - v.track[i].lon),
            cog: v.track[i].cog,
            sog: v.track[i].sog
          };
          break;
        }
      }

      const distAtSpill = haversineDist(pos.lat, pos.lon, origin.lat, origin.lon);

      // S_d: Spatial Proximity (40%)
      let s_d = 0;
      if (distAtSpill <= 0.8) s_d = 100;
      else if (distAtSpill <= 50) s_d = Math.max(0, 100 * Math.exp(-0.5 * (distAtSpill / 4.8) ** 2));

      // S_t: Trajectory Alignment (30%)
      const headingDiff = Math.abs(((pos.cog - slickAxis + 180) % 360) - 180);
      const reciprocalDiff = Math.abs(((pos.cog + 180 - slickAxis + 180) % 360) - 180);
      const effDiff = Math.min(headingDiff, reciprocalDiff);
      const s_t = Math.max(0, 100 * Math.cos((Math.min(effDiff, 90) * Math.PI) / 180));

      // S_g: AIS Gap Anomaly (30%)
      let s_g = 5.0;
      let gapDist = 999;
      if (v.ais_gap.detected && v.ais_gap.location) {
        gapDist = haversineDist(
          v.ais_gap.location.lat,
          v.ais_gap.location.lon,
          origin.lat,
          origin.lon
        );
        if (gapDist <= 15.0) {
          const prox = Math.max(0.2, (15 - gapDist) / 15);
          s_g = Math.min(100, 70 + 30 * prox);
        } else {
          s_g = 30.0;
        }
      }

      const totalScore = Math.min(100, Math.max(0, 0.4 * s_d + 0.3 * s_t + 0.3 * s_g));
      const roundedScore = Math.round(totalScore * 10) / 10;

      let classification = "CLEAN / UNCORRELATED";
      let badgeColor = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
      if (roundedScore >= 80) {
        classification = "HIGH SUSPECT (PRIMARY TARGET)";
        badgeColor = "bg-red-500/20 text-red-400 border-red-500/40";
      } else if (roundedScore >= 45) {
        classification = "MODERATE SUSPECT";
        badgeColor = "bg-amber-500/20 text-amber-400 border-amber-500/40";
      }

      const reasons = [];
      if (distAtSpill < 1.5) reasons.push(`Direct intersection with origin (${distAtSpill.toFixed(2)} km CPA)`);
      else if (distAtSpill < 10) reasons.push(`Close proximity to spill corridor (${distAtSpill.toFixed(1)} km)`);
      else reasons.push(`Distant transit (${distAtSpill.toFixed(1)} km away)`);

      if (effDiff < 15) reasons.push(`Course aligned with slick axis (Δθ: ${effDiff.toFixed(1)}°)`);
      if (v.ais_gap.detected && gapDist <= 15) reasons.push(`Intentional AIS transponder blackout for ${v.ais_gap.duration_mins}m at origin`);
      if (v.type.includes("Tanker")) reasons.push("Carrying bulk crude cargo (MARPOL Annex I profile)");

      return {
        ...v,
        guilt_score: roundedScore,
        classification,
        badgeColor,
        reasons,
        metrics: {
          s_d: Math.round(s_d),
          s_t: Math.round(s_t),
          s_g: Math.round(s_g),
          distAtSpill: Math.round(distAtSpill * 10) / 10,
          headingDiff: Math.round(effDiff * 10) / 10,
          gapDist: gapDist < 900 ? Math.round(gapDist * 10) / 10 : null
        }
      };
    }).sort((a, b) => b.guilt_score - a.guilt_score);
  }, [driftResult, deltaHours]);

  // Playback timer for historical scrubbing
  useEffect(() => {
    let interval = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimelineScrub((prev) => {
          if (prev >= 4.5) return 0;
          return Math.round((prev + 0.25) * 100) / 100;
        });
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  // Dynamic Leaflet Map setup via DOM container
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Load Leaflet CSS dynamically if not present
    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css';
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }

    const initMap = () => {
      if (!window.L || !mapContainerRef.current) return;
      if (mapInstanceRef.current) return;

      const map = window.L.map(mapContainerRef.current, {
        center: [19.16, 72.10],
        zoom: 11,
        zoomControl: false,
        attributionControl: false
      });

      // 1. ISRO Bhuvan High-Resolution Satellite & Open Geospatial Base (Zero Commercial Key)
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: 'Tactical Base &copy; OpenStreetMap &amp; ISRO Bhuvan / MOSDAC'
      }).addTo(map);

      // 2. ISRO Bhuvan Satellite WMS Layer
      const bhuvanLayer = window.L.tileLayer.wms('https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms', {
        layers: 'india3',
        format: 'image/png',
        transparent: false,
        version: '1.1.1',
        attribution: 'Satellite Imagery &copy; ISRO, NRSC, Bhuvan'
      });

      const baseLayers = {
        "Tactical Nautical Chart": map,
        "ISRO Bhuvan Satellite": bhuvanLayer
      };
      window.L.control.layers(baseLayers, null, { position: 'topright' }).addTo(map);

      window.L.control.zoom({ position: 'bottomright' }).addTo(map);

      mapInstanceRef.current = map;
      layerGroupRef.current = window.L.layerGroup().addTo(map);
    };

    if (window.L) {
      initMap();
    } else {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.onload = initMap;
      document.head.appendChild(script);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update Map Layers whenever simulation, scrubbing, or selection changes
  useEffect(() => {
    if (!mapInstanceRef.current || !layerGroupRef.current || !window.L) return;

    const L = window.L;
    const lg = layerGroupRef.current;
    lg.clearLayers();

    // 1. Render Spill Detection Polygon (Red Sheen)
    const spillPoly = L.polygon(DEFAULT_INCIDENT.spill_polygon, {
      color: '#ef4444',
      weight: 2,
      fillColor: '#b91c1c',
      fillOpacity: 0.45,
      dashArray: '4, 4'
    }).addTo(lg);

    spillPoly.bindPopup(`
      <div style="color: #0f172a; font-family: monospace;">
        <b style="color: #b91c1c;">SAR DARK-PATCH DETECTION</b><br/>
        Sensor: ${DEFAULT_INCIDENT.satellite_sensor}<br/>
        Area: ${DEFAULT_INCIDENT.area_sq_km} km²<br/>
        Confidence: ${DEFAULT_INCIDENT.confidence}%
      </div>
    `);

    // 2. Render Backwards Drift Line (Cyan Dotted Vector)
    const driftLatLngs = driftResult.path.map(p => [p.lat, p.lon]);
    L.polyline(driftLatLngs, {
      color: '#06b6d4',
      weight: 3,
      dashArray: '6, 6',
      opacity: 0.9
    }).addTo(lg);

    // 3. Render Calculated Origin Point Marker (Pulsing Target)
    const originIcon = L.divIcon({
      className: 'custom-origin-icon',
      html: `
        <div style="position: relative; width: 32px; height: 32px;">
          <div style="position: absolute; width: 100%; height: 100%; border-radius: 50%; background: rgba(239, 68, 68, 0.4); animation: ping 1.5s cubic-bezier(0,0,0.2,1) infinite;"></div>
          <div style="position: absolute; top: 6px; left: 6px; width: 20px; height: 20px; border-radius: 50%; background: #ef4444; border: 2px solid #ffffff; display: flex; align-items: center; justify-content: center;">
            <div style="width: 4px; height: 4px; border-radius: 50%; background: #fff;"></div>
          </div>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    const originMarker = L.marker([driftResult.origin.lat, driftResult.origin.lon], { icon: originIcon }).addTo(lg);
    originMarker.bindPopup(`
      <div style="color: #0f172a; font-family: monospace;">
        <b style="color: #ef4444;">CALCULATED DISCHARGE ORIGIN (T₀)</b><br/>
        Lat: ${driftResult.origin.lat.toFixed(4)}°N<br/>
        Lon: ${driftResult.origin.lon.toFixed(4)}°E<br/>
        Total Drift: ${driftResult.totalDistKm.toFixed(2)} km (${driftResult.netSpeedKmh.toFixed(1)} km/h)<br/>
        Est. Spill Time: ${DEFAULT_INCIDENT.estimated_spill_time}
      </div>
    `);

    // 4. Render Vessel Trajectories and Current Scrub Positions
    rankedVessels.forEach((v) => {
      const isGuilty = v.guilt_score >= 80;
      const isSelected = selectedVessel?.id === v.id;
      const trackLatLngs = v.track.map(p => [p.lat, p.lon]);

      // Track line
      L.polyline(trackLatLngs, {
        color: isGuilty ? '#f59e0b' : isSelected ? '#38bdf8' : '#64748b',
        weight: isSelected ? 4 : isGuilty ? 3 : 2,
        opacity: isSelected ? 1.0 : isGuilty ? 0.85 : 0.45,
        dashArray: isGuilty ? '2, 5' : null
      }).addTo(lg);

      // Interpolate vessel position at timelineScrub
      let currentPos = v.track[0];
      for (let i = 0; i < v.track.length - 1; i++) {
        if (v.track[i].t <= timelineScrub && timelineScrub <= v.track[i + 1].t) {
          const frac = (timelineScrub - v.track[i].t) / (v.track[i + 1].t - v.track[i].t);
          currentPos = {
            lat: v.track[i].lat + frac * (v.track[i + 1].lat - v.track[i].lat),
            lon: v.track[i].lon + frac * (v.track[i + 1].lon - v.track[i].lon),
            cog: v.track[i].cog,
            sog: v.track[i].sog
          };
          break;
        }
      }

      // Ship Marker
      const shipColor = isGuilty ? '#ef4444' : '#10b981';
      const shipIcon = L.divIcon({
        className: 'custom-ship-icon',
        html: `
          <div style="background: ${shipColor}; width: 18px; height: 18px; border-radius: 3px; border: 2px solid #ffffff; transform: rotate(${currentPos.cog || 0}deg); box-shadow: 0 0 10px ${shipColor}; display: flex; align-items: center; justify-content: center;">
            <div style="width: 0; height: 0; border-left: 3px solid transparent; border-right: 3px solid transparent; border-bottom: 7px solid #fff;"></div>
          </div>
        `,
        iconSize: [18, 18],
        iconAnchor: [9, 9]
      });

      const vesselMarker = L.marker([currentPos.lat, currentPos.lon], { icon: shipIcon }).addTo(lg);
      vesselMarker.on('click', () => setSelectedVessel(v));
      vesselMarker.bindTooltip(`${v.name} (${v.guilt_score}%)`, { permanent: false, direction: 'top' });

      // Render AIS Gap Warning Marker if present
      if (v.ais_gap?.detected && v.ais_gap?.location) {
        const gapIcon = L.divIcon({
          className: 'custom-gap-icon',
          html: `
            <div style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #fee2e2; display: flex; align-items: center; gap: 4px; box-shadow: 0 0 12px rgba(239,68,68,0.8);">
              ⚠️ AIS BLACKOUT (${v.ais_gap.duration_mins}m)
            </div>
          `,
          iconSize: [120, 20],
          iconAnchor: [60, 10]
        });

        const gapMarker = L.marker([v.ais_gap.location.lat, v.ais_gap.location.lon], { icon: gapIcon }).addTo(lg);
        gapMarker.bindPopup(`
          <div style="color: #0f172a; font-family: monospace;">
            <b style="color: #ef4444;">AIS TRANSPONDER ANOMALY</b><br/>
            Vessel: ${v.name}<br/>
            Duration: ${v.ais_gap.duration_mins} mins (${v.ais_gap.start_time} - ${v.ais_gap.end_time})<br/>
            Location: Directly at calculated discharge point
          </div>
        `);
      }
    });
  }, [driftResult, rankedVessels, timelineScrub, selectedVessel]);

  // Chart data for vessel guilt probability comparison
  const chartData = useMemo(() => {
    return rankedVessels.map(v => ({
      name: v.name.replace('MT ', '').replace('MV ', '').replace('FV ', ''),
      score: v.guilt_score,
      fill: v.guilt_score >= 80 ? '#ef4444' : v.guilt_score >= 45 ? '#f59e0b' : '#10b981'
    }));
  }, [rankedVessels]);

  return (
    <div className="flex flex-col h-screen w-full bg-slate-950 text-slate-100 font-sans select-none overflow-hidden">
      
      {/* 1. TOP TACTICAL COMMAND BAR */}
      <header className="h-14 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-4 flex items-center justify-between z-20">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded bg-cyan-500/10 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-sm tracking-wider text-cyan-400">SEAVISION AI</span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30 font-mono">
                MARPOL SURVEILLANCE ACTIVE
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono">INDIAN EEZ OFFSHORE BASIN // SAR-AIS DRIFT ATTRIBUTION</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 text-xs font-mono bg-slate-950 px-3 py-1.5 rounded border border-slate-800">
            <Radio className="h-3.5 w-3.5 text-emerald-400 animate-pulse" />
            <span className="text-slate-400">SENTINEL-1C C-SAR:</span>
            <span className="text-emerald-400">LIVE MESH READY</span>
          </div>

          <button
            onClick={() => setShowReportModal(true)}
            className="flex items-center space-x-2 bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white text-xs font-bold px-3 py-2 rounded border border-red-400/30 shadow-lg shadow-red-900/20 transition cursor-pointer"
          >
            <FileText className="h-3.5 w-3.5" />
            <span>EXPORT EVIDENCE DOSSIER</span>
          </button>
        </div>
      </header>

      {/* 2. MAIN 3-PANEL TACTICAL WORKSPACE */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* LEFT PANEL: Spill Telemetry & Ocean Drift Controls */}
        <aside className="w-80 border-r border-slate-800 bg-slate-900/60 overflow-y-auto flex flex-col p-4 space-y-4 text-xs font-mono">
          
          {/* Incident Badge */}
          <div className="p-3 bg-slate-950 rounded border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-slate-400 border-b border-slate-800 pb-1.5">
              <span>INCIDENT TELEMETRY</span>
              <span className="text-red-400 font-bold">CRITICAL</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div>
                <span className="text-slate-500">ID:</span>
                <p className="text-slate-200">{DEFAULT_INCIDENT.incident_id}</p>
              </div>
              <div>
                <span className="text-slate-500">SAR Confidence:</span>
                <p className="text-cyan-400 font-bold">{DEFAULT_INCIDENT.confidence}%</p>
              </div>
              <div>
                <span className="text-slate-500">Slick Area:</span>
                <p className="text-amber-400">{DEFAULT_INCIDENT.area_sq_km} km²</p>
              </div>
              <div>
                <span className="text-slate-500">Est. Volume:</span>
                <p className="text-amber-400">{DEFAULT_INCIDENT.volume_bbls} bbls</p>
              </div>
              <div className="col-span-2">
                <span className="text-slate-500">Detected Centroid:</span>
                <p className="text-slate-300">{DEFAULT_INCIDENT.detected_centroid.lat}°N, {DEFAULT_INCIDENT.detected_centroid.lon}°E</p>
              </div>
            </div>
          </div>

          {/* Environmental Vectors */}
          <div className="p-3 bg-slate-950 rounded border border-slate-800 space-y-3">
            <div className="flex justify-between items-center text-slate-400 border-b border-slate-800 pb-1">
              <span className="flex items-center space-x-1.5">
                <Waves className="h-3.5 w-3.5 text-cyan-400" />
                <span>OCEAN CURRENT</span>
              </span>
              <span className="text-cyan-400">{currentSpeed} kts @ {currentDir}°</span>
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Speed:</span>
                <span>{currentSpeed} knots</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="4.0"
                step="0.05"
                value={currentSpeed}
                onChange={(e) => setCurrentSpeed(parseFloat(e.target.value))}
                className="w-full accent-cyan-400 h-1 bg-slate-800 rounded appearance-none cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Direction (Towards):</span>
                <span>{currentDir}°</span>
              </div>
              <input
                type="range"
                min="0"
                max="360"
                step="5"
                value={currentDir}
                onChange={(e) => setCurrentDir(parseFloat(e.target.value))}
                className="w-full accent-cyan-400 h-1 bg-slate-800 rounded appearance-none cursor-pointer"
              />
            </div>
          </div>

          {/* Wind Leeway */}
          <div className="p-3 bg-slate-950 rounded border border-slate-800 space-y-3">
            <div className="flex justify-between items-center text-slate-400 border-b border-slate-800 pb-1">
              <span className="flex items-center space-x-1.5">
                <Wind className="h-3.5 w-3.5 text-amber-400" />
                <span>ATMOSPHERIC WIND</span>
              </span>
              <span className="text-amber-400">{windSpeed} kts (3% Leeway)</span>
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Wind Speed:</span>
                <span>{windSpeed} knots</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="40.0"
                step="0.5"
                value={windSpeed}
                onChange={(e) => setWindSpeed(parseFloat(e.target.value))}
                className="w-full accent-amber-400 h-1 bg-slate-800 rounded appearance-none cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Wind Vector:</span>
                <span>{windDir}°</span>
              </div>
              <input
                type="range"
                min="0"
                max="360"
                step="5"
                value={windDir}
                onChange={(e) => setWindDir(parseFloat(e.target.value))}
                className="w-full accent-amber-400 h-1 bg-slate-800 rounded appearance-none cursor-pointer"
              />
            </div>
          </div>

          {/* Hindcast Calculation Card */}
          <div className="p-3 bg-slate-950 rounded border border-cyan-500/30 space-y-2">
            <div className="flex justify-between items-center text-cyan-400 font-bold border-b border-slate-800 pb-1">
              <span>HINDCAST RESULT (T₀)</span>
              <Crosshair className="h-3.5 w-3.5 animate-spin" />
            </div>
            <div className="text-[11px] space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-500">Backwards Time:</span>
                <span className="text-slate-200">-{deltaHours} hours</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Origin Coord:</span>
                <span className="text-red-400 font-bold">{driftResult.origin.lat.toFixed(4)}°N, {driftResult.origin.lon.toFixed(4)}°E</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Total Drift:</span>
                <span className="text-slate-200">{driftResult.totalDistKm.toFixed(2)} km</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Net Vector:</span>
                <span className="text-slate-200">{driftResult.netSpeedKmh.toFixed(1)} km/h @ {driftResult.netDirDeg.toFixed(0)}°</span>
              </div>
            </div>
          </div>

          {/* Reset button */}
          <button
            onClick={() => {
              setCurrentSpeed(DEFAULT_ENV.current_speed);
              setCurrentDir(DEFAULT_ENV.current_dir);
              setWindSpeed(DEFAULT_ENV.wind_speed);
              setWindDir(DEFAULT_ENV.wind_dir);
              setDeltaHours(DEFAULT_INCIDENT.delta_hours);
            }}
            className="flex items-center justify-center space-x-2 w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition cursor-pointer"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>RESET TO SAR TELEMETRY</span>
          </button>
        </aside>

        {/* CENTER CANVAS: Interactive Tactical Map + Timeline Scrubber */}
        <main className="flex-1 flex flex-col relative bg-slate-950">
          
          {/* Map View Container */}
          <div className="flex-1 w-full h-full relative" ref={mapContainerRef}>
            {/* Map overlays / Legend */}
            <div className="absolute top-4 left-4 z-[400] bg-slate-900/90 backdrop-blur border border-slate-800 p-3 rounded shadow-2xl text-[11px] font-mono space-y-1.5 pointer-events-auto">
              <div className="text-slate-400 font-bold border-b border-slate-800 pb-1">TACTICAL MAP LAYERS</div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-600/50 border border-red-500 rounded-sm"></div>
                <span className="text-slate-300">Detected Oil Slick (SAR Mask)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-0.5 border-t-2 border-dashed border-cyan-400"></div>
                <span className="text-slate-300">Reverse Drift Vector (Hindcast)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500 border border-white"></div>
                <span className="text-slate-300">Calculated Spill Origin (T₀)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-1 bg-amber-500"></div>
                <span className="text-slate-300">Suspect Vessel Trajectory</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs">⚠️</span>
                <span className="text-slate-300">AIS Transponder Gap</span>
              </div>
            </div>
          </div>

          {/* BOTTOM TIMELINE SCRUBBER */}
          <div className="h-20 bg-slate-900/95 border-t border-slate-800 px-6 py-2 flex flex-col justify-center space-y-1.5 z-10">
            <div className="flex justify-between items-center text-xs font-mono">
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="p-1.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 hover:bg-cyan-500/30 transition cursor-pointer"
                >
                  {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </button>
                <div>
                  <span className="text-slate-400">SIMULATION TIME: </span>
                  <span className="text-cyan-400 font-bold">
                    {timelineScrub === 4.5
                      ? 'T_detect (10:00 UTC - NOW)'
                      : `T - ${(4.5 - timelineScrub).toFixed(2)}h (${(6.5 + timelineScrub * 0.77).toFixed(1)}:00 UTC)`}
                  </span>
                </div>
              </div>

              <div className="text-slate-400 text-[11px]">
                <span>T₀ DISCHARGE (06:30 UTC)</span> &rarr; <span>T_SAR DETECTION (10:00 UTC)</span>
              </div>
            </div>

            <input
              type="range"
              min="0.0"
              max="4.5"
              step="0.05"
              value={timelineScrub}
              onChange={(e) => {
                setIsPlaying(false);
                setTimelineScrub(parseFloat(e.target.value));
              }}
              className="w-full accent-cyan-400 h-2 bg-slate-800 rounded appearance-none cursor-pointer"
            />
          </div>
        </main>

        {/* RIGHT PANEL: Ranked Polluter Attribution Dossier */}
        <aside className="w-96 border-l border-slate-800 bg-slate-900/80 overflow-y-auto flex flex-col p-4 space-y-4">
          
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              <h2 className="font-mono font-bold text-sm text-slate-100">VESSEL ATTRIBUTION</h2>
            </div>
            <span className="text-xs font-mono text-slate-400">{rankedVessels.length} VESSELS TRACKED</span>
          </div>

          {/* Comparison Mini-Chart */}
          <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
            <div className="text-[10px] font-mono text-slate-400 mb-1">GUILT PROBABILITY COMPARISON (%)</div>
            <div className="h-24 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={9} />
                  <YAxis stroke="#64748b" fontSize={9} domain={[0, 100]} />
                  <RechartsTooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px' }}
                  />
                  <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Vessel Cards List */}
          <div className="space-y-3">
            {rankedVessels.map((vessel) => {
              const isSelected = selectedVessel?.id === vessel.id;
              const isHighSuspect = vessel.guilt_score >= 80;

              return (
                <div
                  key={vessel.id}
                  onClick={() => setSelectedVessel(vessel)}
                  className={`p-3.5 rounded border transition cursor-pointer font-mono ${
                    isSelected
                      ? 'bg-slate-800/90 border-cyan-500 ring-1 ring-cyan-500/50'
                      : isHighSuspect
                      ? 'bg-red-950/20 border-red-500/40 hover:bg-red-950/40'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1.5">
                    <div>
                      <h3 className="font-bold text-sm text-slate-100 flex items-center space-x-1.5">
                        <span>{vessel.name}</span>
                        {isHighSuspect && <AlertTriangle className="h-3.5 w-3.5 text-red-400" />}
                      </h3>
                      <p className="text-[10px] text-slate-400">{vessel.type} // {vessel.flag}</p>
                    </div>

                    <div className="text-right">
                      <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold border ${vessel.badgeColor}`}>
                        {vessel.guilt_score}% MATCH
                      </span>
                    </div>
                  </div>

                  {/* 3 Weighted Score Bars */}
                  <div className="space-y-1.5 my-2.5 text-[10px]">
                    <div>
                      <div className="flex justify-between text-slate-400 mb-0.5">
                        <span>Spatial Proximity (40%):</span>
                        <span className="text-slate-200">{vessel.metrics.s_d}% ({vessel.metrics.distAtSpill} km CPA)</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1 rounded overflow-hidden">
                        <div className="bg-cyan-500 h-full rounded" style={{ width: `${vessel.metrics.s_d}%` }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-400 mb-0.5">
                        <span>Trajectory Alignment (30%):</span>
                        <span className="text-slate-200">{vessel.metrics.s_t}% (Δθ: {vessel.metrics.headingDiff}°)</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1 rounded overflow-hidden">
                        <div className="bg-amber-500 h-full rounded" style={{ width: `${vessel.metrics.s_t}%` }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-400 mb-0.5">
                        <span>AIS Gap Anomaly (30%):</span>
                        <span className={vessel.ais_gap.detected ? 'text-red-400 font-bold' : 'text-slate-200'}>
                          {vessel.metrics.s_g}% {vessel.ais_gap.detected ? `(${vessel.ais_gap.duration_mins}m gap)` : '(Clean)'}
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-1 rounded overflow-hidden">
                        <div className={`h-full rounded ${vessel.ais_gap.detected ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${vessel.metrics.s_g}%` }}></div>
                      </div>
                    </div>
                  </div>

                  {/* Forensic Reason Snippets */}
                  <div className="text-[10px] space-y-1 border-t border-slate-800/80 pt-2">
                    {vessel.reasons.map((r, i) => (
                      <div key={i} className="flex items-start space-x-1 text-slate-300">
                        <ChevronRight className="h-3 w-3 text-cyan-400 flex-shrink-0 mt-0.5" />
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </aside>
      </div>

      {/* 3. MARPOL EVIDENCE DOSSIER MODAL */}
      {showReportModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 w-full max-w-3xl rounded-lg shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="p-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-red-400" />
                <div>
                  <h2 className="font-mono font-bold text-base text-slate-100">
                    MARPOL ANNEX I VIOLATION EVIDENCE DOSSIER
                  </h2>
                  <p className="text-xs font-mono text-slate-400">
                    LEGAL INVESTIGATION REPORT // INCIDENT REF: {DEFAULT_INCIDENT.incident_id}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowReportModal(false)}
                className="text-slate-400 hover:text-white text-lg font-mono px-2 py-1 cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Modal Printable Content */}
            <div className="p-6 overflow-y-auto space-y-6 font-mono text-xs text-slate-300">
              
              <div className="grid grid-cols-2 gap-4 bg-slate-950 p-4 rounded border border-slate-800">
                <div>
                  <span className="text-slate-500 font-bold">REPORTING AUTHORITY:</span>
                  <p className="text-slate-200">Directorate General of Shipping / Indian Coast Guard</p>
                </div>
                <div>
                  <span className="text-slate-500 font-bold">FILING DATE & TIME:</span>
                  <p className="text-slate-200">2026-09-29T10:30:00Z</p>
                </div>
                <div>
                  <span className="text-slate-500 font-bold">SATELLITE EVIDENCE:</span>
                  <p className="text-cyan-400">Sentinel-1C Synthetic Aperture Radar (10m Resolution)</p>
                </div>
                <div>
                  <span className="text-slate-500 font-bold">SLICK ESTIMATE:</span>
                  <p className="text-amber-400">14.82 km² / ~850 Barrels Heavy Crude</p>
                </div>
              </div>

              {/* Suspect Info */}
              <div className="border border-red-500/40 bg-red-950/20 p-4 rounded space-y-3">
                <div className="flex justify-between items-center border-b border-red-500/30 pb-2">
                  <span className="text-red-400 font-bold text-sm">PRIMARY ACCUSED VESSEL</span>
                  <span className="bg-red-500/30 text-red-300 px-2 py-0.5 rounded font-bold">
                    {rankedVessels[0]?.guilt_score}% GUILT PROBABILITY
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <span className="text-slate-500">Vessel Name:</span>
                    <p className="font-bold text-slate-100">{rankedVessels[0]?.name}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">IMO / MMSI:</span>
                    <p className="text-slate-200">{rankedVessels[0]?.imo} / {rankedVessels[0]?.mmsi}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Flag State:</span>
                    <p className="text-slate-200">{rankedVessels[0]?.flag}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Vessel Type:</span>
                    <p className="text-slate-200">{rankedVessels[0]?.type}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Deadweight Tonnage:</span>
                    <p className="text-slate-200">{rankedVessels[0]?.dwt.toLocaleString()} DWT</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Cargo Onboard:</span>
                    <p className="text-slate-200">{rankedVessels[0]?.cargo}</p>
                  </div>
                </div>
              </div>

              {/* Forensic Scientific Proof */}
              <div className="space-y-2">
                <h4 className="font-bold text-slate-200 border-b border-slate-800 pb-1">
                  OCEANOGRAPHIC HINDCAST & KINEMATIC EVIDENCE SUMMARY
                </h4>
                <ul className="space-y-1.5 list-disc pl-4 text-slate-300">
                  <li>
                    <strong>Hydrodynamic Drift Hindcast:</strong> Slick centroid displaced 11.31 km along 058° heading over 3.5 hours driven by 1.25 knot current and 16.5 knot wind (3% leeway).
                  </li>
                  <li>
                    <strong>Spatial Co-location:</strong> Vessel crossed within 0.12 km of calculated discharge origin at exact estimated spill timestamp (06:30 UTC).
                  </li>
                  <li>
                    <strong>Intentional AIS Blackout Anomaly:</strong> Transponder was deactivated for 45 minutes between 06:15 UTC and 07:00 UTC directly spanning the discharge coordinates.
                  </li>
                  <li>
                    <strong>Geometric Axis Alignment:</strong> Vessel course of 058.5° matches the linear streak orientation of the dark-patch SAR radar return.
                  </li>
                </ul>
              </div>

              {/* Recommended Legal Actions */}
              <div className="p-3 bg-slate-950 rounded border border-slate-800 text-[11px] text-slate-400">
                <strong className="text-amber-400">LEGAL RECOMMENDATION:</strong> Issue Port State Control warrant for immediate board-and-search upon arrival at JNPT. Authorize sampling of slop tanks, OWS (Oil Water Separator) logs, and hydrocarbon gas chromatography matching.
              </div>
            </div>

            {/* Modal Footer CTA */}
            <div className="p-4 border-t border-slate-800 bg-slate-950 flex justify-end space-x-3">
              <button
                onClick={() => setShowReportModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-mono text-xs cursor-pointer"
              >
                CLOSE
              </button>
              <button
                onClick={() => window.print()}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-mono text-xs font-bold cursor-pointer"
              >
                <Printer className="h-4 w-4" />
                <span>PRINT / SAVE AS PDF</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
