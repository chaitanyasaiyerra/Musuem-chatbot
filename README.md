# 🏛️ MuseumBot - AI-Powered Museum Assistant

A sophisticated web application that combines AI chatbot capabilities with museum ticket booking functionality. Built with Flask, SQLite, and Ollama for local AI processing, MuseumBot provides an intelligent interface for art exploration and seamless ticket management.

📚 **Read the full documentation:**
- [Step-by-Step Guide](STEP_BY_STEP_GUIDE.md) — How the application works from a user's perspective
- [Technical Guide](TECHNICAL_GUIDE.md) — Deep dive into the architecture, data flow, and components

## ✨ Features

### 🤖 AI-Powered Chatbot
- **Intelligent Q&A**: Answers questions about artworks, artists, and museum information
- **Natural Language Processing**: Understands conversational queries
- **Local AI Processing**: Uses Ollama with llama3.2 model for privacy and speed
- **Smart Date Parsing**: Converts natural language dates ("tomorrow", "next week") to proper format using `dateparser`
- **MCP Tool Integration**: AI agent uses MCP tools for artwork search, navigation, and information retrieval

### 🎫 Ticket Management
- **Seamless Booking**: Book tickets through chat or web form with visitor details (name, age, gender, contact)
- **Real-time Updates**: Automatic refresh of booking history
- **Booking Cancellation**: Cancel tickets with booking ID (soft delete with status tracking)
- **Unique Booking IDs**: 8-character alphanumeric codes (e.g., GLCXMLXT)
- **Date Validation**: Prevents booking for past dates
- **Ticket Status Tracking**: Active, Visited, and Cancelled statuses with automatic updates
- **Ticket History**: View all past bookings with full status history

### 🖼️ Art Navigation
- **Artwork Search**: Find specific paintings and their locations
- **Room Navigation**: Get step-by-step directions to artwork locations (floor, section, room)
- **Availability Check**: Verify if artworks are on display
- **Complete Artwork Info**: Get description, history, and artist information
- **Excel Data Integration**: Loads art information from structured data

### 🔐 User Management
- **Secure Authentication**: Bcrypt password hashing
- **User Registration**: Email-based signup system
- **Session Management**: Persistent login sessions
- **User-Specific Bookings**: Private booking history
- **Chat Persistence**: Chat history saved per user in database

## 🛠️ Tech Stack

### Backend
- **Flask 3.0+**: Web framework
- **SQLite**: Lightweight database
- **Bcrypt**: Password security
- **Pandas**: Excel data processing
- **OpenPyXL**: Excel file handling
- **Dateparser**: Natural language date parsing

### AI & Tools
- **Ollama**: Local LLM runtime
- **llama3.2:latest**: AI model (used in main app)
- **qwen2.5:1.5b**: Lightweight AI model (used in standalone agent)
- **Smolagents**: AI agent framework with tool-calling capabilities
- **MCP (Model Context Protocol)**: Tool communication via FastMCP server
- **LiteLLM**: Model integration layer
- **ChromaDB**: Vector database for embeddings

### Frontend
- **HTML5/CSS3**: Modern responsive design with custom styling
- **JavaScript**: Dynamic interactions and chat persistence
- **Font Awesome**: Icon library
- **AOS (Animate On Scroll)**: Smooth scroll animations
- **Google Fonts**: Poppins & Playfair Display typography

### Development
- **Python 3.12+**: Runtime environment
- **UV**: Fast Python package manager
- **Virtual Environment**: Isolated dependencies

## 📋 Prerequisites

- **Python 3.12 or higher**
- **Ollama** installed and running locally
- **UV** package manager (recommended) or pip
- **Git** for version control

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/chaitanyasaiyerra/Musuem-chatbot.git
cd Musuem-chatbot
```

### 2. Install Ollama
```bash
# Windows (using winget)
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

### 3. Download AI Model
```bash
ollama pull llama3.2:latest
```

### 4. Set Up Python Environment
```bash
# Using UV (recommended)
uv venv
uv pip install -e .

# Or using traditional pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask bcrypt pandas openpyxl dateparser smolagents[litellm,mcp] mcp[cli] chromadb colorama
```

### 5. Prepare Data Files
Ensure these Excel files are in the project root:
- `Chatbot Question and answers.xlsx` - Q&A database
- `Unique_Museum_Art_Plan.xlsx` - Artwork information

### 6. Initialize Database
The database will be created automatically on first run, but you can manually initialize:
```bash
python -c "from app import init_db; init_db()"
```

## 🎯 Usage

### Starting the Application
```bash
# Start Ollama (in a separate terminal)
ollama serve

# Start the Flask application
python app.py
```

The application will be available at `http://localhost:5000`

### Basic Workflow

1. **Landing Page**: Visit the homepage to learn about features
2. **Registration**: Create an account with email and password
3. **Login**: Access your personalized dashboard
4. **Chat Interface**: Use the floating chatbot for:
   - General museum questions
   - Artwork information & navigation
   - Ticket booking with visitor details
   - Booking cancellation

### Chatbot Commands

