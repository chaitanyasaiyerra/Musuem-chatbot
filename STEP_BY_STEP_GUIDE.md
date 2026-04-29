# 🏛️ MuseumBot: Step-by-Step Project Explanation

## 🎯 What This Project Does

MuseumBot is an **AI-powered museum assistant** that combines the intelligence of a chatbot with practical ticket booking functionality. Think of it as a smart museum concierge that can:

1. **Answer questions** about artworks, artists, and museum information
2. **Book tickets** through natural conversation
3. **Help navigate** the museum by finding specific artworks
4. **Manage bookings** (view, cancel, track history)
## 🚀 How It Works: Step-by-Step Flow

### **Step 1: User Arrives at the Website**
```
User visits http://localhost:5000
↓
Landing page displays museum information and features
↓
User clicks "Get Started" to register
```

**What happens behind the scenes:**
- Flask serves the `landing.html` template
- Static assets (CSS, JS, images) are loaded
- Responsive design adapts to user's device

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
User is redirected to login page
```

**Technical details:**
```python
# Password security
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Database insertion
conn.execute(
    "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
    (username, email, hashed_password, datetime.utcnow().isoformat())
)
```

### **Step 3: User Login**
```
User enters email and password
↓
System verifies credentials against database
↓
If valid, Flask session is created
↓
User is redirected to dashboard (/home)
```

**Security features:**
- Passwords are never stored in plain text
- Sessions use random secret keys
- Failed login attempts are logged

### **Step 4: Dashboard Access**
```
User sees personalized dashboard
↓
Recent bookings are loaded from database
↓
Ticket booking form is available
↓
Floating chatbot appears in bottom-right corner
```

**Dashboard features:**
- User-specific booking history
- Real-time booking form
- Interactive chatbot interface
- Responsive design for all devices

### **Step 5: Chatbot Interaction**
```
User types message in chatbot
↓
Message is sent to /api/chat endpoint
↓
System processes the request
```

**Message processing flow:**
1. **Q&A Lookup**: Check if question exists in Excel database
2. **Booking Detection**: Check if user wants to book tickets
3. **Cancellation Detection**: Check if user wants to cancel
4. **AI Processing**: If none of above, send to Ollama AI

### **Step 6: Ticket Booking Process**
```
User says: "book 2 tickets for tomorrow"
↓
System detects booking intent
↓
Natural language date parsing converts "tomorrow" to actual date
↓
System validates date (no past dates allowed)
↓
Unique booking ID is generated (e.g., "GLCXMLXT")
↓
Booking is saved to database
↓
Confirmation message is formatted and sent back
↓
Recent bookings section automatically updates
```

**Natural language date parsing:**
```python
def parse_natural_date(date_text):
    if date_text in ['tomorrow', 'tmr', 'tmrw']:
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    elif date_text in ['next week']:
        return (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    # ... more patterns
```

### **Step 7: AI-Powered Responses**
```
User asks: "Where is the Mona Lisa?"
↓
Question not found in Q&A database
↓
Request sent to Ollama AI model (qwen2.5:1.5b)
↓
AI model calls appropriate MCP tool
↓
Tool searches Excel art database
↓
Response is formatted and returned
```

**AI integration details:**
- Uses local Ollama server for privacy
- MCP (Model Context Protocol) for tool communication
- Lightweight model (1.5B parameters) for speed
- Structured tool calling for reliable responses

### **Step 8: Artwork Navigation**
```
User asks: "Tell me about Starry Night"
↓
AI calls painting_description tool
↓
Tool searches Unique_Museum_Art_Plan.xlsx
↓
Artwork details are retrieved
↓
Formatted response includes location, artist, description
```

**Data sources:**
- `Chatbot Question and answers.xlsx`: Pre-defined Q&A pairs
- `Unique_Museum_Art_Plan.xlsx`: Artwork information and locations

### **Step 9: Booking Cancellation**
```
User says: "cancel booking ABC12345"
↓
System extracts booking ID using regex
↓
Database is searched for user's booking
↓
If found and belongs to user, booking is deleted
↓
Confirmation message is sent
↓
Recent bookings section updates automatically
```

**Security features:**
- Users can only cancel their own bookings
- Booking ID validation prevents unauthorized access
- Database transactions ensure data integrity

### **Step 10: Real-time Updates**
```
After any booking or cancellation
↓  
JavaScript automatically calls refreshBookings()
↓
New data is fetched from /api/recent-bookings
↓
UI updates without page refresh
↓
User sees immediate feedback
```

**Frontend updates:**
- AJAX calls for seamless experience
- Automatic refresh after actions
- Loading states and error handling
- Responsive design updates

## 🔧 Technical Architecture Breakdown

### **Backend Components**

1. **Flask Application (`app.py`)**
   - Web server and route handler
   - User authentication and sessions
   - Database operations
   - Natural language processing

2. **MCP Server (`server.py`)**
   - Tool functions for AI agent
   - Artwork search and booking logic
   - Database interactions for tools

3. **AI Agent (`agent.py`)**
   - Ollama model configuration
   - Tool integration setup
   - AI response generation

### **Frontend Components**

1. **HTML Templates**
   - `landing.html`: Marketing homepage
   - `login.html` & `signup.html`: Authentication
   - `home.html`: User dashboard
   - `base.html`: Common layout with chatbot

2. **JavaScript Functions**
   - Chatbot message handling
   - Form submissions and validation
   - Real-time UI updates
   - Error handling and user feedback

### **Data Storage**

1. **SQLite Database (`app.db`)**
   - Users table: authentication data
   - Bookings table: ticket reservations

2. **Excel Files**
   - Q&A database: pre-defined questions and answers
   - Art database: artwork information and locations

## 🎨 User Experience Flow

### **First-Time User Journey**
1. **Discovery**: Lands on attractive homepage
2. **Registration**: Simple signup process
3. **Onboarding**: Immediate access to chatbot
4. **Interaction**: Natural conversation for booking
5. **Confirmation**: Clear booking details and next steps

### **Returning User Journey**
1. **Login**: Quick authentication
2. **Dashboard**: View booking history
3. **New Booking**: Easy ticket booking
4. **Management**: Cancel or modify bookings
5. **Support**: Get help through chatbot

## 🔄 Data Flow Examples

### **Booking Flow**
```
User Input: "book 3 tickets for next weekend"
↓
Date Parsing: "next weekend" → "2025-01-18"
↓
Validation: Date is in future ✓
↓
Database: Insert booking record
↓
Response: Formatted confirmation with booking ID
↓
UI Update: Recent bookings refresh automatically
```

### **Question Flow**
```
User Input: "What are your opening hours?"
↓
Q&A Lookup: Check Excel database
↓
Match Found: Return pre-defined answer
↓
Response: Display formatted answer
```

### **AI Question Flow**
```
User Input: "Where can I find Van Gogh paintings?"
↓
Q&A Lookup: No match found
↓
AI Processing: Send to Ollama model
↓
Tool Calling: navigate_to_painting("Van Gogh")
↓
Data Search: Query art database
↓
Response: Return location information
```

## 🛡️ Security & Reliability

### **Data Protection**
- Passwords hashed with bcrypt
- SQL injection prevention with parameterized queries
- XSS protection with proper output encoding
- Session security with random keys

### **Error Handling**
- Graceful degradation when AI is unavailable
- Input validation on all user inputs
- Database transaction rollback on errors
- User-friendly error messages

### **Performance Optimization**
- Lightweight AI model for fast responses
- Database indexing for quick queries
- Cached Q&A data loaded at startup
- Efficient frontend updates

## 🎯 Key Features Explained

### **Natural Language Date Parsing**
- Converts "tomorrow" → actual date
- Supports multiple formats and variations
- Prevents booking for past dates
- User-friendly error messages

### **Smart Booking System**
- Unique 8-character booking IDs
- Real-time availability checking
- Automatic booking history updates
- Secure cancellation process

### **AI-Powered Assistance**
- Local processing for privacy
- Contextual responses based on user queries
- Tool integration for specific actions
- Fallback to pre-defined Q&A

### **Responsive Design**
- Works on desktop, tablet, and mobile
- Touch-friendly interface
- Fast loading times
- Accessible design patterns

This step-by-step guide shows how MuseumBot transforms a simple web application into an intelligent, user-friendly museum assistant that combines the best of modern web development with cutting-edge AI technology. 