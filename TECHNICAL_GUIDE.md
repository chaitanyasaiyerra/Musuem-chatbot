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
5. **Custom CSS Design**: Hand-crafted responsive design with CSS Grid, Flexbox, and CSS variables

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │   MCP Server    │
│   (Browser)     │◄──►│   (app.py)      │◄──►│   (server.py)   │
│                 │    │                 │    │                 │
│ - HTML/CSS/JS   │    │ - Web Routes    │    │ - Art Search    │
│ - Custom CSS    │    │ - Auth Logic    │    │ - Navigation    │
│ - Chatbot UI    │    │ - Booking Logic │    │ - Art Info      │
│ - Chat Persist  │    │ - Session Mgmt  │    │ - Descriptions  │
└─────────────────┘    │ - Chat History  │    └─────────────────┘
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │   (app.db)      │
                       │                 │
                       │ - Users Table   │
                       │ - Bookings Table│
                       │ - Chat History  │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Ollama        │
                       │   (Local AI)    │
                       │                 │
                       │ - llama3.2      │
                       │ - Model Runtime │
                       └─────────────────┘
```

## 🔧 Core Components

### 1. Flask Application (`app.py`)

**Purpose**: Main web application entry point and request handler

**Key Responsibilities**:
- HTTP route handling
- User authentication and session management
- Database operations (users, bookings, chat history)
- AI agent coordination via Smolagents
- Natural language date parsing using `dateparser`
- Ticket booking & cancellation logic
- Chat history persistence

**Critical Functions**:

```python
# Natural Language Date Parsing (using dateparser library)
def parse_natural_date(date_text):
    """
    Converts natural language to YYYY-MM-DD format
    Uses dateparser library first, then falls back to manual patterns.
    Supports: tomorrow, today, next week, this weekend, etc.
    """
    today = datetime.now().date()
    date_text = date_text.lower().strip()
    
    # Try dateparser first for advanced parsing
    parsed = dateparser.parse(date_text, settings={
        'PREFER_DATES_FROM': 'future',
        'RETURN_AS_TIMEZONE_AWARE': False,
        'RELATIVE_BASE': datetime.now()
    })
    if parsed:
        return parsed.strftime('%Y-%m-%d')
    
    # Fallback to manual patterns
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

**Purpose**: Provides artwork-related tools for the AI agent via FastMCP

**Key Tools** (6 tools):
- `check_painting_availability()`: Verify if an artwork is in the museum collection
- `navigate_to_painting()`: Get step-by-step directions including floor, section, and room
- `painting_description()`: Get detailed description and history of an artwork
- `painting_painter()`: Get information about the artist
- `get_artwork_image()`: Get image URL for an artwork
- `get_complete_artwork_info()`: Get comprehensive information (location + description + history + artist)

**Tool Implementation Example**:
```python
@mcp.tool()
def navigate_to_painting(painting_name: str) -> str:
    """
    Get detailed navigation to an artwork including room, floor, and section.
    Provides step-by-step directions to locate the artwork.
    """
    match = art_df[art_df['art_name'].str.lower() == painting_name.strip().lower()]
    if not match.empty:
        room = match.iloc[0]['room_number']
        floor = match.iloc[0].get('floor_number', 'Ground Floor')
        section = match.iloc[0].get('section_name', 'Main Gallery')
        
        navigation = f"""🖼️ Navigation to '{painting_name}':

📍 Location Details:
• Floor: {floor}
• Section: {section}
• Room: {room}

🚶 Directions:
Take the main stairs to {floor}, proceed to the {section} area, 
and look for Room {room}."""
        
        return navigation
    return f"❌ Unable to find location for '{painting_name}'."
```

> **Note**: Booking and cancellation logic is handled directly in `app.py`, NOT through MCP tools. The MCP server is exclusively for artwork-related queries.

### 3. AI Agent (`agent.py`)

**Purpose**: Standalone AI agent configuration for testing/development

**Configuration**:
```python
# Standalone agent uses qwen2.5:1.5b
model = LiteLLMModel(
    model_id="ollama_chat/qwen2.5:1.5b",
    num_ctx=2048  # Smaller context window for efficiency
)

# MCP server integration
server_parameters = StdioServerParameters(
    command="uv", args=["run", "server.py"]
)

# Tool collection setup
with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
    agent = ToolCallingAgent(tools=tool_collection.tools, model=model)
```

> **Note**: The main application (`app.py`) uses `llama3.2:latest` while `agent.py` uses `qwen2.5:1.5b`. The `app.py` agent is the one used in production.

## 🔄 Data Flow

### 1. User Registration Flow
```
User Input → Form Validation → Password Hashing (bcrypt) → Database Insert → Flash Message → Redirect to Login
```

### 2. Chat Request Flow
```
User Message → Route Handler → Q&A Excel Lookup → Cancel Detection → Booking Detection → AI Agent (fallback) → Tool Execution → Response Formatting → JSON Response
```