#### Booking Tickets
```
"Book ticket for John Smith, age 30, Male, contact 9876543210, 2 tickets for tomorrow"
"Book ticket for Jane Doe, age 25, Female, contact 8765432109, 1 ticket for next Monday"
"Book ticket for Alex, age 28, Male, contact 7654321098, 3 tickets for 2026-12-25"
```

#### Cancelling Tickets
```
"cancel booking ABC12345"
"delete my booking XYZ98765"
```
  
#### Artwork Queries
```
"where is the Mona Lisa?"
"is Starry Night available?"
"tell me about The Scream"
```

#### General Questions
```
"what are your opening hours?"
"how much do tickets cost?"
"what exhibitions are currently running?"
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file for production settings:
```env
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///app.db
OLLAMA_HOST=http://localhost:11434
```

### Database Configuration
The application uses SQLite by default. For production, consider:
- PostgreSQL for better concurrency
- Database backups and migrations
- Connection pooling

### AI Model Configuration
Modify `app.py` to change the Ollama model:
```python
model = LiteLLMModel(
    model_id="ollama_chat/llama3.2:latest",  # Change model here
    num_ctx=2048  # Adjust context window
)
```

## 📁 Project Structure

```
Musuem-chatbot/
├── app.py                              # Main Flask application (routes, auth, chat logic)
├── server.py                           # MCP tool server (artwork search, navigation, info)
├── agent.py                            # Standalone AI agent configuration
├── pyproject.toml                      # Project dependencies and metadata
├── run.bat                             # Windows startup script
├── migrate_db.py                       # Database migration utility
├── show_db.py                          # Database viewer utility
├── analyze_ppt.py                      # PPT analysis script
├── extract_pdf_script.py               # PDF extraction script
├── database_view.html                  # HTML database viewer
├── templates/                          # HTML templates (Jinja2)
│   ├── base.html                       # Base template with navbar & floating chatbot
│   ├── landing.html                    # Homepage / landing page
│   ├── login.html                      # Login page
│   ├── signup.html                     # Registration page
│   └── home.html                       # User dashboard with bookings
├── static/                             # Static assets
│   └── chat_persistence.js             # Chat history persistence script
├── Chatbot Question and answers.xlsx   # Q&A database
├── Unique_Museum_Art_Plan.xlsx         # Artwork data
├── README.md                           # This file
├── STEP_BY_STEP_GUIDE.md              # Setup guide
├── TECHNICAL_GUIDE.md                  # Technical documentation
└── .gitignore                          # Git ignore rules
```

### Key Files Explained

- **`app.py`**: Core Flask application with routes, authentication, chat logic, booking management, and AI agent integration
- **`server.py`**: MCP server providing 6 tools — painting availability, navigation, description, painter info, artwork image, and complete artwork info
- **`agent.py`**: Standalone AI agent setup with Ollama model configuration (uses qwen2.5:1.5b)
- **`templates/`**: Jinja2 HTML templates with custom CSS, responsive design, and floating chatbot integration
- **`static/chat_persistence.js`**: Handles saving/loading chat history to the database per user session
- **Excel files**: Data sources for Q&A pairs and artwork information

## 🔧 Development

### Running in Development Mode
```bash
# Windows
set FLASK_ENV=development
set FLASK_DEBUG=1
python app.py

# Linux/macOS
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
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
rm app.db    # Linux/macOS
python -c "from app import init_db; init_db()"
```

### Testing the AI Model
```bash
# Test Ollama connection
ollama list
ollama run llama3.2:latest "Hello, how are you?"

# Test MCP server
uv run server.py
```

## 🐛 Troubleshooting

### Common Issues

**Ollama Connection Error**
```bash
# Ensure Ollama is running
ollama serve

# Check model availability
ollama list

# Pull the model if missing
ollama pull llama3.2:latest
```

**Database Errors**
```bash
# Recreate database
del app.db   # Windows
python -c "from app import init_db; init_db()"

# Run migrations if schema changed
python migrate_db.py
```

**Import Errors**
```bash
# Reinstall dependencies
uv pip install -e .
```

**Port Already in Use**
```bash
# Change port in app.py
app.run(host='0.0.0.0', port=5001, debug=True)
```

## 🔒 Security Considerations

- **Password Hashing**: Uses bcrypt for secure password storage
- **Session Security**: Flask sessions with random secret keys
- **SQL Injection Protection**: Parameterized queries throughout
- **Input Validation**: Server-side validation for all inputs
- **Local AI**: No data sent to external AI services — all processing happens locally via Ollama
- **Soft Deletes**: Bookings are cancelled via status update, not deleted

## 🚀 Deployment

### Production Setup
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up reverse proxy (Nginx, Apache)
3. Configure environment variables
4. Set up database backups
5. Enable HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to functions
- Include error handling
- Test thoroughly before submitting

## 📝 TODO

- [ ] Add comprehensive test suite
- [ ] Implement Docker containerization
- [ ] Add API documentation
- [ ] Create admin dashboard
- [ ] Add email notifications
- [ ] Implement payment integration
- [ ] Add multi-language support
- [ ] Create mobile app version

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for local AI processing
- **Flask** for the web framework
- **Smolagents** by HuggingFace for the AI agent framework
- **MCP (Model Context Protocol)** for tool communication
- **Font Awesome** for icons
- **AOS** for scroll animations

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Made with ❤️ for the art community**