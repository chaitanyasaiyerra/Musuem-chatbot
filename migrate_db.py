"""
migrate_db.py — Database Migration Utility
-------------------------------------------
Run this if you have an existing app.db from a previous version
that is missing the newer columns (user_id, visitor_name, age,
gender, contact, status, cancelled_at).

Usage:
    python migrate_db.py
    # or
    uv run migrate_db.py
"""

import sqlite3
from datetime import datetime


def migrate():
    """
    Database migration script to add new features:
    1. Add chat_history table for persistent chat
    2. Update bookings table with visitor details and status lifecycle
    """
    conn = sqlite3.connect('app.db')
    cur = conn.cursor()

    print("Starting database migration...")

    # ---- chat_history table ----
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                sender TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("✓ Created / verified chat_history table")
    except Exception as e:
        print(f"✗ Error creating chat_history table: {e}")

    # ---- Add new columns to bookings table (safe: each wrapped individually) ----
    columns_to_add = [
        ('user_id',      'INTEGER'),
        ('visitor_name', 'TEXT'),
        ('age',          'INTEGER'),
        ('gender',       'TEXT'),
        ('contact',      'TEXT'),
        ('status',       'TEXT DEFAULT "Active"'),
        ('cancelled_at', 'TEXT'),
    ]

    for column_name, column_type in columns_to_add:
        try:
            cur.execute(f'ALTER TABLE bookings ADD COLUMN {column_name} {column_type}')
            print(f"✓ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"⊙ Column already exists: {column_name}")
            else:
                print(f"✗ Error adding column {column_name}: {e}")

    # ---- Default status for legacy bookings ----
    try:
        cur.execute('UPDATE bookings SET status = "Active" WHERE status IS NULL')
        print("✓ Updated existing bookings with default status")
    except Exception as e:
        print(f"✗ Error updating existing bookings: {e}")

    # ---- Map user_id from username for legacy rows ----
    try:
        cur.execute('SELECT DISTINCT name FROM bookings WHERE user_id IS NULL')
        names = cur.fetchall()

        for (name,) in names:
            cur.execute('SELECT id FROM users WHERE username = ?', (name,))
            user = cur.fetchone()
            if user:
                cur.execute(
                    'UPDATE bookings SET user_id = ? WHERE name = ? AND user_id IS NULL',
                    (user[0], name)
                )
        print("✓ Updated bookings with user_id mappings")
    except Exception as e:
        print(f"✗ Error mapping user_ids: {e}")

    conn.commit()
    conn.close()

    print("\n✅ Migration completed successfully!")
    print("\nCurrent schema:")
    print("  users        — id, username, email, password, created_at")
    print("  bookings     — id, booking_id, user_id, name, visitor_name, age, gender,")
    print("                 contact, tickets, date, status, created_at, cancelled_at")
    print("  chat_history — id, user_id, message, sender, timestamp")
    print("\nBooking status values: Active, Cancelled, Visited")


if __name__ == '__main__':
    migrate()
