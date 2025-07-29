#!/usr/bin/env python3
"""
Migration script to allow NULL values for created_by column in Collection table
This enables collections to be unowned when users leave them.
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
    
    print("Updating collection table to allow NULL values for created_by...")
    
    # SQLite doesn't support modifying column constraints directly
    # We need to recreate the table
    
    # First, get the current table structure
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='collection'")
    create_sql = cursor.fetchone()[0]
    print(f"Current table structure: {create_sql}")
    
    # Create a new temporary table with nullable created_by
    cursor.execute("""
        CREATE TABLE collection_new (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            description TEXT,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_public BOOLEAN DEFAULT 0 NOT NULL,
            FOREIGN KEY(created_by) REFERENCES user (id)
        )
    """)
    
    # Copy data from old table to new table
    cursor.execute("""
        INSERT INTO collection_new (id, name, description, created_by, created_at, is_public)
        SELECT id, name, description, created_by, created_at, is_public 
        FROM collection
    """)
    
    # Drop the old table
    cursor.execute("DROP TABLE collection")
    
    # Rename the new table
    cursor.execute("ALTER TABLE collection_new RENAME TO collection")
    
    # Recreate any indexes that existed
    # (None expected based on the current structure, but this is where you'd add them)
    
    # Commit the changes
    conn.commit()
    print("Successfully updated collection table to allow NULL created_by values")
    
    # Verify the change
    cursor.execute("PRAGMA table_info(collection)")
    columns = cursor.fetchall()
    for col in columns:
        if col[1] == 'created_by':
            print(f"created_by column: nullable={col[3] == 0}")  # notnull flag
    
    # Close the connection
    conn.close()
    
except sqlite3.Error as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close()
    exit(1)

print("Migration completed successfully!")
