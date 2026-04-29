// Chat Persistence and Enhanced Functionality

// Save chat message to database
function saveChatMessage(message, sender) {
    fetch('/api/save-chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message, sender: sender })
    }).catch(err => console.log('Error saving chat:', err));
}

// Load chat history on page load
function loadChatHistory() {
    fetch('/api/chat-history')
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                const messagesContainer = document.getElementById('chatbotMessages');
                if (!messagesContainer) return;

                // Clear welcome message
                messagesContainer.innerHTML = '';

                // Load all messages
                data.messages.forEach(msg => {
                    addMessageToUI(msg.message, msg.sender);
                });
            }
        })
        .catch(err => console.log('Error loading chat history:', err));
}

// Helper function to add message to UI
function addMessageToUI(message, sender) {
    const messagesContainer = document.getElementById('chatbotMessages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');

    if (sender === 'user') {
        messageDiv.style.cssText = 'text-align: right; margin: 1rem 0;';
        messageDiv.innerHTML = `
            <div style="background: var(--gradient-primary); color: white; padding: 0.8rem; border-radius: 15px; display: inline-block; max-width: 80%;">
                ${message}
            </div>
        `;
    } else if (sender === 'bot') {
        messageDiv.style.cssText = 'text-align: left; margin: 1rem 0;';
        messageDiv.innerHTML = `
            <div style="background: white; padding: 0.8rem; border-radius: 15px; display: inline-block; max-width: 80%; box-shadow: var(--shadow-light);">
                ${message}
            </div>
        `;
    } else if (sender === 'error') {
        messageDiv.style.cssText = 'text-align: left; margin: 1rem 0;';
        messageDiv.innerHTML = `
            <div style="background: #fee; color: #c53030; padding: 0.8rem; border-radius: 15px; display: inline-block; max-width: 80%;">
                ${message}
            </div>
        `;
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Override the original sendChatbotMessage function with enhanced version
if (typeof sendChatbotMessage !== 'undefined') {
    const originalSendChatMessage = sendChatbotMessage;
}

function sendChatbotMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();
    if (!message) return;

    const messagesContainer = document.getElementById('chatbotMessages');

    // Add user message
    addMessageToUI(message, 'user');

    // Save user message to database
    saveChatMessage(message, 'user');

    // Clear input
    input.value = '';

    // Add loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.style.cssText = 'text-align: left; margin: 1rem 0;';
    loadingDiv.innerHTML = `
        <div style="background: #f1f1f1; padding: 0.8rem; border-radius: 15px; display: inline-block;">
            <div class="loading"></div>
        </div>
    `;
    messagesContainer.appendChild(loadingDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Send to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: message })
    })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            const loading = document.getElementById('loadingIndicator');
            if (loading && messagesContainer.contains(loading)) {
                messagesContainer.removeChild(loading);
            }

            // Check if response exists
            if (!data || !data.response) {
                console.error('Invalid response from server:', data);
                addMessageToUI('Sorry, I received an invalid response. Please try again.', 'error');
                return;
            }

            // Add bot response
            addMessageToUI(data.response, 'bot');

            // Save bot response to database
            saveChatMessage(data.response, 'bot');

            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            // Check if booking or cancellation and refresh
            if (data.booking_created || data.booking_cancelled) {
                setTimeout(() => {
                    if (typeof loadRecentBookings === 'function') {
                        loadRecentBookings();
                    }
                }, 1000);
            }
        })
        .catch(error => {
            console.error('Chat error:', error);
            const loading = document.getElementById('loadingIndicator');
            if (loading && messagesContainer.contains(loading)) {
                messagesContainer.removeChild(loading);
            }

            // Add error message
            addMessageToUI('Sorry, I encountered an error. Please try again.', 'error');
        });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    // Update logout link to clear chat before logout
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(function (logoutLink) {
        logoutLink.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.href;
            // Clear chat history
            fetch('/api/clear-chat', { method: 'POST' })
                .then(() => {
                    window.location.href = href;
                })
                .catch(() => {
                    window.location.href = href;
                });
        });
    });

    // Load chat history if chatbot exists
    if (document.getElementById('chatbotMessages')) {
        setTimeout(loadChatHistory, 500);  // Small delay to ensure DOM is ready
    }
});
