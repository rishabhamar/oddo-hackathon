from flask import Flask, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import uuid
from datetime import datetime
import logging
import firebase_admin
from firebase_admin import credentials, firestore
import re
from PyPDF2 import PdfReader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='clinicq.log'
)
logger = logging.getLogger('ClinicQ')

# Load environment variables
load_dotenv()

# Define PDFProcessor class
class PDFProcessor:
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            return ""

# Define PDF content function
def get_pdf_content(pdf_directory):
    """Get content from PDFs with validation and logging"""
    pdf_content = ""
    if not os.path.exists(pdf_directory):
        logger.warning(f"PDF directory not found: {pdf_directory}")
        return pdf_content

    processor = PDFProcessor()
    for filename in os.listdir(pdf_directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_directory, filename)
            logger.info(f"Processing PDF: {filename}")
            text = processor.extract_text_from_pdf(pdf_path)
            if text:
                pdf_content += f"\n\nContent from {filename}:\n{text}"
            else:
                logger.warning(f"No content extracted from {filename}")
    
    return pdf_content

# Load PDF content
try:
    PDF_DIRECTORY = "D:/IIT-Gandhinagar/pdfs"
    pdf_knowledge = get_pdf_content(PDF_DIRECTORY)
except Exception as e:
    print(f"Error loading PDFs: {str(e)}")
    pdf_knowledge = ""  # Fallback to empty string if PDF loading fails

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model with configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# system instruction with PDF knowledge
system_instruction = f"""You are Sarah, a ClinicQ healthcare assistant. You have knowledge of both healthcare and government schemes.

# ClinicQ Assistant System Instructions 2.0

## 1. Introduction Protocol
- Use introduction ONLY for first message: "Hello! I'm Sarah, your ClinicQ healthcare assistant. I'm here to help you with medical information and healthcare queries. How are you feeling today?"
- For all follow-up messages: DO NOT repeat the introduction
- If user returns after long pause: Say "Welcome back! How can I help you today?"

## 2. Response Structure
Always follow this pattern:
1. Direct response to query
2. Relevant information
3. Next steps or questions

## 3. Healthcare Services Information
give response in the same languae as user's
### Must Cover:
- Basic medical information
- Medication details
- General health guidance
- Healthcare programs
- Insurance basics
- Hospital services
- Preventive care

### Healthcare Programs & Schemes
When asked about healthcare schemes:
1. Confirm if they want:
   - Government healthcare programs
   - Insurance schemes
   - Hospital programs
   - Wellness programs
2. Provide relevant category information
3. Share reliable sources for more details

Example Response:
"I understand you're interested in healthcare schemes. Would you like information about:
- Government healthcare programs
- Insurance options
- Hospital wellness programs
Please specify your interest so I can guide you better."

## 4. Core Communication Rules
- NO repeated introductions
- ONE clear response per query
- Stay on topic
- Be concise but complete
- Guide users step by step

## 5. Do Not:
- Repeat introduction in every message
- Give circular responses
- Restart conversations unnecessarily
- Leave queries unaddressed
- Provide outdated information

## 6. Response Templates

### For Healthcare Schemes:
I can help you with information about [specific type] healthcare schemes.

Key Points:
1. [Relevant point 1]
2. [Relevant point 2]
3. [Relevant point 3]

For detailed information, you can:
- [Action step 1]
- [Action step 2]

Would you like specific information about any of these aspects?


### For General Queries:
Regarding [topic]:

[Direct answer]

Additional Information:
- [Key point 1]
- [Key point 2]

How else can I assist you with this?


## 7. Navigation Rules
- Keep track of conversation context
- Reference previous queries when relevant
- Guide users to specific information
- Provide clear next steps
- Offer relevant alternatives

## 8. Quality Checks
Before sending response, verify:
- No repeated introductions
- Direct answer provided
- Clear next steps
- Relevant to user's query
- Professional tone maintained

## 9. Error Recovery
If conversation goes off track:
- Acknowledge the deviation
- Redirect to relevant information
- Clarify user's needs
- Provide correct information
- Ask specific follow-up questions

## 10. Continuous Flow
- Maintain conversation continuity
- Reference previous information when relevant
- Build on established context
- Progress logically through topics
- Avoid circular discussions    

Government Schemes Knowledge:
{pdf_knowledge}

For Government Scheme Queries (When user mentions: scheme, yojana, government programs, healthcare schemes):
- Provide detailed scheme information from the knowledge base
- Structure information as:
  * Scheme Name and Overview
  * Eligibility Criteria
  * Benefits
  * Application Process
  * Required Documents
  * Where to Apply
- Include relevant state-specific information if available
- Mention official websites or helpline numbers if available

Remember: Your role is to provide clear, accurate healthcare information efficiently, without unnecessary repetition or confusion. You are from India, so your responses should be India-centric and understand most of the Indian language.

## 11. Appointment Booking Protocol
When user wants to book an appointment:
1. Collect required information in this order:
   - Patient name
   - Phone number
   - Email
   - Preferred doctor (if any)
   - Preferred date and time
   - Hospital choice (if not specified, use default)
2. Validate each piece of information
3. Confirm all details before booking
4. Provide booking confirmation and reference number

Example appointment dialogue:
"I'll help you book an appointment. Please provide:
1. Patient's full name
2. Contact number
3. Email address
4. Preferred doctor (optional)
5. Preferred date and time
6. Hospital preference (optional)"

and ask the user if they want to confirm the appointment if they say yes and you have all the requird data then book the appointment and provide the reference number. and if not ask for the missing data and then confirm the appointment. by asking should i confirm and show the details. if user says yes confirm, yes, i want to book or anything similar to yes then book them othherwise can
"""

