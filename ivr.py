# from flask import Flask, request, Response
# import requests
# from twilio.twiml.voice_response import VoiceResponse, Gather
# from twilio.rest import Client
# import json
# import os
# from datetime import datetime
# import firebase_admin
# from firebase_admin import credentials, firestore
# import streamlit as st
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
# import threading

# @st.cache_resource
# def load_model():
#     tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
#     model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
#     return tokenizer, model

# tokenizer, model = load_model()

# flask_app = Flask(__name__)

# # You'll need to replace these with your actual values
# TWILIO_ACCOUNT_SID = "USdcbfe267f637b1355f16e93b153d5e64"
# TWILIO_AUTH_TOKEN = "6be19c83f4543832b9620c2059c84975"
# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# # Store conversations in memory (replace with database in production)
# cred = credentials.Certificate("credentials.json")
# firebase_admin.initialize_app(cred)

# db=firestore.client()

# conversations = {}

# def get_dialogpt_response(user_input, chat_history_ids=None):
#     """Get response from DialoGPT"""
#     # Encode user input
#     new_user_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')

#     # Append to chat history if it exists
#     if chat_history_ids is not None:
#         bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
#     else:
#         bot_input_ids = new_user_input_ids

#     # Generate response
#     chat_history_ids = model.generate(
#         bot_input_ids,
#         max_length=1000,
#         pad_token_id=tokenizer.eos_token_id,
#         no_repeat_ngram_size=3,
#         do_sample=True,
#         top_k=100,
#         top_p=0.7,
#         temperature=0.8
#     )

#     # Decode and return response
#     response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
#     return response, chat_history_ids

# # Streamlit interface
# def main():
#     st.title("DialoGPT IVR System")

#      # Add phone call section
#     st.subheader("Make a Call")
#     phone_number = st.text_input("Enter phone number (with country code, e.g., +91XXXXXXXXXX)")
    
#     if st.button("Make Call"):
#         if phone_number:
#             try:
#                 # Make the call
#                 call = client.calls.create(
#                     to=phone_number,
#                     from_=TWILIO_PHONE_NUMBER,
#                     url=f"https://your-ngrok-url.ngrok.io/voice"  # Replace with your ngrok URL
#                 )
#                 st.success(f"Call initiated! Call SID: {call.sid}")
#             except Exception as e:
#                 st.error(f"Error making call: {str(e)}")
#         else:
#             st.warning("Please enter a phone number")
    
#     # Initialize session state
#     if 'chat_history' not in st.session_state:
#         st.session_state.chat_history = []
#     if 'model_history_ids' not in st.session_state:
#         st.session_state.model_history_ids = None
    
#     # Chat interface
#     st.subheader("Chat Interface")
    
#     # Display chat history
#     for message in st.session_state.chat_history:
#         with st.chat_message(message["role"]):
#             st.write(message["content"])
    
#     # Chat input
#     if user_input := st.chat_input("Type your message here..."):
#         # Add user message to chat
#         st.session_state.chat_history.append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.write(user_input)
        
#         # Get bot response
#         bot_response, st.session_state.model_history_ids = get_dialogpt_response(
#             user_input, 
#             st.session_state.model_history_ids
#         )
        
#         # Add bot response to chat
#         st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
#         with st.chat_message("assistant"):
#             st.write(bot_response)
    
#     # IVR Status
#     st.subheader("IVR System Status")
#     st.write(f"Active calls: {len(conversations)}")
    
#     # Display IVR logs if any exist
#     if conversations:
#         st.json(conversations)
    
#     db.collection("chat history").add(conversations)

# # Flask routes for IVR
# @flask_app.route("/voice", methods=['POST'])
# def voice():
#     """Handle incoming calls"""
#     response = VoiceResponse()
    
#     # Initialize the call session
#     caller_id = request.values.get('From', '')
#     if caller_id not in conversations:
#         conversations[caller_id] = {
#             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             'messages': [],
#             'model_history_ids': None
#         }
    
#     # Welcome message and gather speech input
#     gather = Gather(
#         input='speech',
#         action='/handle-input',
#         language='en-IN',
#         timeout=3,
#         speech_timeout='auto'
#     )
#     gather.say("Welcome to our AI assistant. How may I help you today?", voice='Polly.Aditi')
#     response.append(gather)
    
#     return str(response)

# @flask_app.route("/handle-input", methods=['POST'])
# def handle_input():
#     """Handle speech input and generate response"""
#     response = VoiceResponse()
#     caller_id = request.values.get('From', '')
    
#     # Get the speech input
#     user_speech = request.values.get('SpeechResult', '')
    
#     if user_speech:
#         # Store the user message
#         conversations[caller_id]['messages'].append({
#             'role': 'user',
#             'content': user_speech
#         })
        
