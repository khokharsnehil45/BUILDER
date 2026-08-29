"""
BUILDER Database Engine (SQLite).
Manages venture ideas, business model canvases, pitch decks, financial roadmaps, and go-to-market plans.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path.home() / ".builder_ventures.db"

def init_db(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Business Ventures & Startups
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tagline TEXT,
        industry TEXT NOT NULL,
        target_market TEXT,
        business_model TEXT, -- SaaS, Marketplace, Agency, D2C, B2B
        stage TEXT DEFAULT 'Idea', -- 'Idea', 'Validation', 'MVP', 'Growth', 'Scaling'
        summary TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # 2. Business Plan Modules (Value Prop, Competitors, GTM, Pricing, Risks)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS venture_modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venture_id INTEGER NOT NULL,
        module_type TEXT NOT NULL, -- 'canvas', 'pitch_deck', 'financials', 'gtm', 'tech_stack'
        title TEXT NOT NULL,
        content_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (venture_id) REFERENCES ventures(id) ON DELETE CASCADE
    )
    """)
    
    # Seed default sample venture if empty
    cursor.execute("SELECT COUNT(*) FROM ventures")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO ventures (name, tagline, industry, target_market, business_model, stage, summary, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "CyberDeck AI",
            "Zero-Cloud Developer Productivity & AI Terminal Suite",
            "Developer Tools / SaaS",
            "Software Engineers, Indie Hackers, Privacy Advocates",
            "Freemium SaaS / Open Core",
            "MVP",
            "An offline-first, terminal-native suite of developer productivity tools powered by local LLMs with privacy-first SQLite persistence.",
            now,
            now
        ))
        
    conn.commit()
    conn.close()

# ==========================================
# VENTURE CRUD
# ==========================================

def create_venture(name: str, tagline: str, industry: str, target_market: str, business_model: str = "SaaS", stage: str = "Idea", summary: str = "", db_path: Path = DB_PATH) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO ventures (name, tagline, industry, target_market, business_model, stage, summary, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name.strip(), tagline.strip(), industry.strip(), target_market.strip(), business_model, stage, summary.strip(), now, now))
    vid = cursor.lastrowid
    conn.commit()
    conn.close()
    return vid

def get_ventures(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventures ORDER BY updated_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_venture_by_id(venture_id: int, db_path: Path = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventures WHERE id = ?", (venture_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    res = dict(row)
    
    # Fetch modules
    cursor.execute("SELECT * FROM venture_modules WHERE venture_id = ? ORDER BY id ASC", (venture_id,))
    res["modules"] = [dict(m) for m in cursor.fetchall()]
    conn.close()
    return res

def save_venture_module(venture_id: int, module_type: str, title: str, content: Dict[str, Any], db_path: Path = DB_PATH) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    content_str = json.dumps(content)
    
    # Check if module exists
    cursor.execute("SELECT id FROM venture_modules WHERE venture_id = ? AND module_type = ?", (venture_id, module_type))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE venture_modules SET title = ?, content_json = ?, created_at = ? WHERE id = ?
        """, (title, content_str, now, row[0]))
        mid = row[0]
    else:
        cursor.execute("""
            INSERT INTO venture_modules (venture_id, module_type, title, content_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (venture_id, module_type, title, content_str, now))
        mid = cursor.lastrowid
        
    cursor.execute("UPDATE ventures SET updated_at = ? WHERE id = ?", (now, venture_id))
    conn.commit()
    conn.close()
    return mid

def delete_venture(venture_id: int, db_path: Path = DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventures WHERE id = ?", (venture_id,))
    cursor.execute("DELETE FROM venture_modules WHERE venture_id = ?", (venture_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success
