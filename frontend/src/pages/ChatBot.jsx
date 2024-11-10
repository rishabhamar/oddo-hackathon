import React, { useState } from 'react';
import "../assets/chat.css"

function ChatBot() {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your AI Health Assistant. How can I help you today?", sender: 'ai' },
  ]);
  const [userInput, setUserInput] = useState('');

  // Function to handle user input and send the message
  async function sendMessage() {
    if (!userInput.trim()) return;

    // Add user message to messages state
    const newUserMessage = { text: userInput, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);

    // Clear the input field
    setUserInput('');

    try {
      // Send POST request to Flask server
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput }),
      });

      const data = await response.json();

      if (response.ok) {
        // Add AI response to messages state
        const newAIMessage = { text: data.response, sender: 'ai' };
        setMessages((prevMessages) => [...prevMessages, newAIMessage]);
      } else {
        console.error('Error:', data.error);
      }
    } catch (error) {
      console.error('Error connecting to server:', error);
    }
  }

  return (
    <>
      <main className="main">
        <div className="card">
          <div className="card-header">
            <h1><span className="icon">☀️</span> AI Health Assistant</h1>
            <p>Your personal guide to natural health and wellness</p>
          </div>
          <div className="card-content">
            <div className="message-container" id="messageContainer">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.sender}`}
                >
                  {message.text}
                </div>
              ))}
            </div>
            <div className="input-container">
              <input
                type="text"
                id="userInput"
                placeholder="Type your health-related question..."
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              />
              <button onClick={sendMessage}>Send</button>
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>&copy; 2024 ClinicQ. All rights reserved.</p>
        <p className="disclaimer">
          Disclaimer: This AI Health Assistant is for informational purposes only and should not be considered medical advice. Always consult with a qualified healthcare professional for medical concerns.
        </p>
      </footer>
    </>
  );
}

export default ChatBot;
