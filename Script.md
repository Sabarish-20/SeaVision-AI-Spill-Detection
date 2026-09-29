# 🎬 SeaVision AI — Complete Video Demonstration Script

**Project Title:** SeaVision AI: Catching Spills with ML & AIS Data  
**Problem Statement:** SIH26143 (Smart India Hackathon / Maritime Domain Awareness)  
**Video Reference:** `recordings/seavision_ai_walkthrough_demo.webm` (1080p Full-HD @ 1920×1080)  
**Target Duration:** 01:18 (Video Sync) / Presentation Ready  
**Tone & Persona:** Confident, technical, authoritative, and engaging (Defense / Geospatial AI Product Launch).

---

## 📑 Quick Scene Index

1. [0:00 – 0:10] **Scene 1: Tactical Command Center & Satellite Feed Overview**
2. [0:10 – 0:25] **Scene 2: Real-Time Detection Pass Simulation (5-Phase Automated Pipeline)**
3. [0:25 – 0:34] **Scene 3: MARPOL Annex I Legal Evidence Dossier**
4. [0:34 – 0:44] **Scene 4: Reverse-Drift Hydrodynamic Parameter Tuning**
5. [0:44 – 0:52] **Scene 5: 4.5-Hour Kinematic Reconstruction & Blackout Anomaly**
6. [0:52 – 1:02] **Scene 6: Multi-Scenario Surveillance Across the Indian EEZ**
7. [0:02 – 1:08] **Scene 7: ISRO MOSDAC Satellite Telemetry Gateway & Bhuvan WMS**
8. [1:08 – 1:12] **Scene 8: International Data Standards (Marine Cadastre AIS & Zenodo SAR)**
9. [1:12 – 1:16] **Scene 9: Indian Coast Guard Tactical Intercept Dispatch**
10. [1:16 – 1:18] **Scene 10: Conclusion & System Wrap-Up**

---

## 🎙️ Complete Time-Stamped Script

---

### ⏱️ **0:00 – 0:10 | Scene 1: Tactical Command Center & Live Feed Overview**

* **Scene Captured:** Full-screen view of the SeaVision AI Tactical Operations Center at `http://localhost:8000/`. Cursor smoothly glides across the top emergency alert ribbon, the Sentinel-1 SAR telemetry card on the left panel, and the suspect polluter cards on the right.
* **Highlights in Video:**
  * Flashing red live surveillance beacon: `● LIVE RADAR PASS`.
  * Real-time telemetry connection to port 8000.
  * ISRO Bhuvan (NRSC) high-resolution nautical GIS basemap.
  * Active suspect ranking panel highlighting 4 tracked vessels.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"Welcome to **SeaVision AI**, an autonomous geospatial AI platform built for Maritime Domain Awareness to detect ocean oil spills and mathematically identify guilty polluters using Synthetic Aperture Radar, hydrodynamic reverse-drift modeling, and AIS anomaly forensics."*

---

### ⏱️ **0:10 – 0:25 | Scene 2: Real-Time Detection Pass Simulation**

* **Scene Captured:** User clicks the pulsing gradient button **`▶️ SIMULATE REAL-TIME DETECTION PASS`**. The bottom status pill emerges and steps through the 5 automated pipeline phases while sonar chirps and alert sirens play.
* **Highlights in Video:**
  * **Phase 1:** Ingests Sentinel-1C C-SAR radar swath at 10-meter resolution.
  * **Phase 2:** Deep U-Net segmentation isolates the fluorescent red $14.82\text{ km}^2$ dark patch (96.2% confidence).
  * **Phase 3:** Assimilates ISRO Oceansat-3 OSCAT wind ($16.5\text{ kts}$) & SARAL-AltiKa current ($1.25\text{ kts}$) to backtrack the hydrodynamic drift trail to $T_0$.
  * **Phase 4:** Detects an intentional $45\text{-minute}$ AIS transponder blackout on the crude tanker *MT ARABIAN TITAN* at the exact spill origin.
  * **Phase 5:** System triggers a critical **100% MARPOL Annex I violation match**.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"When we trigger a simulated real-time satellite pass, our multi-source pipeline ingests a Sentinel-1 radar swath, performs deep U-Net dark-patch segmentation on a 14.82 square kilometer crude slick, backtracks ocean drift forces using ISRO MOSDAC telemetry, and flags an intentional 45-minute AIS blackout on the crude oil tanker MT ARABIAN TITAN with 100% guilt probability."*

