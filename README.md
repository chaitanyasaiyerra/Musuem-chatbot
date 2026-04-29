# 🏛️ MuseumBot - AI-Powered Museum Assistant

A sophisticated web application that combines AI chatbot capabilities with museum ticket booking functionality. Built with Flask, SQLite, and Ollama for local AI processing, MuseumBot provides an intelligent interface for art exploration and seamless ticket management.

## ✨ Features

### 🤖 AI-Powered Chatbot
- **Intelligent Q&A**: Answers questions about artworks, artists, and museum information
- **Natural Language Processing**: Understands conversational queries
- **Local AI Processing**: Uses Ollama with qwen2.5:1.5b model for privacy and speed
- **Smart Date Parsing**: Converts natural language dates ("tomorrow", "next week") to proper format

### 🎫 Ticket Management
- **Seamless Booking**: Book tickets through chat or web form
- **Real-time Updates**: Automatic refresh of booking history
- **Booking Cancellation**: Cancel tickets with booking ID
- **Unique Booking IDs**: 8-character alphanumeric codes (e.g., GLCXMLXT)
- **Date Validation**: Prevents booking for past dates

### 🖼️ Art Navigation
- **Artwork Search**: Find specific paintings and their locations
- **Room Navigation**: Get directions to artwork locations
- **Availability Check**: Verify if artworks are on display
- **Excel Data Integration**: Loads art information from structured data

### 🔐 User Management
- **Secure Authentication**: Bcrypt password hashing
- **User Registration**: Email-based signup system
- **Session Management**: Persistent login sessions
- **User-Specific Bookings**: Private booking history

## 🛠️ Tech Stack

### Backend
- **Flask 3.0+**: Web framework
- **SQLite**: Lightweight database
- **Bcrypt**: Password security
- **Pandas**: Excel data processing
- **OpenPyXL**: Excel file handling

### AI & Tools
- **Ollama**: Local LLM runtime
- **qwen2.5:1.5b**: Lightweight AI model
- **Smolagents**: AI agent framework
- **MCP (Model Context Protocol)**: Tool communication
- **LiteLLM**: Model integration

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Dynamic interactions
- **Bootstrap**: UI components
- **AOS (Animate On Scroll)**: Smooth animations

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
git clone <repository-url>
cd museum-chatbot
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
ollama pull qwen2.5:1.5b
```

### 4. Set Up Python Environment
```bash
# Using UV (recommended)
uv venv
uv pip install -e .

# Or using traditional pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
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
   - Artwork information
   - Ticket booking
   - Booking cancellation

### Chatbot Commands

#### Booking Tickets
```
"book 2 tickets for tomorrow"
"book a ticket for next week"
"book 3 tickets for 2025-12-25"
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
    model_id="ollama_chat/qwen2.5:1.5b",  # Change model here
    num_ctx=2048  # Adjust context window
)
```

## 📁 Project Structure

```
museum-chatbot/
├── app.py                 # Main Flask application
├── server.py             # MCP tool server
├── agent.py              # AI agent configuration
├── app.db                # SQLite database
├── pyproject.toml        # Project dependencies
├── uv.lock              # Dependency lock file
├── templates/            # HTML templates
│   ├── base.html         # Base template with chatbot
│   ├── landing.html      # Homepage
│   ├── login.html        # Login page
│   ├── signup.html       # Registration page
│   └── home.html         # User dashboard
├── venv/                 # Virtual environment
├── Chatbot Question and answers.xlsx    # Q&A database
└── Unique_Museum_Art_Plan.xlsx          # Artwork data
```

### Key Files Explained

- **`app.py`**: Core Flask application with routes, authentication, and chat logic
- **`server.py`**: MCP server providing tools for artwork search and ticket booking
- **`agent.py`**: AI agent setup with Ollama model configuration
- **`templates/`**: HTML templates with responsive design and chatbot integration
- **Excel files**: Data sources for Q&A and artwork information

## 🔧 Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
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

### Testing the AI Model
```bash
# Test Ollama connection
ollama list
ollama run qwen2.5:1.5b "Hello, how are you?"

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
```

**Database Errors**
```bash
# Recreate database
rm app.db
python -c "from app import init_db; init_db()"
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
- **SQL Injection Protection**: Parameterized queries
- **Input Validation**: Server-side validation for all inputs
- **Local AI**: No data sent to external AI services

## 🚀 Deployment

### Production Setup
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up reverse proxy (Nginx, Apache)
3. Configure environment variables
4. Set up database backups
5. Enable HTTPS

### Docker Deployment (TODO)
```dockerfile
# Dockerfile example
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "app:app"]
```

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
- **Bootstrap** for UI components
- **Unsplash** for placeholder images

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Made with ❤️ for the art community** 