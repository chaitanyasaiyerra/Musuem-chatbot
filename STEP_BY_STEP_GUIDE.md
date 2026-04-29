# 🏛️ MuseumBot: Step-by-Step Project Explanation

## 🎯 What This Project Does

MuseumBot is an **AI-powered museum assistant** that combines the intelligence of a chatbot with practical ticket booking functionality. Think of it as a smart museum concierge that can:

1. **Answer questions** about artworks, artists, and museum information
2. **Book tickets** through natural conversation (with full visitor details)
3. **Help navigate** the museum by finding specific artworks
4. **Manage bookings** (view, cancel, track history with status lifecycle)

## 🚀 How It Works: Step-by-Step Flow

### **Step 1: User Arrives at the Website**
```
User visits http://localhost:5000
↓
Landing page displays museum information, features, and gallery
↓
User clicks "Get Started" to register
```

**What happens behind the scenes:**
- Flask serves the `landing.html` template (extends `base.html`)
- Custom CSS with CSS Grid, Flexbox, and CSS variables provides responsive styling
- AOS (Animate On Scroll) library triggers smooth scroll animations
- Google Fonts (Poppins + Playfair Display) provide typography
- Font Awesome icons enhance the UI

### **Step 2: User Registration**
```
User fills out registration form (username, email, password)
↓
Form submits to /signup endpoint
↓
Password is securely hashed using bcrypt
↓
User data is stored in SQLite database
↓
User is redirected to login page with success flash message
```

**Technical details:**
```python
# Password security
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Database insertion with parameterized queries (prevents SQL injection)
conn.execute(
    "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
    (username, email, hashed_password, datetime.utcnow().isoformat())
)
```

### **Step 3: User Login**
```
User enters email and password
↓
System looks up user by email in database
↓
bcrypt verifies password against stored hash
↓
If valid, Flask session is created with user_id and username
↓
User is redirected to dashboard (/home)
```

**Security features:**
- Passwords are never stored in plain text
- Sessions use random secret keys (`os.urandom(24)`)
- Failed login attempts show flash error messages

### **Step 4: Dashboard Access**
```
User sees personalized dashboard
↓
Recent active bookings are loaded via AJAX (/api/recent-bookings)
↓
Ticket statuses are auto-updated (past dates → "Visited")
↓
Quick action cards: Chat, Book Tickets, Current Exhibitions
↓
Floating chatbot appears in bottom-right corner
```

**Dashboard features:**
- User-specific booking history (filtered by `user_id`)
- Real-time ticket booking form modal (with visitor details)
- Ticket history modal (shows Active, Cancelled, Visited statuses)
- Booking details modal (full visitor info)
- Exhibitions modal (current exhibitions display)
- Interactive floating chatbot with chat persistence

### **Step 5: Chatbot Interaction**
```
User types message in chatbot
↓
Message is sent to /api/chat endpoint
↓
Message is saved to chat_history table for persistence
↓
System processes the request through a priority pipeline
```

**Message processing pipeline (in order):**
1. **Q&A Lookup**: Normalize question, check against Excel Q&A database (`qa_dict`)
2. **Cancel Detection**: Check for cancel/delete keywords + extract booking ID via regex
3. **Booking Detection**: Check for book/ticket keywords + extract visitor details via regex
4. **AI Processing**: If none of above match, send to Ollama AI agent with MCP tools

### **Step 6: Ticket Booking Process (via Chat)**
```
User says: "Book ticket for John Smith, age 30, Male, contact 9876543210, 2 tickets for tomorrow"
↓
System detects booking intent (keywords: book, ticket, reservation)
↓
Regex extracts: name, age, gender, contact, ticket count, date
↓
dateparser library converts "tomorrow" to actual YYYY-MM-DD date
↓
System validates date (no past dates allowed)
↓
Unique 8-character booking ID is generated (e.g., "GLCXMLXT")
↓
Booking is saved to database with status "Active"
↓
Confirmation message with all details is sent back
↓
Recent bookings section automatically refreshes via AJAX
```

**Regex extraction (from `app.py`):**
```python
name_match = re.search(r'for\s+([A-Za-z\s]+),\s*age', query, re.IGNORECASE)
age_match = re.search(r'age\s+(\d+)', query, re.IGNORECASE)
gender_match = re.search(r'(male|female|other)', query, re.IGNORECASE)
contact_match = re.search(r'contact\s+(\d{10})', query, re.IGNORECASE)
ticket_match = re.search(r'(\d+)\s*tickets?', query.lower())
date_match = re.search(r'(\d+)\s*tickets?\s+for\s+([a-zA-Z0-9\s\-/,]+)$', query, re.IGNORECASE)
```

