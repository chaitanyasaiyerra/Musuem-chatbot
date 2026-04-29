import sqlite3
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel
from mcp import StdioServerParameters
import contextlib
from datetime import datetime, timedelta
import bcrypt
import os
import pandas as pd
import string
import random
import dateparser
import re

# Setup Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# ====== SQLite Setup ======
DB_PATH = "app.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password BLOB NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    # Bookings table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL,
            name TEXT NOT NULL,
            tickets INTEGER NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    # Chat history table
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
    conn.commit()
    conn.close()

init_db()

# ====== Load tools and model ======
model = LiteLLMModel(
    model_id="ollama_chat/llama3.2:latest",  # Changed to llama3.2
    num_ctx=2048
)

server_parameters = StdioServerParameters(
    command="uv", args=["run", "server.py"]
)

tool_collection_ctx = ToolCollection.from_mcp(server_parameters, trust_remote_code=True)
tool_collection = contextlib.ExitStack().enter_context(tool_collection_ctx)

agent = ToolCallingAgent(tools=tool_collection.tools, model=model)

# ====== Load Local Q&A from Excel (Alternating Q/A Format) ======
qa_path = "Chatbot Question and answers.xlsx"
qa_dict = {}
if os.path.exists(qa_path):
    qa_df = pd.read_excel(qa_path)
    col = qa_df.columns[0]
    rows = qa_df[col].dropna().tolist()
    i = 0
    while i < len(rows):
        q = rows[i].strip()
        if q.lower().startswith('q:'):
            # Find the next answer
            if i + 1 < len(rows):
                a = rows[i + 1].strip()
                if a.lower().startswith('a:'):
                    # Normalize question (remove 'q:', lowercase, strip punctuation)
                    norm_q = q[2:].strip().lower().translate(str.maketrans('', '', string.punctuation))
                    qa_dict[norm_q] = a[2:].strip()
                    i += 2
                    continue
        i += 1
    print("[Q&A DEBUG] Loaded questions:")
    for k in qa_dict.keys():
        print(f"  - '{k}'")

# ====== Helper Functions ======
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def parse_natural_date(date_text):
    """
    Enhanced natural language date parser using dateparser library
    Supports: tomorrow, next Monday, DD/MM/YYYY, Month Date Year, etc.
    Returns date in YYYY-MM-DD format or None if not recognized.
    """
    today = datetime.now().date()
    date_text = date_text.lower().strip()
    
    # Try dateparser first for advanced parsing
    try:
        parsed = dateparser.parse(date_text, settings={
            'PREFER_DATES_FROM': 'future',
            'RETURN_AS_TIMEZONE_AWARE': False,
            'RELATIVE_BASE': datetime.now()
        })
        
        if parsed:
            return parsed.strftime('%Y-%m-%d')
    except:
        pass
    
    # Fallback to manual parsing for common patterns
    if date_text in ['tomorrow', 'tmr', 'tmrw']:
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    elif date_text in ['today', 'now']:
        return today.strftime('%Y-%m-%d')
    elif date_text in ['day after tomorrow', 'day after tmrw']:
        return (today + timedelta(days=2)).strftime('%Y-%m-%d')
    elif 'next week' in date_text:
        return (today + timedelta(days=7)).strftime('%Y-%m-%d')
    elif 'next month' in date_text:
        next_month = today.replace(day=1) + timedelta(days=32)
        return next_month.replace(day=1).strftime('%Y-%m-%d')
    elif 'this weekend' in date_text:
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        return (today + timedelta(days=days_until_saturday)).strftime('%Y-%m-%d')
    elif 'next weekend' in date_text:
        days_until_saturday = (5 - today.weekday()) % 7
        return (today + timedelta(days=days_until_saturday + 7)).strftime('%Y-%m-%d')
    
    return None

def update_ticket_statuses():
    """Update ticket statuses based on visit dates"""
    conn = get_db()
    today = datetime.now().date().strftime('%Y-%m-%d')
    
    # Update Active tickets with past dates to Visited
    conn.execute("""
        UPDATE bookings 
        SET status = 'Visited' 
        WHERE status = 'Active' AND date < ?
    """, (today,))
    
    conn.commit()
    conn.close()

