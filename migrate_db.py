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
    
    # Create chat_history table
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
        print("✓ Created chat_history table")
    except Exception as e:
        print(f"✗ Error creating chat_history table: {e}")
    
    # Add new columns to bookings table
    columns_to_add = [
        ('user_id', 'INTEGER'),
        ('visitor_name', 'TEXT'),
        ('age', 'INTEGER'),
        ('gender', 'TEXT'),
        ('contact', 'TEXT'),
        ('status', 'TEXT DEFAULT "Active"'),
        ('cancelled_at', 'TEXT')
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
    
    # Update existing bookings to have default status
    try:
        cur.execute('UPDATE bookings SET status = "Active" WHERE status IS NULL')
        print("✓ Updated existing bookings with default status")
    except Exception as e:
        print(f"✗ Error updating existing bookings: {e}")
    
    # Get user_id mapping from name to users table
    try:
        # First, get all unique names from bookings
        cur.execute('SELECT DISTINCT name FROM bookings WHERE user_id IS NULL')
        names = cur.fetchall()
        
        for (name,) in names:
            # Try to find matching user
            cur.execute('SELECT id FROM users WHERE username = ?', (name,))
            user = cur.fetchone()
            if user:
                cur.execute('UPDATE bookings SET user_id = ? WHERE name = ? AND user_id IS NULL', 
                           (user[0], name))
        print("✓ Updated bookings with user_id mappings")
    except Exception as e:
        print(f"✗ Error mapping user_ids: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("\nNew schema:")
    print("- chat_history table: stores persistent chat messages")
    print("- bookings table enhanced with: visitor_name, age, gender, contact, status, cancelled_at")
    print("\nStatus values: Active, Cancelled, Visited, Expired")

if __name__ == '__main__':
    migrate()