### **Step 7: Ticket Booking (via Web Form)**
```
User clicks "Book Tickets" on dashboard
↓
Modal opens with form: visitor name, age, gender, contact, tickets, date
↓
Form submits to /api/book-ticket endpoint
↓
Server validates date and creates booking
↓
Confirmation displayed in modal
↓
Bookings list auto-refreshes after 1 second
```

### **Step 8: AI-Powered Responses**
```
User asks: "Where is the Mona Lisa?"
↓
Question not found in Q&A database
↓
Not a booking or cancellation request
↓
Request sent to Ollama AI model (llama3.2:latest)
↓
AI model receives the query via Smolagents ToolCallingAgent
↓
AI decides to call navigate_to_painting("Mona Lisa") MCP tool
↓
Tool searches Unique_Museum_Art_Plan.xlsx for the artwork
↓
Response with floor, section, and room info is formatted and returned
```

**AI integration details:**
- Uses local Ollama server for complete privacy (no data sent externally)
- MCP (Model Context Protocol) for structured tool communication via FastMCP
- `llama3.2:latest` model used in production (`app.py`)
- 6 MCP tools available: check availability, navigate, description, painter info, image, complete info
- Smolagents `ToolCallingAgent` handles tool selection and execution

### **Step 9: Artwork Navigation**
```
User asks: "Tell me about Starry Night"
↓
AI calls get_complete_artwork_info("Starry Night") or painting_description() tool
↓
Tool searches Unique_Museum_Art_Plan.xlsx
↓
Artwork details are retrieved (room, floor, section, description, history, artist)
↓
Formatted response includes all available information
```

**Data sources:**
- `Chatbot Question and answers.xlsx`: Pre-defined Q&A pairs (loaded at startup into `qa_dict`)
- `Unique_Museum_Art_Plan.xlsx`: Artwork information including names, rooms, descriptions, history, artist info

### **Step 10: Booking Cancellation**
```
User says: "cancel booking ABC12345"
↓
System detects cancel intent (keywords: cancel, cancellation, delete)
↓
Regex extracts 8-character booking ID from message
↓
Database is searched for booking matching ID AND user_id
↓
If found and belongs to user:
  → Status updated to "Cancelled" (soft delete)
  → cancelled_at timestamp is recorded
↓
Confirmation message is sent
↓
Recent bookings section updates automatically
```

**Security features:**
- Users can only cancel their own bookings (verified via `user_id`)
- Bookings are **soft deleted** — status changes to "Cancelled", record is preserved
- Database transactions ensure data integrity

### **Step 11: Chat Persistence**
```
Every message sent or received
↓
chat_persistence.js saves message to /api/save-chat
↓
Message stored in chat_history table with user_id, sender, timestamp
↓
On page load, /api/chat-history restores previous messages
↓
On logout, /api/clear-chat clears the user's chat history
```

### **Step 12: Real-time Updates**
```
After any booking or cancellation
↓  
JavaScript detects booking_created or booking_cancelled in response
↓
setTimeout triggers loadRecentBookings() after 1 second
↓
New data is fetched from /api/recent-bookings via AJAX
↓
UI updates without page refresh
↓
User sees immediate feedback
```

**Frontend updates:**
- AJAX calls (fetch API) for seamless experience
- Automatic refresh after booking/cancellation actions
- Loading states with CSS spinner animations
- Responsive card grid updates dynamically

## 🔧 Technical Architecture Breakdown

### **Backend Components**

1. **Flask Application (`app.py`)**
   - Web server and route handler (13 routes)
   - User authentication and sessions
   - Database operations (3 tables)
   - Natural language date parsing (dateparser + manual fallback)
   - Chat history persistence
   - Booking CRUD with status lifecycle

2. **MCP Server (`server.py`)**
   - FastMCP server with 6 artwork tools
   - Excel data loading and searching
   - Stdio transport for communication with Smolagents

3. **AI Agent (`agent.py`)**
   - Standalone Ollama model configuration
   - MCP tool integration setup
   - Used for development/testing

4. **Database Migration (`migrate_db.py`)**
   - Schema evolution script
   - Adds new columns to bookings table
   - Creates chat_history table
   - Maps existing data to new schema

### **Frontend Components**

1. **HTML Templates (Jinja2)**
   - `base.html`: Common layout with navbar, floating chatbot, AOS init
   - `landing.html`: Marketing homepage with hero, features, gallery, about sections
   - `login.html` & `signup.html`: Auth forms with gradient backgrounds
   - `home.html`: Dashboard with quick actions, bookings, 4 modals

2. **JavaScript Functions**
   - `chat_persistence.js`: Chat save/load/clear with database backend
   - Chatbot message handling with loading states
   - Form submissions with AJAX
   - Real-time booking list updates
   - Modal management (open/close/outside-click)

3. **Styling**
   - Custom CSS (no framework) with CSS variables for theming
   - CSS Grid for responsive card layouts
   - Glassmorphism effects (backdrop-filter)
   - Gradient backgrounds and hover animations
   - Mobile-responsive with `@media (max-width: 768px)` breakpoint