#         # Get response from DialoGPT
#         bot_response, conversations[caller_id]['model_history_ids'] = get_dialogpt_response(
#             user_speech,
#             conversations[caller_id].get('model_history_ids')
#         )
        
#         # Store the bot response
#         conversations[caller_id]['messages'].append({
#             'role': 'assistant',
#             'content': bot_response
#         })
        
#         # Convert bot response to speech
#         gather = Gather(
#             input='speech',
#             action='/handle-input',
#             language='en-IN',
#             timeout=3,
#             speech_timeout='auto'
#         )
#         gather.say(bot_response, voice='Polly.Aditi')
#         response.append(gather)
#     else:
#         response.say("I didn't catch that. Could you please repeat?", voice='Polly.Aditi')
#         response.redirect('/voice')
    
#     return str(response)

# def run_flask():
#     """Run Flask app"""
#     flask_app.run(port=5000)

# if __name__ == "__main__":
#     # Start Flask in a separate thread
#     flask_thread = threading.Thread(target=run_flask)
#     flask_thread.start()
    
#     # Run Streamlit
#     main()

# # def get_chatbot_response(message, session_id):
# #     """
# #     Function to integrate with your chatbot
# #     Replace this with your actual chatbot integration
# #     """
# #     # Example: You can integrate with DialoGPT or any other open-source chatbot
# #     response = "Thank you for your message: " + message
# #     return response

# # @app.route("/voice", methods=['POST'])
# # def voice():
# #     """Handle incoming calls"""
# #     response = VoiceResponse()
    
# #     # Initialize the call session
# #     caller_id = request.values.get('From', '')
# #     if caller_id not in conversations:
# #         conversations[caller_id] = {
# #             'timestamp': datetime.now(),
# #             'messages': []
# #         }
    
# #     # Welcome message and gather speech input
# #     gather = Gather(
# #         input='speech',
# #         action='/handle-input',
# #         language='en-IN',  # Set to Indian English
# #         timeout=3,
# #         speech_timeout='auto'
# #     )
# #     gather.say("Welcome to our service. How may I help you today?", voice='Polly.Aditi')  # Using Indian voice
# #     response.append(gather)
    
# #     return str(response)

# # @app.route("/handle-input", methods=['POST'])
# # def handle_input():
# #     """Handle speech input and generate response"""
# #     response = VoiceResponse()
# #     caller_id = request.values.get('From', '')
    
# #     # Get the speech input
# #     user_speech = request.values.get('SpeechResult', '')
    
# #     if user_speech:
# #         # Store the user message
# #         conversations[caller_id]['messages'].append({
# #             'role': 'user',
# #             'content': user_speech
# #         })
        
# #         # Get response from chatbot
# #         bot_response = get_chatbot_response(user_speech, caller_id)
        
# #         # Store the bot response
# #         conversations[caller_id]['messages'].append({
# #             'role': 'assistant',
# #             'content': bot_response
# #         })
        
# #         # Convert bot response to speech
# #         gather = Gather(
# #             input='speech',
# #             action='/handle-input',
# #             language='en-IN',
# #             timeout=3,
# #             speech_timeout='auto'
# #         )
# #         gather.say(bot_response, voice='Polly.Aditi')
# #         response.append(gather)
# #     else:
# #         response.say("I didn't catch that. Could you please repeat?", voice='Polly.Aditi')
# #         response.redirect('/voice')
    
# #     return str(response)

# # @app.route("/webhook", methods=['POST'])
# # def webhook():
# #     """Handle webhook events from Twilio"""
# #     return Response(status=200)


# # if __name__ == "__main__":
# #     app.run(debug=True, port=5000)

from flask import Flask
from pysip import SIPServer
import vosk
import json
import wave
import pyaudio

app = Flask(__name__)

class SIPIVRServer:
    def __init__(self):
        self.sip = SIPServer(
            bind_address="0.0.0.0",
            bind_port=5060,
            realm="ivr.local"
        )
        
        # Initialize speech recognition
        self.model = vosk.Model("vosk-model-en-in-0.4")
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        
    def start(self):
        @self.sip.incoming_call
        def handle_call(call):
            # Answer call
            call.answer()
            
            # Record audio
            audio = self.record_audio()
            
            # Convert speech to text
            text = self.speech_to_text(audio)
            
            # Get AI response
            response = "This is Test" # get_dialogpt_response(text)
            
            # Play response
            self.play_response(call, response)
            
            # End call
            call.hangup()
    
    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = 5
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return b''.join(frames)
    
    def speech_to_text(self, audio):
        if self.recognizer.AcceptWaveform(audio):
            result = json.loads(self.recognizer.Result())
            return result['text']
        return ""

if __name__ == "__main__":
    # Start SIP server
    server = SIPIVRServer()
    server.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000)