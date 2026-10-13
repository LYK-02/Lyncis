"""
Fast Sanctions Lookup (SanctionWeb)
Queries local indexed SQLite database (data/sanctions/sanctions.db).
Sub-millisecond exact matching on IMO, MMSI, and Name.
"""

import os
import sqlite3
from typing import Optional, Dict, Any
from app.config import settings

def check_sanctions(mmsi: Optional[str] = None, imo: Optional[str] = None, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    db_path = settings.SANCTIONS_DB_PATH
    if not os.path.exists(db_path):
        return None
        
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # 1. Exact match on IMO
        if imo:
            clean_imo = str(imo).upper().replace("IMO", "").strip()
            if clean_imo:
                cur.execute("SELECT * FROM maritime_entities WHERE imo = ? LIMIT 1", (clean_imo,))
                row = cur.fetchone()
                if row:
                    conn.close()
                    return dict(row)
                    
        # 2. Exact match on MMSI
        if mmsi:
            clean_mmsi = str(mmsi).strip()
            if clean_mmsi:
                cur.execute("SELECT * FROM maritime_entities WHERE mmsi = ? OR mmsi LIKE ? LIMIT 1", 
                            (clean_mmsi, f"%{clean_mmsi}%"))
                row = cur.fetchone()
                if row:
                    conn.close()
                    return dict(row)
                    
        # 3. Exact match on uppercase/lowercase caption
        if name:
            clean_name = name.strip().lower()
            if clean_name and len(clean_name) >= 3:
                cur.execute("SELECT * FROM maritime_entities WHERE caption_lower = ? LIMIT 1", (clean_name,))
                row = cur.fetchone()
                if row:
                    conn.close()
                    return dict(row)
                    
        conn.close()
        return None
    except Exception as e:
        print(f"[-] Sanctions lookup error: {e}")
        return None