### **Data Storage**

1. **SQLite Database (`app.db`)**
   - `users` table: authentication data (id, username, email, bcrypt password)
   - `bookings` table: ticket reservations with visitor details and status lifecycle
   - `chat_history` table: persistent chat messages per user

2. **Excel Files**
   - Q&A database: pre-defined question-answer pairs
   - Art database: artwork names, rooms, floors, sections, descriptions, history, artist info

## 🎨 User Experience Flow

### **First-Time User Journey**
1. **Discovery**: Lands on attractive landing page with hero, features, gallery
2. **Registration**: Simple 3-field signup (username, email, password)
3. **Login**: Quick authentication with flash messages
4. **Dashboard**: Personalized welcome with quick action cards
5. **Chat**: Floating chatbot with natural conversation
6. **Booking**: Book via chat or web form with full visitor details
7. **Confirmation**: Clear booking details with unique ID

### **Returning User Journey**
1. **Login**: Quick authentication
2. **Dashboard**: View active bookings with auto-updated statuses
3. **Chat History**: Previous chat messages restored automatically
4. **Management**: Cancel bookings, view details, check history
5. **Support**: Get help through AI chatbot

## 🔄 Data Flow Examples

### **Booking Flow**
```
User Input: "Book ticket for Alice, age 25, Female, contact 9876543210, 3 tickets for next weekend"
↓
Regex Extraction: name="Alice", age=25, gender="Female", contact="9876543210", tickets=3
↓
Date Parsing: "next weekend" → "2026-05-02" (via dateparser)
↓
Validation: Date is in future ✓
↓
Database: INSERT with booking_id="X7K2M9PL", status="Active"
↓
Response: Formatted confirmation with all details
↓
UI Update: Recent bookings refresh automatically
```

### **Question Flow (Q&A Match)**
```
User Input: "What are your opening hours?"
↓
Normalize: "what are your opening hours" (lowercase, no punctuation)
↓
Q&A Lookup: Check qa_dict → Match Found!
↓
Response: Return pre-defined answer from Excel
```

### **Question Flow (AI Fallback)**
```
User Input: "Where can I find Van Gogh paintings?"
↓
Q&A Lookup: No match found
↓
Not a booking or cancel request
↓
AI Processing: Send to llama3.2 via Smolagents ToolCallingAgent
↓
Tool Calling: AI decides to call navigate_to_painting("Van Gogh")
↓
Data Search: Query Unique_Museum_Art_Plan.xlsx
↓
Response: Return location information (floor, section, room)
```

## 🛡️ Security & Reliability

### **Data Protection**
- Passwords hashed with bcrypt (random salt per password)
- SQL injection prevention with parameterized queries throughout
- Session security with `os.urandom(24)` secret keys
- Booking ownership verification via `user_id`

### **Error Handling**
- Try/catch blocks on all database operations
- Graceful degradation when AI is unavailable
- Input validation on all user inputs (dates, contacts, etc.)
- User-friendly error messages with emoji indicators
- Debug logging with `[Q&A DEBUG]`, `[BOOKING]`, `[AGENT]`, `[ERROR]` prefixes

### **Performance Optimization**
- Q&A data loaded once at startup (O(1) dictionary lookup)
- Art data loaded once at startup in MCP server
- Lightweight AI model for fast local responses
- AJAX updates avoid full page reloads
- CSS animations for perceived performance

## 🎯 Key Features Explained

### **Natural Language Date Parsing**
- Primary: `dateparser` library for advanced parsing (relative dates, multiple formats)
- Fallback: Manual pattern matching for common cases (tomorrow, next week, etc.)
- Prevents booking for past dates
- User-friendly error messages for unrecognized dates

### **Smart Booking System**
- Unique 8-character alphanumeric booking IDs
- Full visitor details: name, age, gender, contact
- Status lifecycle: Active → Visited (auto) / Cancelled (manual)
- Dual booking methods: chat conversation or web form
- Automatic dashboard refresh after actions

### **AI-Powered Assistance**
- Local processing via Ollama for complete privacy
- 6 specialized MCP tools for artwork queries
- Contextual responses based on user queries
- Fallback hierarchy: Q&A → Cancel → Booking → AI

### **Chat Persistence**
- Messages saved to SQLite per user session
- Chat history restored on page load
- Chat cleared on logout
- Both user and bot messages preserved

### **Responsive Design**
- Works on desktop, tablet, and mobile
- CSS Grid with `auto-fit` for fluid card layouts
- Chatbot resizes for mobile (`width: 90%`)
- Touch-friendly interactive elements

---

This step-by-step guide shows how MuseumBot transforms a simple web application into an intelligent, user-friendly museum assistant that combines the best of modern web development with cutting-edge AI technology.