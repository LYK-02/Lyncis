"""
AISStream Validation & Recorder Script (Phase 0)
Connects to wss://stream.aisstream.io/v0/stream
Subscribes to bounding box, logs throughput, counts unique vessels,
calculates reports/vessel, and records capture to JSONL.
"""

import os
import sys
import json
import time
import argparse
import asyncio
from datetime import datetime, timezone
import websockets

# Predefined bounding boxes for high-traffic corridors
BOUNDING_BOXES = {
    "english_channel": [[50.0, -2.0], [51.5, 2.0]],
    "singapore_strait": [[1.1, 103.5], [1.5, 104.2]],
    "gibraltar": [[35.8, -6.0], [36.3, -5.0]],
    "rotterdam_approach": [[51.8, 3.5], [52.3, 4.5]],
    "malacca_strait": [[2.0, 101.0], [3.0, 102.5]],
}

async def run_ais_collector(api_key: str, bbox_name: str, duration_sec: int, output_file: str):
    bbox = BOUNDING_BOXES.get(bbox_name, BOUNDING_BOXES["english_channel"])
    url = "wss://stream.aisstream.io/v0/stream"
    
    print("=" * 60)
    print("Lyncis Phase 0 — AISStream Live Validation & Capture")
    print(f"Target Bounding Box : {bbox_name} -> {bbox}")
    print(f"Target Duration     : {duration_sec} seconds ({duration_sec / 60:.1f} minutes)")
    print(f"Output Capture File : {output_file}")
    print("=" * 60)
    
    sub_msg = {
        "APIKey": api_key,
        "BoundingBoxes": [bbox],
        "FilterMessageTypes": ["PositionReport", "StandardClassBPositionReport", "ShipStaticData"]
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    vessel_reports = {}  # mmsi -> count
    vessel_names = {}    # mmsi -> name
    msg_types = {}
    total_msgs = 0
    start_time = time.time()
    
    try:
        async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
            print("[+] Connected to AISStream WebSocket. Sending subscription...")
            await ws.send(json.dumps(sub_msg))
            print("[+] Subscription sent. Listening for messages...")
            
            with open(output_file, "a", encoding="utf-8") as f_out:
                while time.time() - start_time < duration_sec:
                    remaining = int(duration_sec - (time.time() - start_time))
                    try:
                        raw_msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    except asyncio.TimeoutError:
                        print(f"[*] Waiting for data... ({remaining}s remaining)")
                        continue
                        
                    data = json.loads(raw_msg)
                    total_msgs += 1
                    
                    # Persist raw message line-by-line
                    f_out.write(json.dumps(data) + "\n")
                    f_out.flush()
                    
                    # Extract metadata
                    meta = data.get("MetaData", {})
                    mmsi = meta.get("MMSI") or meta.get("MMSI_String")
                    ship_name = meta.get("ShipName", "").strip()
                    msg_type = data.get("MessageType", "Unknown")
                    
                    msg_types[msg_type] = msg_types.get(msg_type, 0) + 1
                    
                    if mmsi:
                        vessel_reports[mmsi] = vessel_reports.get(mmsi, 0) + 1
                        if ship_name and ship_name != "Unknown":
                            vessel_names[mmsi] = ship_name
                            
                    # Progress log every 20 messages or every 30s
                    if total_msgs % 25 == 0:
                        elapsed = time.time() - start_time
                        rate = total_msgs / elapsed if elapsed > 0 else 0
                        avg_per_vessel = total_msgs / len(vessel_reports) if vessel_reports else 0
                        print(f"[{elapsed:.0f}s elapsed] Msgs: {total_msgs:4d} | Distinct Vessels: {len(vessel_reports):3d} | Rate: {rate:4.1f} msg/s | Avg/Vessel: {avg_per_vessel:3.1f}")
                        
    except Exception as e:
        print(f"[-] AISStream Error: {e}")
        return False
        
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("AISStream Validation Summary:")
    print(f"Elapsed Time       : {elapsed:.1f} seconds")
    print(f"Total Messages     : {total_msgs}")
    print(f"Distinct Vessels   : {len(vessel_reports)}")
    print(f"Message Types      : {msg_types}")
    if vessel_reports:
        avg = total_msgs / len(vessel_reports)
        print(f"Average Reports/Vessel: {avg:.2f}")
        top_vessels = sorted(vessel_reports.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Top Active Vessels :")
        for m, count in top_vessels:
            name = vessel_names.get(m, "Unknown")
            print(f"  - MMSI {m} ({name}): {count} reports")
            
    # Phase 0 Gate Check
    if len(vessel_reports) >= 5 and total_msgs >= 20:
        print("\n[SUCCESS] Phase 0 AISStream Gate PASSED!")
        print(f"Coverage is healthy in {bbox_name}.")
        return True
    else:
        print("\n[WARNING] Low vessel count or low reports in this window. Consider testing a busier box (e.g., singapore_strait or english_channel).")
        return False

def main():
    parser = argparse.ArgumentParser(description="AISStream Validation & Recorder")
    parser.add_argument("--key", type=str, default=os.getenv("AIS_API_KEY", ""), help="AISStream API Key")
    parser.add_argument("--bbox", type=str, default="english_channel", choices=list(BOUNDING_BOXES.keys()), help="Bounding box to monitor")
    parser.add_argument("--duration", type=int, default=600, help="Monitoring duration in seconds (default 600 = 10 min)")
    parser.add_argument("--output", type=str, default=f"data/replay/ais_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl", help="Capture file path")
    
    args = parser.parse_args()
    
    if not args.key:
        print("[-] Error: No AISStream API key provided.")
        print("    Please provide --key <YOUR_KEY> or set AIS_API_KEY environment variable.")
        print("    Get a free key in 30 seconds at: https://aisstream.io/")
        sys.exit(1)
        
    success = asyncio.run(run_ais_collector(args.key, args.bbox, args.duration, args.output))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