### 3. Booking Flow (via Chat)
```
Natural Language → Regex Extraction (name, age, gender, contact, tickets, date) → Date Parsing → Validation → Database Insert → Confirmation → Dashboard Auto-Refresh
```

### 4. Booking Flow (via Web Form)
```
Form Submission → Server Validation → Date Check → Database Insert → JSON Response → UI Update
```

### 5. Authentication Flow
```
Login Request → Email Lookup → bcrypt Password Verification → Session Creation → Dashboard Access
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password BLOB NOT NULL,  -- bcrypt hashed
    created_at TEXT NOT NULL  -- ISO format
);
```

### Bookings Table (Enhanced)
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id TEXT NOT NULL,      -- 8-char alphanumeric (e.g., "GLCXMLXT")
    user_id INTEGER,               -- FK to users.id
    name TEXT NOT NULL,             -- username who booked
    visitor_name TEXT,              -- actual visitor name
    age INTEGER,                   -- visitor age
    gender TEXT,                   -- Male/Female/Other
    contact TEXT,                  -- 10-digit phone number
    tickets INTEGER NOT NULL,
    date TEXT NOT NULL,             -- YYYY-MM-DD format
    status TEXT DEFAULT 'Active',  -- Active/Cancelled/Visited
    created_at TEXT NOT NULL,      -- ISO format
    cancelled_at TEXT              -- ISO format, set on cancellation
);
```

### Chat History Table
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    sender TEXT NOT NULL,        -- 'user' or 'bot'
    timestamp TEXT NOT NULL,     -- ISO format
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Data Relationships
- **One-to-Many**: User → Bookings (via `user_id`)
- **One-to-Many**: User → Chat History (via `user_id`)
- **Unique Constraints**: email (users), booking_id (bookings)

## 🤖 AI Integration

### Model Selection

| Component | Model | Purpose |
|-----------|-------|---------|
| `app.py` (main app) | `llama3.2:latest` | Production chatbot responses |
| `agent.py` (standalone) | `qwen2.5:1.5b` | Development/testing |

- **Context Window**: 2048 tokens for memory efficiency
- **Tool Calling**: Structured function execution via Smolagents `ToolCallingAgent`

### Tool Communication Protocol (MCP)
```python
# Tool definition with type hints and docstrings
@mcp.tool()
def function_name(param1: str) -> str:
    """
    Tool description for AI understanding.
    The AI reads this docstring to decide when to use the tool.
    """
    # Implementation
    return "formatted response"
```

### Chat Processing Pipeline
```python
# 1. Normalize question for Q&A lookup
user_q = query.strip().lower().translate(str.maketrans('', '', string.punctuation))
answer = qa_dict.get(user_q)

# 2. If Q&A match found → return immediately
if answer:
    return jsonify({"response": answer})

# 3. Check for cancel intent → handle cancellation
# 4. Check for booking intent → extract visitor details via regex
# 5. Fallback → send to AI agent with MCP tools
```

### Natural Language Date Parsing
```python
# Uses dateparser library as primary parser
parsed = dateparser.parse(date_text, settings={
    'PREFER_DATES_FROM': 'future',
    'RETURN_AS_TIMEZONE_AWARE': False
})

# Falls back to manual patterns for common cases
patterns = {
    'tomorrow': lambda: (today + timedelta(days=1)),
    'next week': lambda: (today + timedelta(days=7)),
    'this weekend': lambda: find_next_saturday(),
    'next month': lambda: first_of_next_month(),
}
```

## 🌐 API Endpoints

### Authentication Endpoints
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/` | Landing page |
| GET/POST | `/login` | Login form & authentication |
| GET/POST | `/signup` | Registration form & user creation |
| GET | `/logout` | Session termination |
| GET | `/home` | User dashboard (auth required) |

### Chat Endpoints
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/chat` | Chatbot interaction (Q&A, booking, cancel, AI) |
| GET | `/api/chat-history` | Load user's chat history |
| POST | `/api/save-chat` | Save a chat message to database |
| POST | `/api/clear-chat` | Clear chat history (on logout) |

### Booking Endpoints
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/book-ticket` | Web form ticket booking |
| GET | `/api/recent-bookings` | Active upcoming bookings for dashboard |
| GET | `/api/ticket-history` | All bookings (all statuses) |
| GET | `/api/booking-details/<id>` | Complete details for a specific booking |
| POST | `/api/cancel-booking` | Cancel a booking (soft delete) |

### API Response Format
```json
{
    "response": "Formatted message with HTML tags",
    "booking_created": true,
    "booking_cancelled": true,
    "error": "Error message if applicable"
}
```

## 🎨 Frontend Architecture

### Template Structure (Jinja2)
```
templates/
├── base.html      # Base layout: navbar, floating chatbot, AOS init, chat persistence
├── landing.html   # Marketing homepage with hero, features, gallery, about, CTA
├── login.html     # Login form with gradient background
├── signup.html    # Registration form with gradient background
└── home.html      # User dashboard: quick actions, bookings, modals (ticket, history, details, exhibitions)
```

