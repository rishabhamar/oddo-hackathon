from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from dotenv import load_dotenv
import os
import logging
import google.generativeai as genai
import requests
from urllib.request import urlopen


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
USER_PHONE_NUMBER = os.getenv('USER_PHONE_NUMBER')
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL')  # Add this to your .env file
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

# Validate environment variables
required_env_vars = [
    'TWILIO_ACCOUNT_SID', 
    'TWILIO_AUTH_TOKEN', 
    'TWILIO_PHONE_NUMBER', 
    'USER_PHONE_NUMBER',
    'WEBHOOK_BASE_URL',
    'HUGGINGFACE_API_KEY'
]


for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def gemini():
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
    4. Give response in the same language as users when possible

    ## 3. Healthcare Services Information

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

    return model

@app.route("/initiate-call", methods=['GET','POST'])
def initiate():
    """Initiate an outbound call to the user"""
    try:
        call = client.calls.create(
            to=USER_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url=f'{WEBHOOK_BASE_URL}/voice'
        )
        logger.info(f"Call initiated with SID: {call.sid}")
        return {"message": "Call initiated successfully", "call_sid": call.sid}, 200
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        return {"error": "Failed to initiate call"}, 500

@app.route("/voice", methods=['POST'])
def voice():
    """Handle incoming voice calls and initial greeting"""
    resp = VoiceResponse()
    
    # Initial greeting
    gather = Gather(
        input='speech',
        timeout=2,
        language='en-US',
        hints=['hello', 'hi', 'help', 'goodbye'],
        action='/handle-input',
        method='POST',
    )
    
    gather.say(
        "Welcome to the AI voice assistant. How can i help you",
        voice="Polly.Aditi"
    )
    
    resp.append(gather)
    
    # If the user doesn't say anything, try again
    resp.redirect('/voice', method='POST')
    return str(resp)

@app.route("/handle-input", methods=['POST'])
def handle_input():
    """Process the user's speech input"""
    resp = VoiceResponse()
    
    # Get the user's speech input
    user_speech = request.values.get('SpeechResult', '')
    confidence = request.values.get('Confidence', 0)
    
    logger.info(f"Received speech input: {user_speech} (confidence: {confidence})")
    # logger.info(f"{text}")
    
    if user_speech.lower() in ['goodbye', 'bye']:
        resp.say("Thank you for chatting! Goodbye!", voice="Polly.Aditi")
        resp.hangup()
    elif user_speech:
        # Echo back what the user said
        chat_session = gemini()
        response = chat_session.generate_content(user_speech)
        print(response.text)
        resp.say(f"{response.text}", voice="Polly.Aditi")
        
        # Offer another interaction
        gather = Gather(
            input='speech',
            timeout=5,
            language='en-US',
            action='/handle-input',
            method='POST',
            hints=['goodbye', 'bye', 'help']
        )
        gather.say(
            "or say goodbye to end the call.",
            voice="Polly.Aditi"
        )
        resp.append(gather)
    else:
        resp.say(
            "I'm sorry, I didn't catch that. Let's try again.",
            voice="Polly.Aditi"
        )
        resp.redirect('/voice', method='POST')
    
    return str(resp)

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    logger.error(f"An error occurred: {str(error)}")
    resp = VoiceResponse()
    resp.say(
        "I'm sorry, something went wrong. Please try again later.",
        voice="Polly.Aditi"
    )
    resp.hangup()
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)