def is_logged_in():
    return 'user_id' in session

# ====== Routes ======
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        password = data.get("password")
        conn = get_db()
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()
        if user and check_password(password, user["password"]):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "error")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        conn = get_db()
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            conn.close()
            flash("Email already registered", "error")
            return render_template("signup.html")
        hashed_password = hash_password(password)
        conn.execute(
            "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
            (username, email, hashed_password, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/home")
def home():
    if not is_logged_in():
        return redirect(url_for("login"))
    # Update ticket statuses before showing dashboard
    update_ticket_statuses()
    return render_template("home.html", username=session.get("username"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))

# ====== Chat History Endpoints ======
@app.route("/api/chat-history", methods=["GET"])
def get_chat_history():
    """Load user's chat history"""
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session.get("user_id")
        conn = get_db()
        cur = conn.execute(
            "SELECT message, sender, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC",
            (user_id,)
        )
        messages = cur.fetchall()
        conn.close()
        
        formatted_messages = [{
            "message": msg["message"],
            "sender": msg["sender"],
            "timestamp": msg["timestamp"]
        } for msg in messages]
        
        return jsonify({"messages": formatted_messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/save-chat", methods=["POST"])
def save_chat_message():
    """Save chat message to database"""
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.json
        message = data.get("message")
        sender = data.get("sender")  # 'user' or 'bot'
        user_id = session.get("user_id")
        
        conn = get_db()
        conn.execute(
            "INSERT INTO chat_history (user_id, message, sender, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, message, sender, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clear-chat", methods=["POST"])
def clear_chat_history():
    """Clear chat history (called on logout)"""
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session.get("user_id")
        conn = get_db()
        conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== Chat Endpoint ======
@app.route("/api/chat", methods=["POST"])
def chat():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "Missing query"}), 400
    
    # Normalize for Q&A lookup
    user_q = query.strip().lower().translate(str.maketrans('', '', string.punctuation))
    print(f"[Q&A DEBUG] Normalized user question: '{user_q}'")
    answer = qa_dict.get(user_q)
    print(f"[Q&A DEBUG] Lookup result: {answer}")
    
    if answer:
        return jsonify({"response": answer})
    
    try:
        username = session.get("username")
        user_id = session.get("user_id")
        
        
        # Handle cancel requests FIRST (before booking check)
        # This prevents "Cancel booking XYZ" from triggering booking intent
        if any(word in query.lower() for word in ['cancel', 'cancellation', 'delete']):
            booking_id_match = re.search(r'([A-Z0-9]{8})', query.upper())
            
            if booking_id_match:
                booking_id = booking_id_match.group(1)
                try:
                    conn = get_db()
                    cur = conn.execute(
                        "SELECT * FROM bookings WHERE booking_id = ? AND user_id = ?",
                        (booking_id, user_id)
                    )
                    booking = cur.fetchone()
                    
                    if not booking:
                        return jsonify({"response": f"❌ Booking {booking_id} not found or you don't have permission to cancel it."})
                    
                    # Update status to Cancelled (soft delete)
                    conn.execute(
                        "UPDATE bookings SET status = 'Cancelled', cancelled_at = ? WHERE booking_id = ? AND user_id = ?",
                        (datetime.utcnow().isoformat(), booking_id, user_id)
                    )
                    conn.commit()
                    conn.close()
                    
                    print(f"\n❌ BOOKING CANCELLED (via Chat):")
                    print(f"🆔 Booking ID: {booking_id}")
                    print(f"👤 User: {username}")
                    print(f"⏰ Cancelled: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("-" * 50)
                    
                    return jsonify({"response": f"✅ Booking {booking_id} has been cancelled successfully!", "booking_cancelled": True})
                        
                except Exception as e:
                    return jsonify({"response": f"❌ Error cancelling booking: {str(e)}"})
            else:
                return jsonify({"response": "❌ Please provide the booking ID to cancel (e.g., 'Cancel booking ABC12345')"})
        
        # Handle booking requests with visitor details
        elif any(word in query.lower() for word in ['book', 'ticket', 'reservation', 'booking']):
            # Extract visitor details from query
            response_text = "To book tickets, I need the following details:\n\n"
            response_text += "1. Visitor Name\n2. Age\n3. Gender\n4. Contact Number\n5. Number of Tickets\n6. Visit Date\n\n"
            response_text += "Please provide these details in this format:\n"
            response_text += "\"Book ticket for [Name], age [Age], [Gender], contact [Number], [X] tickets for [Date]\"\n\n"
            response_text += "Example: \"Book ticket for John Smith, age 30, Male, contact 9876543210, 2 tickets for tomorrow\""
            
            # Try to extract all details
            print(f"\n[BOOKING] Attempting to extract booking details from query")
            name_match = re.search(r'for\s+([A-Za-z\s]+),\s*age', query, re.IGNORECASE)
            age_match = re.search(r'age\s+(\d+)', query, re.IGNORECASE)
            gender_match = re.search(r'(male|female|other)', query, re.IGNORECASE)
            contact_match = re.search(r'contact\s+(\d{10})', query, re.IGNORECASE)
            ticket_match = re.search(r'(\d+)\s*tickets?', query.lower())
            # FIX: Match date ONLY after [number] ticket(s) for, not "Book ticket for"
            # This ensures we get "2026-02-16" not "John Doe, age..."
            date_match = re.search(r'(\d+)\s*tickets?\s+for\s+([a-zA-Z0-9\s\-/,]+)$', query, re.IGNORECASE)
            
            print(f"[BOOKING] Extraction results:")
            print(f"  - Name: {'✅ ' + name_match.group(1) if name_match else '❌ Not found'}")
            print(f"  - Age: {'✅ ' + age_match.group(1) if age_match else '❌ Not found'}")
            print(f"  - Gender: {'✅ ' + gender_match.group(1) if gender_match else '❌ Not found'}")
            print(f"  - Contact: {'✅ ' + contact_match.group(1) if contact_match else '❌ Not found'}")
            print(f"  - Tickets: {'✅ ' + ticket_match.group(1) if ticket_match else '❌ Not found'}")
            print(f"  - Date: {'✅ ' + date_match.group(2) if date_match else '❌ Not found'}")  # GROUP 2 now!
            
            if all([name_match, age_match, gender_match, contact_match, ticket_match, date_match]):
                visitor_name = name_match.group(1).strip()
                age = int(age_match.group(1))
                gender = gender_match.group(1).capitalize()
                contact = contact_match.group(1)
                tickets = int(ticket_match.group(1))
                date_text = date_match.group(2).strip()  # FIXED: group 2 contains the date now!
                
                # Parse date
                date = parse_natural_date(date_text)
                if not date:
                    # Try to parse as standard date
                    try:
                        date_obj = datetime.strptime(date_text, "%Y-%m-%d")
                        date = date_text
                    except:
                        return jsonify({"response": f"❌ I couldn't understand the date '{date_text}'. Please use YYYY-MM-DD format or natural language like 'tomorrow', 'next Monday', etc."})
                
                # Validate date
                try:
                    visit_date = datetime.strptime(date, "%Y-%m-%d").date()
                    if visit_date < datetime.today().date():
                        return jsonify({"response": "❌ Cannot book for past dates."})
                except ValueError:
                    return jsonify({"response": f"❌ Invalid date format."})
                
                # Create booking
                booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                
                conn = get_db()
                conn.execute(
                    """INSERT INTO bookings 
                    (booking_id, user_id, name, visitor_name, age, gender, contact, tickets, date, status, created_at) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)""",
                    (booking_id, user_id, username, visitor_name, age, gender, contact, tickets, date, datetime.utcnow().isoformat())
                )
                conn.commit()
                conn.close()
                
                print(f"\n🎫 NEW BOOKING CREATED (via Chat):")
                print(f"🆔 Booking ID: {booking_id}")
                print(f"👤 User: {username}")
                print(f"👤 Visitor: {visitor_name}, Age: {age}, Gender: {gender}")
                print(f"📞 Contact: {contact}")
                print(f"🎟️ Tickets: {tickets}")
                print(f"📅 Date: {date}")
                print("-" * 50)
                
                response = f"""🎉 Booking Confirmed Successfully!<br><br>
📋 Booking Details<br><br>
🆔 Booking ID: {booking_id}<br><br>
👤 Visitor Name: {visitor_name}<br>
👤 Age: {age}<br>
👤 Gender: {gender}<br>
📞 Contact: {contact}<br><br>
🎟️ Number of Tickets: {tickets}<br><br>
📅 Visit Date: {date}<br><br>
🏛️ Your museum visit is now confirmed!<br><br>
⏳ Please arrive 15 minutes before your scheduled time."""
                
                return jsonify({"response": response, "booking_created": True})
            else:
                # Missing some booking details, show instructions
                return jsonify({"response": response_text})
        else:
            # Use agent for non-booking/non-cancel requests
            print(f"\n[AGENT] Query doesn't match booking or cancel pattern, using AI agent...")
            print(f"[AGENT] Query: {query}")
            enhanced_query = f"User {username} asks: {query}"
            response = agent.run(enhanced_query)
            print(f"[AGENT] Response: {response}")
            return jsonify({"response": response})
            
    except Exception as e:
        print(f"\n❌ [ERROR] Exception in /api/chat:")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        print(f"[ERROR] Exception message: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
        # Return error in 'response' field so frontend can display it
        return jsonify({"response": f"⚠️ Error: {str(e)}"}), 500

# ====== Booking Endpoint (Web Form) ======
@app.route("/api/book-ticket", methods=["POST"])
def book_ticket():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    visitor_name = data.get("visitor_name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")
    tickets = data.get("tickets")
    date = data.get("date")
    username = session.get("username")
    user_id = session.get("user_id")
    
    try:
        # Validate date
        visit_date = datetime.strptime(date, "%Y-%m-%d").date()
        if visit_date < datetime.today().date():
            return jsonify({"error": "Cannot book for past dates"}), 400
        
        booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        conn = get_db()
        conn.execute(
            """INSERT INTO bookings 
            (booking_id, user_id, name, visitor_name, age, gender, contact, tickets, date, status, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)""",
            (booking_id, user_id, username, visitor_name, age, gender, contact, tickets, date, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        
        print(f"\n🎫 NEW BOOKING CREATED:")
        print(f"🆔 Booking ID: {booking_id}")
        print(f"👤 User: {username}")
        print(f"👤 Visitor: {visitor_name}, Age: {age}, Gender: {gender}")
        print(f"📞 Contact: {contact}")
        print(f"🎟️ Tickets: {tickets}")
        print(f"📅 Date: {date}")
        print("-" * 50)
        
        response = f"""🎉 Booking Confirmed Successfully!<br><br>
📋 Booking Details<br><br>
🆔 Booking ID: {booking_id}<br><br>
👤 Visitor Name: {visitor_name}<br>
👤 Age: {age}<br>
👤 Gender: {gender}<br>
📞 Contact: {contact}<br><br>
🎟️ Number of Tickets: {tickets}<br><br>
📅 Visit Date: {date}<br><br>
🏛️ Your museum visit is now confirmed!<br><br>
⏳ Please arrive 15 minutes before your scheduled time."""
        
        return jsonify({"response": response, "booking_id": booking_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== Recent Bookings (Dashboard - Active Only) ======
@app.route("/api/recent-bookings", methods=["GET"])
def get_recent_bookings():
    """Get only ACTIVE and UPCOMING bookings for dashboard"""
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session.get("user_id")
        today = datetime.now().date().strftime('%Y-%m-%d')
        
        # Update statuses first
        update_ticket_statuses()
        
        conn = get_db()
        cur = conn.execute(
            """SELECT booking_id, visitor_name, tickets, date, created_at 
            FROM bookings 
            WHERE user_id = ? AND status = 'Active' AND date >= ?
            ORDER BY date ASC 
            LIMIT 10""",
            (user_id, today)
        )
        bookings = cur.fetchall()
        conn.close()
        
        formatted_bookings = []
        for booking in bookings:
            try:
                dt = datetime.fromisoformat(booking["created_at"])
                created_at_str = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                created_at_str = booking["created_at"]
            
            formatted_bookings.append({
                "booking_id": booking["booking_id"],
                "visitor_name": booking["visitor_name"] or "N/A",
                "tickets": booking["tickets"],
                "date": booking["date"],
                "created_at": created_at_str
            })
        
        return jsonify({"bookings": formatted_bookings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== Ticket History (All Statuses) ======
@app.route("/api/ticket-history", methods=["GET"])
def get_ticket_history():
    """Get ALL tickets (all statuses) for user"""
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session.get("user_id")
        
        # Update statuses first
        update_ticket_statuses()
        
        conn = get_db()
        cur = conn.execute(
            """SELECT booking_id, visitor_name, tickets, date, status, created_at, cancelled_at 
            FROM bookings 
            WHERE user_id = ? 
            ORDER BY created_at DESC""",
            (user_id,)
        )
        bookings = cur.fetchall()
        conn.close()
        
        formatted_bookings = []
        for booking in bookings:
            try:
                dt = datetime.fromisoformat(booking["created_at"])
                created_at_str = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                created_at_str = booking["created_at"]
            
            formatted_bookings.append({
                "booking_id": booking["booking_id"],
                "visitor_name": booking["visitor_name"] or "N/A",
                "tickets": booking["tickets"],
                "date": booking["date"],
                "status": booking["status"],
                "created_at": created_at_str,
                "cancelled_at": booking["cancelled_at"]
            })
        
        return jsonify({"bookings": formatted_bookings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== Booking Details ======
@app.route("/api/booking-details/<booking_id>", methods=["GET"])
def get_booking_details(booking_id):
    """Get complete booking details"""
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session.get("user_id")
        conn = get_db()
        cur = conn.execute(
            """SELECT * FROM bookings 
            WHERE booking_id = ? AND user_id = ?""",
            (booking_id, user_id)
        )
        booking = cur.fetchone()
        conn.close()
        
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
        
        try:
            dt = datetime.fromisoformat(booking["created_at"])
            created_at_str = dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            created_at_str = booking["created_at"]
        
        cancelled_at_str = None
        if booking["cancelled_at"]:
            try:
                dt = datetime.fromisoformat(booking["cancelled_at"])
                cancelled_at_str = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                cancelled_at_str = booking["cancelled_at"]
        
        details = {
            "booking_id": booking["booking_id"],
            "visitor_name": booking["visitor_name"] or "N/A",
            "age": booking["age"] or "N/A",
            "gender": booking["gender"] or "N/A",
            "contact": booking["contact"] or "N/A",
            "tickets": booking["tickets"],
            "date": booking["date"],
            "status": booking["status"],
            "created_at": created_at_str,
            "cancelled_at": cancelled_at_str
        }
        
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== Cancel Booking (Updated) ======
@app.route("/api/cancel-booking", methods=["POST"])
def cancel_booking():
    """Cancel booking by updating status (soft delete)"""
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    booking_id = data.get("booking_id")
    user_id = session.get("user_id")
    username = session.get("username")
    
    if not booking_id:
        return jsonify({"error": "Missing booking ID"}), 400
    
    try:
        conn = get_db()
        cur = conn.execute(
            "SELECT * FROM bookings WHERE booking_id = ? AND user_id = ?",
            (booking_id, user_id)
        )
        booking = cur.fetchone()
        
        if not booking:
            return jsonify({"error": "Booking not found or you don't have permission to cancel it"}), 404
        
        # Update status to Cancelled (soft delete)
        conn.execute(
            "UPDATE bookings SET status = 'Cancelled', cancelled_at = ? WHERE booking_id = ? AND user_id = ?",
            (datetime.utcnow().isoformat(), booking_id, user_id)
        )
        conn.commit()
        conn.close()
        
        print(f"\n❌ BOOKING CANCELLED:")
        print(f"🆔 Booking ID: {booking_id}")
        print(f"👤 User: {username}")
        print(f"⏰ Cancelled: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        return jsonify({"response": f"✅ Booking {booking_id} has been cancelled successfully!"})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== Start App ======
if __name__ == "__main__":
    app.run(debug=True, port=5000)
