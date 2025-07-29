#!/usr/bin/env python3
"""
Migration script to add is_public column to Collection table
"""

import sqlite3
import os

# Get the database path
db_path = os.path.join('instance', 'texture_vault.db')

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    exit(1)

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(collection)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_public' in columns:
        print("is_public column already exists in collection table")
    else:
        print("Adding is_public column to collection table...")
        
        # Add the is_public column with default value False
        cursor.execute("ALTER TABLE collection ADD COLUMN is_public BOOLEAN DEFAULT 0 NOT NULL")
        
        # Commit the changes
        conn.commit()
        print("Successfully added is_public column to collection table")
        print("All existing collections are now set to private (is_public=False)")
    
    # Close the connection
    conn.close()
    
except sqlite3.Error as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.close()
    exit(1)

print("Migration completed successfully!")