# Initialize model with system instruction
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

app = Flask(__name__)
CORS(app)

# Initialize Firebase
try:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Firebase initialization error: {str(e)}")
    raise

chat_histories = {}

# Add a new class to manage appointment data
class AppointmentManager:
    def __init__(self):
        self.pending_appointments = {}

    def store_pending_appointment(self, session_id, data):
        print(f"Storing appointment data for session {session_id}: {data}")  # Debug log
        self.pending_appointments[session_id] = data

    def get_pending_appointment(self, session_id):
        data = self.pending_appointments.get(session_id)
        print(f"Retrieved appointment data for session {session_id}: {data}")  # Debug log
        return data

# Initialize the appointment manager
appointment_manager = AppointmentManager()

def parse_appointment_text(text):
    """Parse appointment details from any format"""
    appointment_data = {
        'name': None,
        'phone': None,
        'email': None,
        'appointment_date': None,
        'appointment_time': None
    }

    # Handle structured format
    if "Patient's full name:" in text:
        return process_structured_format(text)
    
    # Handle unstructured format
    text = text.lower()
    
    # Extract name
    name_match = re.search(r'name(?:\s+is)?\s*[:]?\s*([a-zA-Z\s]+)', text)
    if name_match:
        appointment_data['name'] = name_match.group(1).strip()

    # Extract phone
    phone_match = re.search(r'(?:contact|phone|number)(?:\s+is)?\s*[:]?\s*(\d+)', text)
    if phone_match:
        appointment_data['phone'] = phone_match.group(1).strip()

    # Extract email
    email_match = re.search(r'email(?:\s+is)?\s*[:]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    if email_match:
        appointment_data['email'] = email_match.group(1).strip()

    # Extract date
    date_match = re.search(r'(?:on|date)?\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december))', text)
    if date_match:
        appointment_data['appointment_date'] = date_match.group(1).strip()

    # Extract time
    time_match = re.search(r'(?:at|time)?\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))', text)
    if time_match:
        appointment_data['appointment_time'] = time_match.group(1).strip()

    return appointment_data

def process_structured_format(text):
    """Process structured appointment text format"""
    appointment_data = {
        'name': None,
        'phone': None,
        'email': None,
        'appointment_date': None,
        'appointment_time': None
    }
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if 'name' in key:
                appointment_data['name'] = value
            elif 'contact' in key or 'phone' in key:
                appointment_data['phone'] = re.sub(r'\D', '', value)
            elif 'email' in key:
                appointment_data['email'] = value
            elif 'date' in key:
                appointment_data['appointment_date'] = value
            elif 'time' in key:
                appointment_data['appointment_time'] = value
                
    return appointment_data

def handle_normal_chat(user_input, session_id):
    """Handle regular chat interactions"""
    try:
        # Get chat history or create new
        chat = chat_histories.get(session_id, [])
        
        # Add user message to history
        chat.append({
            "role": "user",
            "content": user_input
        })
        
        # Generate response using the model
        response = model.generate_content(user_input)
        
        # Add bot response to history
        chat.append({
            "role": "bot",
            "content": response.text
        })
        
        # Update chat history
        chat_histories[session_id] = chat
        
        return jsonify({
            "session_id": session_id,
            "response": response.text
        })
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({
            "error": "Failed to generate response",
            "session_id": session_id
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get("input", "").strip()
        session_id = data.get("session_id", str(uuid.uuid4()))

        print(f"\n=== Chat Request ===")
        print(f"Session ID: {session_id}")
        print(f"User Input: {user_input}")

        # Check for appointment-related keywords
        if any(keyword in user_input.lower() for keyword in ['name is', 'appointment']):
            appointment_data = parse_appointment_text(user_input)
            
            # Validate appointment data
            if all(appointment_data.values()):
                # Store in global appointment manager
                appointment_manager.store_pending_appointment(session_id, appointment_data)
                
                # Also store in Firebase for backup
                doc_ref = db.collection("pending_appointments").document(session_id)
                doc_ref.set(appointment_data)
                
                return jsonify({
                    "session_id": session_id,
                    "response": f"""Please confirm these appointment details:
- Name: {appointment_data['name']}
- Phone: {appointment_data['phone']}
- Email: {appointment_data['email']}
- Date: {appointment_data['appointment_date']}
- Time: {appointment_data['appointment_time']}

Type 'yes' to confirm the appointment."""
                })

        # Handle confirmation
        elif user_input.lower() in ['yes', 'confirm', 'correct']:
            # Try to get from memory first
            appointment_data = appointment_manager.get_pending_appointment(session_id)
            
            # If not in memory, try to get from Firebase
            if not appointment_data:
                doc_ref = db.collection("pending_appointments").document(session_id)
                doc = doc_ref.get()
                if doc.exists:
                    appointment_data = doc.to_dict()

            if appointment_data:
                booking_id = str(uuid.uuid4())[:8]
                
                final_appointment = {
                    'booking_id': booking_id,
                    'name': appointment_data['name'],
                    'phone': appointment_data['phone'],
                    'email': appointment_data['email'],
                    'appointment_date': appointment_data['appointment_date'],
                    'appointment_time': appointment_data['appointment_time'],
                    'status': 'confirmed',
                    'created_at': datetime.now().isoformat()
                }

                # Save confirmed appointment
                doc_ref = db.collection("appointments").document(session_id)
                doc_ref.set(final_appointment)
                
                # Clean up pending appointment
                db.collection("pending_appointments").document(session_id).delete()
                if session_id in appointment_manager.pending_appointments:
                    del appointment_manager.pending_appointments[session_id]
                
                return jsonify({
                    "session_id": session_id,
                    "response": f"""Booking ID: {booking_id}
Appointment confirmed for {appointment_data['name']} on {appointment_data['appointment_date']} at {appointment_data['appointment_time']}."""
                })
            else:
                return jsonify({
                    "session_id": session_id,
                    "response": "I couldn't find your appointment details. Please provide them again."
                })

        # Default to normal chat
        return handle_normal_chat(user_input, session_id)

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        print(f"Session ID: {session_id}")
        print(f"Appointment data: {appointment_manager.pending_appointments.get(session_id)}")
        return jsonify({
            "error": "An error occurred processing your request",
            "details": str(e)
        }), 500

# Add a test route
@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        "message": "Server is running",
        "status": "OK"
    })

def save_to_firebase(session_id, appointment_info):
    """Save appointment info to Firebase with better error handling"""
    try:
        print(f"\nSaving to Firebase - Session: {session_id}")
        print(f"Data: {appointment_info}")
        
        # Validate data before saving
        required_fields = ['name', 'phone', 'email', 'appointment_date', 'appointment_time']
        for field in required_fields:
            if not appointment_info.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Save to Firebase
        doc_ref = db.collection("appointments").document(session_id)
        doc_ref.set(appointment_info, merge=True)
        
        # Verify save was successful
        saved_data = doc_ref.get().to_dict()
        if not saved_data:
            raise Exception("Data not saved properly")
            
        print("Successfully saved to Firebase")
        return True
        
    except Exception as e:
        print(f"Firebase save error: {str(e)}")
        return False

def get_from_firebase(session_id):
    """Get appointment info from Firebase"""
    try:
        print(f"\nRetrieving from Firebase - Session: {session_id}")
        doc = db.collection("appointments").document(session_id).get()
        data = doc.to_dict() if doc.exists else {}
        print(f"Retrieved data: {data}")
        return data
    except Exception as e:
        print(f"Firebase get error: {str(e)}")
        return {}  # Return empty dict on error

if __name__ == '__main__':
    app.run(debug=True, port=5000)