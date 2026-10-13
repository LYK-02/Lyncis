"""
OpenSanctions Maritime Ingestion & Indexer (Phase 0 -> Phase 3)
Downloads maritime.csv (4.89 MB), builds SQLite database with indexes on IMO, MMSI, and Name.
"""

import os
import csv
import sqlite3
import time
import requests

DATASET_URL = "https://data.opensanctions.org/artifacts/maritime/20261012150304-jhv/maritime.csv"
LOCAL_CSV = "data/sanctions/maritime.csv"
LOCAL_DB = "data/sanctions/sanctions.db"

def download_file(url: str, dest_path: str):
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    print(f"[*] Downloading OpenSanctions maritime dataset from {url}...")
    headers = {"User-Agent": "Lyncis-OSINT/0.1 (Research/Validation)"}
    
    start = time.time()
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0 and downloaded % (512 * 1024) == 0:
                        percent = (downloaded / total_size) * 100
                        print(f"    Downloaded {downloaded/(1024*1024):.1f} MB / {total_size/(1024*1024):.1f} MB ({percent:.0f}%)", end="\r")
                        
    elapsed = time.time() - start
    print(f"\n[+] Download complete! Saved to {dest_path} ({os.path.getsize(dest_path)/(1024*1024):.2f} MB in {elapsed:.1f}s)")

def build_sqlite_index(csv_path: str, db_path: str):
    print(f"[*] Ingesting CSV into SQLite database at {db_path}...")
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create schema
    cur.execute("""
        CREATE TABLE maritime_entities (
            id TEXT PRIMARY KEY,
            type TEXT,
            caption TEXT,
            caption_lower TEXT,
            imo TEXT,
            mmsi TEXT,
            flag TEXT,
            countries TEXT,
            risk TEXT,
            datasets TEXT,
            url TEXT,
            aliases TEXT
        )
    """)
    
    cur.execute("CREATE INDEX idx_maritime_imo ON maritime_entities(imo);")
    cur.execute("CREATE INDEX idx_maritime_mmsi ON maritime_entities(mmsi);")
    cur.execute("CREATE INDEX idx_maritime_caption_lower ON maritime_entities(caption_lower);")
    
    # Load rows
    start = time.time()
    inserted = 0
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            caption = row.get("caption", "").strip()
            # Normalize IMO (e.g. IMO9427366 -> 9427366 and keep raw)
            imo_raw = row.get("imo", "").strip()
            imo_clean = imo_raw.upper().replace("IMO", "").strip() if imo_raw else ""
            mmsi = row.get("mmsi", "").strip()
            
            batch.append((
                row.get("id", ""),
                row.get("type", "VESSEL"),
                caption,
                caption.lower(),
                imo_clean,
                mmsi,
                row.get("flag", ""),
                row.get("countries", ""),
                row.get("risk", ""),
                row.get("datasets", ""),
                row.get("url", ""),
                row.get("aliases", "")
            ))
            
            if len(batch) >= 2000:
                cur.executemany("""
                    INSERT OR REPLACE INTO maritime_entities 
                    (id, type, caption, caption_lower, imo, mmsi, flag, countries, risk, datasets, url, aliases)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                inserted += len(batch)
                batch = []
                
        if batch:
            cur.executemany("""
                INSERT OR REPLACE INTO maritime_entities 
                (id, type, caption, caption_lower, imo, mmsi, flag, countries, risk, datasets, url, aliases)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            inserted += len(batch)
            
    conn.commit()
    elapsed = time.time() - start
    print(f"[+] Ingested {inserted} maritime records in {elapsed:.2f}s!")
    
    # Verify counts
    cur.execute("SELECT COUNT(*) FROM maritime_entities WHERE imo != '';")
    with_imo = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM maritime_entities WHERE mmsi != '';")
    with_mmsi = cur.fetchone()[0]
    
    print(f"[+] Total records with IMO: {with_imo}")
    print(f"[+] Total records with MMSI: {with_mmsi}")
    
    # Test sample search
    print("\n[*] Testing fast lookup performance:")
    cur.execute("SELECT caption, imo, risk, url FROM maritime_entities WHERE imo != '' LIMIT 1;")
    sample = cur.fetchone()
    if sample:
        test_imo = sample[1]
        t0 = time.time()
        cur.execute("SELECT caption, imo, risk, url FROM maritime_entities WHERE imo = ?;", (test_imo,))
        res = cur.fetchone()
        lookup_time = (time.time() - t0) * 1000
        print(f"    - IMO Lookup '{test_imo}': '{res[0]}' (took {lookup_time:.3f} ms)")
        print(f"    - Risk: {res[2]}")
        print(f"    - Evidence URL: {res[3]}")
        
    conn.close()
    return True

if __name__ == "__main__":
    download_file(DATASET_URL, LOCAL_CSV)
    build_sqlite_index(LOCAL_CSV, LOCAL_DB)
    print("\n[SUCCESS] Phase 0 OpenSanctions Ingestion & Verification Complete!")