---

### ⏱️ **0:25 – 0:34 | Scene 3: MARPOL Annex I Legal Evidence Dossier**

* **Scene Captured:** The full **MARPOL Annex I Violation Evidence Dossier** modal automatically opens over the screen. The viewer scrolls through forensic metrics, ship specifications, and legal recommendations before closing.
* **Highlights in Video:**
  * Formal incident reference: `SV-IND-2026-0929-01`.
  * Accused vessel specifications: *MT ARABIAN TITAN* (IMO: 9384812, MMSI: 636018244, VLCC Tanker, 305,000 DWT).
  * Forensic kinematics: CPA distance of just $0.12\text{ km}$, angular trajectory deviation of $0.0^\circ$, and transponder disabled for 45 minutes at discharge coordinates.
  * Legal directive: Port State Control (PSC) detention and gas chromatography oil fingerprinting.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"The system automatically compiles a courtroom-admissible MARPOL legal dossier, verifying that the tanker's trajectory passed within 120 meters of the discharge point with zero angular deviation during its deliberate transponder blackout."*

---

### ⏱️ **0:34 – 0:44 | Scene 4: Reverse-Drift Hydrodynamic Parameter Tuning**

* **Scene Captured:** User adjusts the **Current Speed** slider up to $2.85\text{ knots}$, increases the **Wind Speed** slider to $28.0\text{ knots}$, and rotates the wind direction to $110^\circ$. The blue $T_0$ origin marker and dashed trajectory line dynamically reposition across the map in real-time. The user then clicks **`RESET TO BASE CONDITIONS`**.
* **Highlights in Video:**
  * Real-time vector math execution: $\vec{P}_{\text{origin}} = \vec{P}_{\text{detected}} - (\vec{V}_{\text{current}} + 0.03 \cdot \vec{V}_{\text{wind}}) \times \Delta t$.
  * Instant recalculation of origin coordinates, total drift displacement, and net velocity.
  * Instant restoration of verified ocean baseline conditions.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"Operators can interactively tune environmental hydrodynamic parameters. As current speed and atmospheric wind leeway are modified, our reverse-drift physics engine recalculates the discharge origin in real-time, with one-click baseline restoration."*

---

### ⏱️ **0:44 – 0:52 | Scene 5: 4.5-Hour Kinematic Reconstruction & Blackout Anomaly**

* **Scene Captured:** User clicks the **Play (▶)** button on the bottom timeline scrubber. Vessel icons and time indicators animate from $T_0$ ($06:30\text{ UTC}$) to $T_{\text{detect}}$ ($10:00\text{ UTC}$), highlighting the dotted circular blackout anomaly zone.
* **Highlights in Video:**
  * Continuous kinematic tracking of all ships in the 50 km surveillance radius.
  * Innocent container ships (*MV INDUS TRADER*) and fishing vessels (*FV SAGAR RATNA*) show uninterrupted signals.
  * Red anomaly boundary highlights the intentional blackout window where the polluter dumped oily bilge water.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"The interactive time scrubber reconstructs historical vessel movements over the 4.5-hour window. While innocent container ships maintain clean transponder tracks, MT ARABIAN TITAN's transponder was deliberately silenced at the exact time of discharge."*

---

### ⏱️ **0:52 – 1:02 | Scene 6: Multi-Scenario Surveillance Across the Indian EEZ**

* **Scene Captured:** User selects the **SCENARIO** dropdown:
  1. Switches to **Scenario 2: Gulf of Kachchh Tanker Fairway (Gujarat)** $\to$ map recenters on $22.51^\circ\text{N}, 69.24^\circ\text{E}$ tracking chemical tanker *MT OCEANIC GLORY*.
  2. Switches to **Scenario 3: Bay of Bengal Approaches (Paradip Basin, Odisha)** $\to$ map recenters on $20.14^\circ\text{N}, 86.82^\circ\text{E}$ tracking bulk carrier *MV BENGAL STAR*.
  3. Returns to **Scenario 1: Mumbai High Offshore Basin**.
