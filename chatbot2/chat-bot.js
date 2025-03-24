// API Integration for existing Chatbot Interface

// Base URL for the API
const API_BASE_URL = 'http://20.197.44.114';

// Store chat history
let chatHistory = [];

// Function to send chat messages to the API
async function sendMessageToAPI(message) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/post`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        query: message
      })
    });

    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending message to API:', error);
    return { error: error.message };
  }
}

// Function to add message to chat UI
function addMessageToChat(message, isUser = false) {
  // First add to history
  chatHistory.push({
    text: message,
    isUser: isUser,
    timestamp: new Date()
  });
  
  // Create message elements
  const chatContainer = document.querySelector('.chat-container') || document.querySelector('.messages-container');
  if (!chatContainer) return;
  
  const messageElement = document.createElement('div');
  messageElement.className = isUser ? 'user-message' : 'bot-message';
  
  const textElement = document.createElement('div');
  textElement.textContent = message;
  
  const timeElement = document.createElement('div');
  const time = new Date();
  timeElement.textContent = `${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')} ${time.getHours() >= 12 ? 'pm' : 'am'}`;
  timeElement.className = 'message-time';
  
  messageElement.appendChild(textElement);
  messageElement.appendChild(timeElement);
  
  chatContainer.appendChild(messageElement);
  
  // Scroll to bottom
  chatContainer.scrollTop = chatContainer.scrollHeight;
  
  // Also update chat history sidebar if it exists
  updateChatHistory();
}

// Update chat history sidebar
function updateChatHistory() {
  const chatHistoryContainer = document.querySelector('.chat-history') || document.getElementById('chat-history');
  if (!chatHistoryContainer) return;
  
  // Clear current history
  chatHistoryContainer.innerHTML = '';
  
  // Add each message to the history
  chatHistory.forEach(message => {
    if (message.isUser) {
      const historyItem = document.createElement('div');
      historyItem.className = 'history-item';
      historyItem.textContent = message.text;
      
      const timeSpan = document.createElement('div');
      const time = new Date(message.timestamp);
      timeSpan.textContent = `${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')} ${time.getHours() >= 12 ? 'pm' : 'am'}`;
      timeSpan.className = 'history-time';
      
      historyItem.appendChild(timeSpan);
      chatHistoryContainer.appendChild(historyItem);
    }
  });
}

// Handle form submission
async function handleSubmit(event) {
  if (event) event.preventDefault();
  
  // Get message input
  const messageInput = document.querySelector('input[type="text"]') || document.getElementById('message-input');
  if (!messageInput) return;
  
  const message = messageInput.value.trim();
  if (!message) return;
  
  // Clear input
  messageInput.value = '';
  
  // Add user message to chat
  addMessageToChat(message, true);
  
  // Show loading indicator if needed
  const sendButton = document.querySelector('button[type="submit"]') || document.querySelector('.send-button');
  if (sendButton) {
    const originalText = sendButton.textContent;
    sendButton.textContent = 'Sending...';
    sendButton.disabled = true;
  }
  
  // Send to API and get response
  try {
    const response = await sendMessageToAPI(message);
    
    if (response.error) {
      addMessageToChat(`Sorry, I encountered an error: ${response.error}`, false);
    } else {
      // Extract the bot response from the API response
      const botResponse = response.response || response.content || response.message || 
                         (response.data ? response.data.response : null) || 
                         "I received your message but couldn't generate a response.";
      
      addMessageToChat(botResponse, false);
    }
  } catch (error) {
    console.error('Error in message handling:', error);
    addMessageToChat('Sorry, there was an error processing your request.', false);
  } finally {
    // Restore button state
    if (sendButton) {
      sendButton.textContent = originalText || 'Send';
      sendButton.disabled = false;
    }
  }
}

// Function to setup the event listeners
function setupChatInterface() {
  // Find the form element
  const form = document.querySelector('form') || document.getElementById('chat-form');
  
  if (form) {
    // Add submit event listener to the form
    form.addEventListener('submit', handleSubmit);
  }
  
  // Find the send button if there's no form
  const sendButton = document.querySelector('.send-button') || document.querySelector('button[type="submit"]');
  if (sendButton && !form) {
    sendButton.addEventListener('click', handleSubmit);
  }
  
  // Add keypress event for enter key
  const messageInput = document.querySelector('input[type="text"]') || document.getElementById('message-input');
  if (messageInput && !form) {
    messageInput.addEventListener('keypress', (event) => {
      if (event.key === 'Enter') {
        handleSubmit();
      }
    });
  }
  
  // Initialize the login/register functionality if needed
  const loginButton = document.querySelector('.login-button') || document.getElementById('login-button');
  if (loginButton) {
    loginButton.addEventListener('click', () => {
      // Handle login logic here
      console.log('Login clicked');
    });
  }
  
  const registerButton = document.querySelector('.register-button') || document.getElementById('register-button');
  if (registerButton) {
    registerButton.addEventListener('click', () => {
      // Handle register logic here
      console.log('Register clicked');
    });
  }
}

// Function for file/document upload if needed
async function uploadDocument(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/documents/upload_and_process_document`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error uploading document:', error);
    return { error: error.message };
  }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('Initializing chat interface with API integration');
  setupChatInterface();
  
  // Add a welcome message if appropriate
  // addMessageToChat('Welcome to Police Assistance Chatbot! How can I help you today?', false);
});