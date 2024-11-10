function sendMessage() {
    const userInput = document.getElementById('userInput');
    const messageContainer = document.getElementById('messageContainer');
  
    if (userInput.value.trim()) {
      // Add user message
      const userMessage = document.createElement('div');
      userMessage.classList.add('message', 'user');
      userMessage.textContent = userInput.value;
      messageContainer.appendChild(userMessage);
  
      // Clear input
      userInput.value = '';
  
      // Simulate AI response
      setTimeout(() => {
        const aiMessage = document.createElement('div');
        aiMessage.classList.add('message', 'ai');
        aiMessage.textContent = "I'm here to assist you with your health-related questions. Please provide more details.";
        messageContainer.appendChild(aiMessage);
      }, 1000);
    }
  }
  // JavaScript to open and close the modal
function openModal() {
    document.getElementById('aiHealthModal').style.display = 'flex';
  }
  
  function closeModal() {
    document.getElementById('aiHealthModal').style.display = 'none';
  }
  