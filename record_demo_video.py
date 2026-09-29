"""
SeaVision AI - Automated High-Definition Video Recording Script
Uses Playwright to interactively execute the complete voiceover demonstration workflow
and outputs a full 1080p recorded video file (recordings/seavision_ai_demo_walkthrough.webm).
"""

import os
import time
from playwright.sync_api import sync_playwright

RECORDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
os.makedirs(RECORDING_DIR, exist_ok=True)

def record_full_walkthrough():
    print("=" * 70)
    print("🎬 STARTING SEAVISION AI HIGH-DEFINITION VIDEO RECORDING")
    print(f"📁 Output Directory: {RECORDING_DIR}")
    print("=" * 70)

    with sync_playwright() as p:
        # Launch Chromium with 1080p recording
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-dev-shm-usage"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=RECORDING_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        # Handle browser alert / dialog prompts automatically
        page.on("dialog", lambda dialog: dialog.accept())

        print("🌐 [0:00] Navigating to Tactical Command Center: http://localhost:8000/ ...")
        page.goto("http://localhost:8000/", wait_until="networkidle")
        page.wait_for_timeout(3000)

        # ----------------------------------------------------------------------
        # SCENE 1: Introduction & Command Center Overview (0:00 - 0:30)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 1] Overview of Tactical Map & Live Radar Feed...")
        page.mouse.move(960, 400)
        page.wait_for_timeout(2000)
        page.mouse.move(200, 200) # Hover on SAR incident telemetry card
        page.wait_for_timeout(1500)
        page.mouse.move(1700, 250) # Hover on suspect card
        page.wait_for_timeout(2000)

        # ----------------------------------------------------------------------
        # SCENE 2: Live Real-Time Detection Pass Simulation (0:30 - 1:30)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 2] Triggering Real-Time Detection Pass Simulation...")
        page.click("#btn-run-realtime-sim")
        
        # Wait through all 5 phases (Phase 1 Swath -> Phase 2 U-Net -> Phase 3 Drift -> Phase 4 AIS -> Phase 5 Alert)
        print("   -> Phase 1 to 5 executing on map...")
        page.wait_for_timeout(9500)

        # Dossier modal auto-opens at end of simulation
        print("   -> Inspecting generated MARPOL Evidence Dossier...")
        page.wait_for_timeout(2500)
        page.click("#btn-close-modal")
        page.wait_for_timeout(1500)

        # ----------------------------------------------------------------------
        # SCENE 3: Reverse-Drift Hydrodynamics & Live Sliders (1:30 - 2:30)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 3] Tuning Hydrodynamic Current & Wind Leeway Sliders...")
        
        def set_slider(selector, val):
            page.eval_on_selector(selector, f"(el) => {{ el.value = {val}; el.dispatchEvent(new Event('input', {{ bubbles: true }})); }}")

        set_slider("#slider-current-speed", 2.85)
        page.wait_for_timeout(1800)
        set_slider("#slider-wind-speed", 28.0)
        page.wait_for_timeout(1800)
        set_slider("#slider-wind-dir", 110)
        page.wait_for_timeout(1800)
        
        print("   -> Resetting to verified oceanographic baseline...")
        page.click("#btn-reset-env")
        page.wait_for_timeout(2000)

        # ----------------------------------------------------------------------
        # SCENE 4: Interactive Time Scrubber & Kinematic Blackout (2:30 - 3:30)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 4] Reconstructing Timeline from T0 to T_detect...")
        # Start playback
        page.click("#btn-play-pause")
        page.wait_for_timeout(6000) # Let it play for 6 seconds
        page.click("#btn-play-pause") # Pause
        page.wait_for_timeout(1500)

        # ----------------------------------------------------------------------
        # SCENE 5: Multi-Scenario Regional Switcher (3:30 - 4:30)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 5] Switching Maritime Scenarios Across Indian EEZ...")
        
        # Scenario 2: Gulf of Kachchh
        print("   -> Loading Scenario 2: Gulf of Kachchh Tanker Fairway...")
        page.select_option("#select-scenario", "gulf_of_kachchh")
        page.wait_for_timeout(4000)

        # Scenario 3: Bay of Bengal
        print("   -> Loading Scenario 3: Bay of Bengal Paradip Approaches...")
        page.select_option("#select-scenario", "bay_of_bengal")
        page.wait_for_timeout(4000)

        # Return to Scenario 1: Mumbai High
        print("   -> Returning to Scenario 1: Mumbai High Offshore Basin...")
        page.select_option("#select-scenario", "mumbai_high")
        page.wait_for_timeout(3000)

        # ----------------------------------------------------------------------
        # SCENE 6: ISRO MOSDAC Satellite Gateway (4:30 - 5:30)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 6] Inspecting ISRO MOSDAC Satellite Data Gateway...")
        page.click("#tab-mosdac")
        page.wait_for_timeout(2500)
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(2000)
        
        print("   -> Syncing Real-Time MOSDAC Telemetry...")
        page.click("#btn-sync-mosdac")
        page.wait_for_timeout(3000)

        # ----------------------------------------------------------------------
        # SCENE 7: Marine Cadastre AIS & Zenodo SAR Standards (5:30 - 6:30)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 7] Viewing Marine Cadastre AIS & Zenodo Datasets...")
        page.click("#tab-marinecadastre")
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, -400)
        page.wait_for_timeout(1000)

        page.click("#tab-zenodo")
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(2000)

        # ----------------------------------------------------------------------
        # SCENE 8: MARPOL Evidence Dossier & Coast Guard Intercept (6:30 - 7:30)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 8] Transmitting Coast Guard Intercept Flash Directive...")
        page.click("#tab-tactical")
        page.wait_for_timeout(2000)

        # Dispatch Coast Guard
        page.click("#btn-dispatch-icg")
        page.wait_for_timeout(3500)
        page.click("#btn-ack-dispatch")
        page.wait_for_timeout(1500)

        # ----------------------------------------------------------------------
        # SCENE 9: Conclusion & Overview (7:30 - 8:00)
        # ----------------------------------------------------------------------
        print("🎥 [Scene 9] Final Tactical Command Overview...")
        page.mouse.move(960, 540)
        page.wait_for_timeout(3000)

        # Retrieve video path
        video_path = page.video.path()
        context.close()
        browser.close()

        final_video_name = os.path.join(RECORDING_DIR, "seavision_ai_walkthrough_demo.webm")
        if os.path.exists(video_path):
            os.rename(video_path, final_video_name)
            print("=" * 70)
            print(f"🎉 VIDEO RECORDING COMPLETE!")
            print(f"📹 Video File Saved: {final_video_name}")
            print(f"📊 Size: {os.path.getsize(final_video_name) / (1024 * 1024):.2f} MB")
            print("=" * 70)
            return final_video_name
        else:
            print("⚠️ Video file path not found.")
            return None

if __name__ == "__main__":
    record_full_walkthrough()
