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
document.getElementById("schedule-btn").onclick = function() {
  window.location.href = "schedule-appointment.html"; // Redirect to the new page
}

document.getElementsByClassName("close")[0].onclick = function() {
    document.getElementById("appointment-modal").style.display = "none";
}

document.getElementById("appointment-form").onsubmit = function(event) {
  event.preventDefault(); // Prevent form submission
  var messageDiv = document.getElementById("message");
    
  // Simulate a successful booking
  messageDiv.innerHTML = "Appointment booked successfully!";
  messageDiv.style.color = "green";

  // Reset form fields
  this.reset();
}
// Listen for the form submission
document.getElementById('appointment-form').addEventListener('submit', function(event) {
  event.preventDefault();  // Prevent the form from submitting the traditional way

  // Get form values
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const date = document.getElementById('date').value;
  const time = document.getElementById('time').value;

  // Hide the appointment form section
  document.getElementById('appointment-section').style.display = 'none';

  // Show the confirmation section
  document.getElementById('confirmation-section').style.display = 'block';

  // Populate the confirmation message with the form data
  document.getElementById('confirmation-name').textContent = name;
  document.getElementById('confirmation-date').textContent = date;
  document.getElementById('confirmation-time').textContent = time;

  // Optionally, you can send the data to your server here via AJAX or Fetch API if needed.
});
