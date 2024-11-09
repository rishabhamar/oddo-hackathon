import streamlit as st
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import torch
import sounddevice as sd
import queue
import numpy as np
import tempfile
import whisper
from scipy.io import wavfile
import whisper.audio
import subprocess

# Load environment variables
load_dotenv()

# Initialize InferenceClient
hf_token = os.getenv("HUGGINGFACE_TOKEN")

if not hf_token:
    raise ValueError("HUGGINGFACE_TOKEN not found in .env file")

# Configure Hugging Face API
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
headers = {"Authorization": f"Bearer {hf_token}"}

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Define FFmpeg path - add this near the top of the file with other initializations
FFMPEG_PATH = "ffmpeg"  # Uses system FFmpeg if it's in PATH, or specify full path if needed

# Function to transcribe audio using Whisper
def transcribe_audio(audio):
    temp_audio_file = None
    try:
        # Create temp file
        temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        
        # Convert audio to float32 and ensure it's in the correct range
        audio = audio.astype(np.float32)
        audio = np.clip(audio, -1, 1)
        
        # Save as WAV
        wavfile.write(temp_audio_file.name, 16000, audio)
        temp_audio_file.close()
        
        # Send to Hugging Face API
        with open(temp_audio_file.name, "rb") as f:
            data = f.read()
        
        response = requests.post(API_URL, headers=headers, data=data)
        
        if response.status_code != 200:
            st.error(f"API request failed with status code: {response.status_code}")
            return ""
            
        result = response.json()
        
        # Extract text from response
        if "text" in result:
            return result["text"].strip()
        else:
            st.error(f"Unexpected API response format")
            return ""
    
    except Exception as e:
        st.error(f"Error during transcription: {str(e)}")
        return ""
    
    finally:
        if temp_audio_file:
            try:
                os.unlink(temp_audio_file.name)
            except Exception:
                pass

# Function to generate response using InferenceClient
def generate_response(prompt):
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    stream = client.chat.completions.create(
        model="google/gemma-2-2b-it",
        messages=messages,
        max_tokens=500,
        stream=True
    )
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content
    return response

# Function to record audio
def record_audio(duration=5, fs=16000):
    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        audio = np.empty((0, 1), dtype=np.float32)
        for _ in range(int(duration * fs / 1024)):
            audio = np.append(audio, q.get(), axis=0)
    return audio

# Main UI
st.title("🗣️ Voice Assistant for Mental Health Counseling")
st.write("""
Welcome to your safe space for mental health support. I'm here to listen and provide 
guidance. While I'm an AI assistant and not a replacement for professional help, 
I'll do my best to support you.
""")

# Record audio
if st.button("Record"):
    st.write("Recording...")
    audio = record_audio()
    st.session_state.audio = audio
    st.write("Recording complete. Click 'Send' to transcribe and get a response.")

# Transcribe and generate response
if st.button("Send"):
    if 'audio' in st.session_state:
        st.write("Transcribing...")
        prompt = transcribe_audio(st.session_state.audio)
        if prompt:
            st.write(f"User: {prompt}")

            # Generate and display assistant response
            st.write("Generating response...")
            response = generate_response(prompt)
            st.write(f"Assistant: {response}")

            # Add to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            st.warning("Transcription failed. Please try again.")
    else:
        st.warning("Please record audio first.")

# Sidebar for chat history
st.sidebar.title("Chat History")
for message in st.session_state.chat_history:
    st.sidebar.write(f"{message['role'].capitalize()}: {message['content']}")

# Disclaimer
st.sidebar.title("Important Notice")
st.sidebar.warning("""
This is an AI assistant meant for general support only. If you're experiencing a mental health crisis or 
having thoughts of self-harm, please contact emergency services or mental health crisis hotlines:

- National Crisis Hotline (US): 988
- Crisis Text Line: Text HOME to 741741

Remember, professional mental health practitioners are the best resource for serious concerns.
""")

try:
    result = subprocess.run([FFMPEG_PATH, "-version"], capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"FFmpeg not found: {e}")
