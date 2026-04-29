# 🏛️ MuseumBot Technical Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [AI Integration](#ai-integration)
7. [API Endpoints](#api-endpoints)
8. [Frontend Architecture](#frontend-architecture)
9. [Security Implementation](#security-implementation)
10. [Performance Considerations](#performance-considerations)
11. [Development Workflow](#development-workflow)

## 🎯 Project Overview   

MuseumBot is a full-stack web application that combines traditional web development with modern AI capabilities. The application serves as an intelligent museum assistant that can handle ticket bookings, answer questions about artworks, and provide navigation assistance.

### Key Technical Decisions

1. **Local AI Processing**: Uses Ollama for privacy and reduced latency
2. **SQLite Database**: Lightweight, file-based database for simplicity
3. **Flask Framework**: Python web framework for rapid development
4. **MCP Protocol**: Standardized tool communication for AI agents
5. **Responsive Design**: Mobile-first approach with Bootstrap

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │   MCP Server    │
│   (Browser)     │◄──►│   (app.py)      │◄──►│   (server.py)   │
│                 │    │                 │    │                 │
│ - HTML/CSS/JS   │    │ - Web Routes    │    │ - Tool Functions│
│ - Bootstrap     │    │ - Auth Logic    │    │ - Art Data      │
│ - Chatbot UI    │    │ - Session Mgmt  │    │ - Booking Logic │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │   (app.db)      │
                       │                 │
                       │ - Users Table   │
                       │ - Bookings Table│
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Ollama        │
                       │   (Local AI)    │
                       │                 │
                       │ - qwen2.5:1.5b  │
                       │ - Model Runtime │
                       └─────────────────┘
```

## 🔧 Core Components

### 1. Flask Application (`app.py`)

**Purpose**: Main web application entry point and request handler

**Key Responsibilities**:
- HTTP route handling
- User authentication and session management
- Database operations
- AI agent coordination
- Natural language date parsing

**Critical Functions**:

```python
# Natural Language Date Parsing
def parse_natural_date(date_text):
    """
    Converts natural language to YYYY-MM-DD format
    Supports: tomorrow, today, next week, this weekend, etc.
    """
    today = datetime.now().date()
    date_text = date_text.lower().strip()
    
    if date_text in ['tomorrow', 'tmr', 'tmrw']:
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    # ... more patterns

# Database Connection
def get_db():
    """Creates and returns SQLite database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Password Security
def hash_password(password):
    """Securely hash passwords using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

### 2. MCP Server (`server.py`)

**Purpose**: Provides tools and functions for the AI agent

**Key Tools**:
- `check_painting_availability()`: Verify artwork presence
- `navigate_to_painting()`: Find artwork locations
- `book_tickets()`: Create ticket bookings
- `cancel_ticket()`: Cancel existing bookings
- `painting_description()`: Get artwork details
- `painting_painter()`: Get artist information

**Tool Implementation Example**:
```python
@mcp.tool()
def book_tickets(visitor_name: str, tickets: int, date: str) -> str:
    """
    Book museum tickets with validation and confirmation
    """
    # Input validation
    if not isinstance(tickets, int) or tickets <= 0:
        return "❌ Number of tickets must be a positive integer."
    
    # Date validation
    try:
        visit_date = datetime.strptime(date, "%Y-%m-%d").date()
        if visit_date < datetime.today().date():
            return "❌ Cannot book for past dates."
    except ValueError:
        return f"❌ Date format should be YYYY-MM-DD. Received: '{date}'"
    
    # Generate unique booking ID
    booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Database insertion
    conn = get_db()
    conn.execute(
        "INSERT INTO bookings (booking_id, name, tickets, date, created_at) VALUES (?, ?, ?, ?, ?)",
        (booking_id, visitor_name, tickets, date, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    
    # Return formatted confirmation
    return f"""🎉 Booking Confirmed Successfully!<br><br>📋 Booking Details<br><br>🆔 Booking ID: {booking_id}<br><br>👤 Visitor Name: {visitor_name}<br><br>🎟️ Number of Tickets: {tickets}<br><br>📅 Visit Date: {date}<br><br>🏛️ Your museum visit is now confirmed!<br><br>⏳ Please arrive 15 minutes before your scheduled time."""
```

### 3. AI Agent (`agent.py`)

**Purpose**: Configures the AI model and tool integration

**Configuration**:
```python
# Lightweight model for better performance
model = LiteLLMModel(
    model_id="ollama_chat/qwen2.5:1.5b",
    num_ctx=2048  # Smaller context window for efficiency
)

# MCP server integration
server_parameters = StdioServerParameters(
    command="uv", args=["run", "server.py"]
)

# Tool collection setup
tool_collection_ctx = ToolCollection.from_mcp(server_parameters, trust_remote_code=True)
agent = ToolCallingAgent(tools=tool_collection.tools, model=model)
```

## 🔄 Data Flow

### 1. User Registration Flow
```
User Input → Form Validation → Password Hashing → Database Insert → Session Creation → Redirect
```

### 2. Chat Request Flow
```
User Message → Route Handler → Q&A Lookup → AI Agent (if needed) → Tool Execution → Response Formatting → JSON Response
```

### 3. Booking Flow
```
Natural Language → Date Parsing → Validation → Database Insert → Confirmation → UI Update
```

### 4. Authentication Flow
```
Login Request → Password Verification → Session Creation → Dashboard Access
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password BLOB NOT NULL,  -- bcrypt hashed
    created_at TEXT NOT NULL
);
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id TEXT NOT NULL,  -- 8-char alphanumeric
    name TEXT NOT NULL,        -- username
    tickets INTEGER NOT NULL,
    date TEXT NOT NULL,        -- YYYY-MM-DD format
    created_at TEXT NOT NULL   -- ISO format
);
```

### Data Relationships
- **One-to-Many**: User → Bookings (via username)
- **Unique Constraints**: email (users), booking_id (bookings)
- **Indexes**: email, booking_id for performance

## 🤖 AI Integration

### Model Selection Rationale
- **qwen2.5:1.5b**: Lightweight model suitable for local deployment
- **Context Window**: 2048 tokens for memory efficiency
- **Tool Calling**: Structured function execution for reliability

### Tool Communication Protocol (MCP)
```python
# Tool definition with type hints
@mcp.tool()
def function_name(param1: str, param2: int) -> str:
    """
    Tool description for AI understanding
    """
    # Implementation
    return "formatted response"
```

### Natural Language Processing
```python
# Question normalization for Q&A lookup
user_q = query.strip().lower().translate(str.maketrans('', '', string.punctuation))
answer = qa_dict.get(user_q)
```

### Date Parsing Intelligence
```python
# Supports multiple natural language patterns
patterns = {
    'tomorrow': lambda: (today + timedelta(days=1)),
    'next week': lambda: (today + timedelta(days=7)),
    'this weekend': lambda: find_next_saturday(),
    # ... more patterns
}
```

## 🌐 API Endpoints

### Authentication Endpoints
- `GET /` - Landing page
- `GET /login` - Login form
- `POST /login` - Authentication
- `GET /signup` - Registration form
- `POST /signup` - User creation
- `GET /logout` - Session termination

### Application Endpoints
- `GET /home` - User dashboard
- `POST /api/chat` - Chatbot interaction
- `POST /api/book-ticket` - Web form booking
- `GET /api/recent-bookings` - User's booking history
- `POST /api/cancel-booking` - Booking cancellation

### API Response Format
```json
{
    "response": "Formatted message with HTML tags",
    "error": "Error message if applicable"
}
```

## 🎨 Frontend Architecture

### Template Structure
```
templates/
├── base.html      # Base template with chatbot
├── landing.html   # Marketing homepage
├── login.html     # Authentication
├── signup.html    # Registration
└── home.html      # User dashboard
```

### Chatbot Integration
```javascript
// Floating chatbot with real-time updates
function sendChatbotMessage() {
    fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: message})
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(data.response);
        if (isBookingOrCancellation(data.response)) {
            setTimeout(refreshBookings, 1500);
        }
    });
}
```

### Responsive Design
- **Mobile-first**: Bootstrap grid system
- **Progressive Enhancement**: Core functionality works without JavaScript
- **Accessibility**: ARIA labels and semantic HTML
- **Performance**: Optimized images and CSS

## 🔒 Security Implementation

### Password Security
```python
# Secure password hashing
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

### Session Management
```python
# Secure session configuration
app.secret_key = os.urandom(24)  # Random secret key
session.permanent = True  # Persistent sessions
```

### Input Validation
```python
# SQL injection prevention
conn.execute("SELECT * FROM users WHERE email = ?", (email,))

# XSS prevention
response = f"🎉 Booking Confirmed!<br><br>🆔 Booking ID: {booking_id}"
```

### Authentication Middleware
```python
def is_logged_in():
    return 'user_id' in session

@app.route("/home")
def home():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("home.html", username=session.get("username"))
```

## ⚡ Performance Considerations

### Database Optimization
- **Connection Pooling**: Reuse database connections
- **Indexed Queries**: Fast lookups on email and booking_id
- **Parameterized Queries**: Prevent SQL injection and improve caching

### AI Model Optimization
- **Lightweight Model**: qwen2.5:1.5b for faster inference
- **Context Window**: Limited to 2048 tokens
- **Tool Caching**: MCP tools cached for repeated use

### Frontend Performance
- **Lazy Loading**: Images and non-critical resources
- **Minified Assets**: Compressed CSS and JavaScript
- **CDN Usage**: External libraries from CDN

### Caching Strategy
```python
# Q&A data loaded once at startup
qa_dict = {}
if os.path.exists(qa_path):
    qa_df = pd.read_excel(qa_path)
    # Process and cache Q&A pairs
```

## 🔄 Development Workflow

### Local Development Setup
```bash
# 1. Environment setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Start Ollama
ollama serve

# 4. Run application
python app.py
```

### Testing Strategy
```python
# Unit tests for core functions
def test_parse_natural_date():
    assert parse_natural_date("tomorrow") == (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

def test_password_hashing():
    password = "test123"
    hashed = hash_password(password)
    assert check_password(password, hashed) == True
```

### Debugging Tools
```python
# Debug logging throughout the application
print(f"DEBUG: Creating booking - ID: {booking_id}, User: {username}")
print(f"DEBUG: Session username: {session.get('username')}")
print(f"DEBUG: Converted '{natural_date}' to '{date}'")
```

### Database Management
```bash
# View database contents
sqlite3 app.db ".tables"
sqlite3 app.db "SELECT * FROM bookings;"

# Reset database
rm app.db
python -c "from app import init_db; init_db()"
```

## 🚀 Deployment Considerations

### Production Requirements
- **WSGI Server**: Gunicorn or uWSGI
- **Reverse Proxy**: Nginx or Apache
- **Process Manager**: systemd or supervisor
- **SSL Certificate**: HTTPS encryption
- **Database Backups**: Automated backup strategy
    
### Environment Configuration
```env
FLASK_ENV=production
FLASK_SECRET_KEY=your-secure-secret-key
DATABASE_URL=sqlite:///app.db
OLLAMA_HOST=http://localhost:11434
```

### Monitoring and Logging
- **Application Logs**: Flask logging configuration
- **Error Tracking**: Sentry or similar service
- **Performance Monitoring**: Application metrics
- **Health Checks**: Endpoint for load balancer

---

This technical guide provides a comprehensive overview of the MuseumBot architecture and implementation details. For specific implementation questions, refer to the inline code comments and documentation. 