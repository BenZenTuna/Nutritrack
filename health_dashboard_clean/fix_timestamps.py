import sqlite3

DB_PATH = "/home/taner/.openclaw/workspace/health_dashboard/nutritrack.db"

def fix_timestamps():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Fixing timestamps in food_entries...")
    # Replace space with T
    c.execute("""
        UPDATE food_entries 
        SET logged_at = REPLACE(logged_at, ' ', 'T')
        WHERE logged_at LIKE '% %'
    """)
    
    print("Fixing timestamps in sport_activities...")
    c.execute("""
        UPDATE sport_activities 
        SET performed_at = REPLACE(performed_at, ' ', 'T')
        WHERE performed_at LIKE '% %'
    """)
    
    conn.commit()
    print(f"Updated {c.rowcount} rows.")
    conn.close()

if __name__ == "__main__":
    fix_timestamps()
