"""
Golden Scenario Replay Generator (Phase 0 / Phase 1 / Phase 3)
Generates a realistic 30-minute AIS capture file in AISStream JSONL format.
Includes background traffic + target vessel (SEAPRIDE, MMSI 572467210, IMO 9187643) that exhibits:
- Normal cruising
- Abrupt AIS gap (14 minutes)
- Reappearance with position/course anomaly
"""

import os
import json
import math
from datetime import datetime, timezone, timedelta

OUTPUT_FILE = "data/replay/golden_scenario.jsonl"

def make_position_report(mmsi, ship_name, imo, lat, lon, sog, cog, heading, dt_utc):
    time_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S.000000 +0000 UTC")
    return {
        "MessageType": "PositionReport",
        "Message": {
            "PositionReport": {
                "Cog": round(cog, 1),
                "CommunicationState": 0,
                "Latitude": round(lat, 5),
                "Longitude": round(lon, 5),
                "MessageID": 1,
                "NavigationalStatus": 0,
                "RateOfTurn": 0,
                "RepeatIndicator": 0,
                "Sog": round(sog, 1),
                "Spare": 0,
                "SpecialManoeuvreIndicator": 0,
                "Timestamp": dt_utc.second,
                "TrueHeading": int(heading) % 360,
                "UserID": int(mmsi),
                "Valid": True
            }
        },
        "MetaData": {
            "MMSI": int(mmsi),
            "MMSI_String": str(mmsi),
            "ShipName": ship_name,
            "IMO": int(imo) if imo else None,
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "time_utc": time_str
        }
    }

def make_static_data(mmsi, ship_name, imo, callsign, ship_type, dt_utc):
    time_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S.000000 +0000 UTC")
    return {
        "MessageType": "ShipStaticData",
        "Message": {
            "ShipStaticData": {
                "AisVersion": 2,
                "CallSign": callsign,
                "Destination": "SINGAPORE",
                "Dimension": {"A": 150, "B": 30, "C": 15, "D": 15},
                "Draught": 11.2,
                "Eta": {"Day": 20, "Hour": 12, "Minute": 0, "Month": 10},
                "FixType": 1,
                "ImoNumber": int(imo) if imo else 0,
                "MaximumPresentStaticDraught": 11.2,
                "MessageID": 5,
                "Name": ship_name,
                "RepeatIndicator": 0,
                "Type": ship_type,
                "UserID": int(mmsi),
                "Valid": True
            }
        },
        "MetaData": {
            "MMSI": int(mmsi),
            "MMSI_String": str(mmsi),
            "ShipName": ship_name,
            "IMO": int(imo) if imo else None,
            "latitude": 0.0,
            "longitude": 0.0,
            "time_utc": time_str
        }
    }

