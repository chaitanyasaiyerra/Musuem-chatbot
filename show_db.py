import sqlite3
import pandas as pd

conn = sqlite3.connect('app.db')

print("=" * 80)
print("MUSEUM CHATBOT - DATABASE STRUCTURE")
print("=" * 80)

# Show all tables
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"\n📊 Database Tables: {', '.join(tables)}\n")

# Users Table
print("=" * 80)
print("TABLE 1: USERS")
print("=" * 80)
df_users = pd.read_sql_query('''
    SELECT id as "ID", 
           username as "Username", 
           created_at as "Created At" 
    FROM users 
    LIMIT 10
''', conn)
print(df_users.to_string(index=False))

# Bookings Table
print("\n" + "=" * 80)
print("TABLE 2: BOOKINGS")
print("=" * 80)
df_bookings = pd.read_sql_query('''
    SELECT booking_id as "Booking ID", 
           visitor_name as "Visitor Name", 
           age as "Age",
           gender as "Gender",
           tickets as "Tickets", 
           date as "Visit Date", 
           status as "Status"
    FROM bookings 
    LIMIT 10
''', conn)
print(df_bookings.to_string(index=False))

# Chat Persistence Table (if exists)
if 'chats' in tables or 'chat_history' in tables:
    chat_table = 'chats' if 'chats' in tables else 'chat_history'
    print("\n" + "=" * 80)
    print(f"TABLE 3: {chat_table.upper()}")
    print("=" * 80)
    df_chats = pd.read_sql_query(f'''
        SELECT * FROM {chat_table} LIMIT 10
    ''', conn)
    print(df_chats.to_string(index=False))

# Database Statistics
print("\n" + "=" * 80)
print("DATABASE STATISTICS")
print("=" * 80)
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM bookings")
booking_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Active'")
active_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'")
cancelled_count = cursor.fetchone()[0]

print(f"👥 Total Users: {user_count}")
print(f"🎫 Total Bookings: {booking_count}")
print(f"✅ Active Bookings: {active_count}")
print(f"❌ Cancelled Bookings: {cancelled_count}")

conn.close()
print("\n" + "=" * 80)