### Styling Approach
- **No CSS framework** — fully custom CSS using CSS variables, CSS Grid, and Flexbox
- **CSS Variables** for theming: `--primary-color`, `--secondary-color`, `--gradient-primary`, etc.
- **Google Fonts**: Poppins (body) + Playfair Display (headings)
- **Font Awesome 6.4**: Icons throughout the UI
- **AOS Library**: Scroll-triggered animations

### Chatbot Integration
```javascript
// Floating chatbot with real-time updates and persistence
function sendChatbotMessage() {
    // 1. Add user message to UI
    addMessageToUI(message, 'user');
    // 2. Save user message to database
    saveChatMessage(message, 'user');
    // 3. Show loading indicator
    // 4. POST to /api/chat
    fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: message})
    })
    .then(response => response.json())
    .then(data => {
        addMessageToUI(data.response, 'bot');
        saveChatMessage(data.response, 'bot');
        // Auto-refresh bookings on booking/cancellation
        if (data.booking_created || data.booking_cancelled) {
            setTimeout(() => loadRecentBookings(), 1000);
        }
    });
}
```

### Dashboard Modals
The home page includes 4 modals:
1. **Ticket Booking Modal** — form with visitor details (name, age, gender, contact, tickets, date)
2. **Exhibitions Modal** — current exhibitions display
3. **Ticket History Modal** — all bookings with status badges (Active/Cancelled/Visited)
4. **Booking Details Modal** — complete details for a single booking

### Responsive Design
- **Custom CSS Grid**: `repeat(auto-fit, minmax(300px, 1fr))` for responsive card layouts
- **Mobile breakpoint**: `@media (max-width: 768px)` for navigation collapse and chatbot sizing
- **Glassmorphism**: `backdrop-filter: blur(10px)` on navbar and about section
- **Micro-animations**: `@keyframes fadeInUp`, `@keyframes pulse`, `@keyframes spin`

## 🔒 Security Implementation

### Password Security
```python
# Secure password hashing with bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

### Session Management
```python
# Random secret key generated at startup
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
```

### Input Validation
```python
# SQL injection prevention — parameterized queries throughout
conn.execute("SELECT * FROM users WHERE email = ?", (email,))

# Booking ownership validation
cur = conn.execute(
    "SELECT * FROM bookings WHERE booking_id = ? AND user_id = ?",
    (booking_id, user_id)
)
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

### Soft Deletes
- Bookings are **never deleted** from the database
- Cancellation updates `status` to `'Cancelled'` and sets `cancelled_at` timestamp
- Users can only cancel their own bookings (verified via `user_id`)

## ⚡ Performance Considerations

### Database Optimization
- **Row Factory**: `sqlite3.Row` for efficient dict-like access
- **Parameterized Queries**: Prevent SQL injection and improve query caching
- **Status Auto-Update**: `update_ticket_statuses()` marks past-date bookings as "Visited"

### AI Model Optimization
- **Lightweight Model**: `llama3.2` for fast local inference
- **Context Window**: Limited to 2048 tokens for memory efficiency
- **MCP Tool Caching**: Tool collection initialized once at startup
- **Q&A Shortcircuit**: Excel-based Q&A lookup runs before AI, saving inference time

### Frontend Performance
- **CDN Assets**: Font Awesome, Google Fonts, AOS loaded from CDN
- **Lazy Loading**: AOS provides scroll-triggered rendering
- **AJAX Updates**: Bookings refresh without full page reload
- **Minimal JS**: No heavy framework — vanilla JavaScript only

### Caching Strategy
```python
# Q&A data and art data loaded ONCE at startup, cached in memory
qa_dict = {}
if os.path.exists(qa_path):
    qa_df = pd.read_excel(qa_path)
    # Process and cache Q&A pairs in a dict for O(1) lookup

# Art data loaded once in server.py
art_df = pd.read_excel("Unique_Museum_Art_Plan.xlsx")
```

## 🔄 Development Workflow

### Local Development Setup
```bash
# 1. Environment setup
uv venv
uv pip install -e .

# 2. Start Ollama
ollama serve

# 3. Pull the model
ollama pull llama3.2:latest

# 4. Run application
python app.py
```

### Database Migration
```bash
# Run migration script to add new columns/tables
python migrate_db.py
```

The migration script (`migrate_db.py`) handles:
- Creating `chat_history` table
- Adding `visitor_name`, `age`, `gender`, `contact`, `status`, `cancelled_at` columns to bookings
- Mapping existing bookings to user IDs

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
print(f"[Q&A DEBUG] Normalized user question: '{user_q}'")
print(f"[BOOKING] Extraction results:")
print(f"  - Name: {'✅ ' + name if name else '❌ Not found'}")
print(f"[AGENT] Query: {query}")
```

### Database Management
```bash
# View database contents
python show_db.py

# Or using sqlite3 directly
sqlite3 app.db ".tables"
sqlite3 app.db "SELECT * FROM bookings;"

# Reset database
del app.db   # Windows
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