def generate_scenario():
    os.makedirs(os.path.dirname(os.path.abspath(OUTPUT_FILE)), exist_ok=True)
    
    base_time = datetime(2026, 10, 13, 10, 0, 0, tzinfo=timezone.utc)
    duration_minutes = 30
    step_seconds = 30
    
    # Target corridor: Gulf of Oman / Hormuz approach (approx 25.0 to 26.0 N, 56.5 to 58.0 E)
    # Target vessel (OFAC sanctioned entity in sanctions.db)
    target = {
        "mmsi": "572467210",
        "imo": "9187643",
        "name": "SEAPRIDE",
        "callsign": "V3RA",
        "type": 80, # Tanker
        "start_lat": 25.3000,
        "start_lon": 56.8000,
        "speed": 13.5, # knots
        "course": 95.0, # degrees East-South-East
        # AIS GAP: silence between minute 8 and minute 22
        "gap_start_min": 8,
        "gap_end_min": 22
    }
    
    # 8 background vessels to create realistic maritime density
    bg_vessels = [
        {"mmsi": "211284910", "imo": "9345120", "name": "MSC GEMINI", "callsign": "DLBZ", "type": 70, "lat": 25.55, "lon": 56.60, "speed": 16.0, "course": 110.0},
        {"mmsi": "311000421", "imo": "9412034", "name": "NORDIC TRADER", "callsign": "C6YZ", "type": 70, "lat": 25.15, "lon": 56.70, "speed": 12.0, "course": 90.0},
        {"mmsi": "477123450", "imo": "9501122", "name": "PACIFIC HARMONY", "callsign": "VRAB", "type": 80, "lat": 25.70, "lon": 57.10, "speed": 14.2, "course": 290.0},
        {"mmsi": "636015678", "imo": "9287340", "name": "ALEXANDRA", "callsign": "A8TG", "type": 80, "lat": 25.40, "lon": 57.30, "speed": 13.0, "course": 285.0},
        {"mmsi": "228345000", "imo": "9112233", "name": "OCEAN EXPLORER", "callsign": "FNBD", "type": 60, "lat": 25.20, "lon": 56.95, "speed": 9.5, "course": 45.0},
        {"mmsi": "538002910", "imo": "9445566", "name": "STAR HORIZON", "callsign": "V7KT", "type": 70, "lat": 25.60, "lon": 56.90, "speed": 15.1, "course": 105.0},
        {"mmsi": "412345678", "imo": "9612345", "name": "HAI SHENG 9", "callsign": "BHEF", "type": 70, "lat": 25.45, "lon": 57.50, "speed": 11.8, "course": 270.0},
        {"mmsi": "352123000", "imo": "9701234", "name": "GULF PIONEER", "callsign": "3FXE", "type": 52, "lat": 25.10, "lon": 56.65, "speed": 8.0, "course": 30.0},
    ]
    
    events = []
    
    # 1. Static messages for all vessels at t=0
    for v in [target] + bg_vessels:
        events.append((0, make_static_data(v["mmsi"], v["name"], v["imo"], v["callsign"], v["type"], base_time)))
        
    total_steps = (duration_minutes * 60) // step_seconds
    
    for step in range(total_steps):
        current_sec = step * step_seconds
        current_time = base_time + timedelta(seconds=current_sec)
        current_min = current_sec / 60.0
        
        # Position updates for background vessels (continuous)
        for v in bg_vessels:
            # 1 knot = 1.852 km/h; at lat 25°, 1 deg lat ≈ 111 km, 1 deg lon ≈ 100 km
            dist_km = (v["speed"] * 1.852) * (step_seconds / 3600.0)
            rad = math.radians(v["course"])
            d_lat = (dist_km * math.cos(rad)) / 111.0
            d_lon = (dist_km * math.sin(rad)) / 100.0
            v["lat"] += d_lat
            v["lon"] += d_lon
            
            # emit position report
            events.append((current_sec, make_position_report(
                v["mmsi"], v["name"], v["imo"], v["lat"], v["lon"],
                v["speed"], v["course"], v["course"], current_time
            )))
            
        # Target vessel logic:
        # Check if in GAP window
        in_gap = target["gap_start_min"] <= current_min < target["gap_end_min"]
        
        # Target position calculation
        dist_km = (target["speed"] * 1.852) * (step_seconds / 3600.0)
        rad = math.radians(target["course"])
        d_lat = (dist_km * math.cos(rad)) / 111.0
        d_lon = (dist_km * math.sin(rad)) / 100.0
        target["start_lat"] += d_lat
        target["start_lon"] += d_lon
        
        if not in_gap:
            # Reappearance after minute 22: course altered to 125° and speed reduced to 10.8 kn
            if current_min >= target["gap_end_min"]:
                speed = 10.8
                course = 125.0
            else:
                speed = target["speed"]
                course = target["course"]
                
            events.append((current_sec, make_position_report(
                target["mmsi"], target["name"], target["imo"],
                target["start_lat"], target["start_lon"],
                speed, course, course, current_time
            )))
            
    # Sort events by relative timestamp
    events.sort(key=lambda x: x[0])
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for _, record in events:
            f.write(json.dumps(record) + "\n")
            
    print(f"[+] Golden Scenario generated successfully at {OUTPUT_FILE}!")
    print(f"    - Total Events: {len(events)}")
    print(f"    - Duration: {duration_minutes} minutes ({total_steps} steps)")
    print(f"    - Target Vessel: {target['name']} (MMSI: {target['mmsi']}, IMO: {target['imo']})")
    print(f"    - Gap Trigger Window: minute {target['gap_start_min']} to {target['gap_end_min']} (14 minutes of silence)")
    print(f"    - Background Vessels: {len(bg_vessels)}")

if __name__ == "__main__":
    generate_scenario()