* **Highlights in Video:**
  * Dynamic multi-region adaptability across the Arabian Sea, Gulf of Kachchh, and Bay of Bengal.
  * Automatic recalibration of regional tidal currents, wind leeway, and vessel traffic.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"SeaVision AI supports multi-region operations across India's Exclusive Economic Zone—from chemical spills in the Gulf of Kachchh fairway to deepwater bilge discharges off Paradip Port in the Bay of Bengal."*

---

### ⏱️ **1:02 – 1:08 | Scene 7: ISRO MOSDAC Satellite Telemetry Gateway & Bhuvan WMS**

* **Scene Captured:** User navigates to the **`ISRO MOSDAC Gateway`** tab, views the operational satellite mission cards, and clicks **`SYNC REAL-TIME MOSDAC TELEMETRY`**.
* **Highlights in Video:**
  * Active mission telemetry: **Oceansat-3 OSCAT (Ku-band Scatterometer)**, **SARAL-AltiKa (Ka-band Altimeter)**, **SCATSAT-1**, and **INSAT-3DR**.
  * Zero commercial third-party map keys—100% powered by Indian Government GIS infrastructure (**ISRO Bhuvan NRSC WMS**).
* **Dialogue / Voiceover (Word-for-Word):**
  > *"Our platform directly connects to the ISRO MOSDAC data gateway, assimilating real-time Oceansat-3 scatterometer winds and SARAL altimetry currents without requiring commercial map keys."*

---

### ⏱️ **1:08 – 1:12 | Scene 8: International Data Standards (Marine Cadastre & Zenodo)**

* **Scene Captured:** User clicks the **`Marine Cadastre AIS`** tab, scrolling the 17-column CSV table, then clicks the **`Zenodo S1 SAR`** tab displaying C-SAR IW GRDH metadata and 3-class segmentation masks.
* **Highlights in Video:**
  * 17-field schema conformance with `marinecadastre.gov/accessais`.
  * Benchmark Zenodo Sentinel-1 SAR dataset (DOI: `10.5281/zenodo.3842416`).
  * One-click download buttons for CSV and GeoJSON payloads.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"We ensure full interoperability by adhering to the international Marine Cadastre 17-field AIS standard and Zenodo Sentinel-1 SAR benchmark datasets with full CSV and GeoJSON export capabilities."*

---

### ⏱️ **1:12 – 1:16 | Scene 9: Indian Coast Guard Tactical Intercept Dispatch**

* **Scene Captured:** User returns to the Tactical Map and clicks **`🚨 DISPATCH COAST GUARD`**. The Flash Operational Order modal pops up with mission priority ratings and asset assignments.
* **Highlights in Video:**
  * Flash Level 1 Immediate Intercept Directive from MRCC Mumbai.
  * Dispatched tactical assets: **ICGS Samudra Prahari** (Pollution Control Vessel) & **Dornier 228 Aircraft** (CG Squadron 750).
  * Directives: Aerial SLAR/FLIR pod tracking, physical grab sampling, and Form B Notice of Violation.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"With one click, operators can transmit a Flash Level 1 Intercept Order to Indian Coast Guard headquarters, dispatching pollution patrol vessels and Dornier surveillance aircraft for physical sampling."*

---

### ⏱️ **1:16 – 1:18 | Scene 10: Conclusion & System Wrap-Up**

* **Scene Captured:** User closes the modal and shows the final high-contrast Tactical Operations Center overview.
* **Highlights in Video:**
  * 100% automated test passing badge (31/31 suites passed).
  * Complete full-stack architecture running seamlessly.
* **Dialogue / Voiceover (Word-for-Word):**
  > *"SeaVision AI: Transforming ocean surveillance into actionable, legal enforcement. Thank you."*

---

## 🎯 Tips for Delivering the Voiceover

1. **Audio Recording:** Use a clear microphone (or USB headset) in a quiet room.
2. **Speed & Clarity:** Speak at a steady, professional pace ($\sim 140\text{ words per minute}$).
3. **Synchronization:** Keep the video playing on one screen or player (e.g., VLC or Chrome) while reading the corresponding lines at each timestamp.
4. **Key Words to Emphasize:** *Sentinel-1 SAR*, *U-Net segmentation*, *ISRO MOSDAC*, *MT ARABIAN TITAN*, *45-minute blackout*, *MARPOL Annex I*, *Indian Coast Guard*.
