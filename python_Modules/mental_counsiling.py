import streamlit as st
import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer,
    BitsAndBytesConfig
)
from peft import PeftModel
from huggingface_hub import login
import os
from dotenv import load_dotenv
import logging
import sys
from typing import Tuple, Optional

# Set up logging at the top of your file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_loading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Mental Health Counseling Assistant",
    page_icon="🧠",
    layout="centered"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

@st.cache_resource
def load_model() -> Tuple[Optional[AutoModelForCausalLM], Optional[AutoTokenizer]]:
    
    try:
        logging.info("Starting model loading process...")
        
        # Get token from environment variable
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        if not hf_token:
            raise ValueError("HUGGINGFACE_TOKEN environment variable is not set")
        
        logging.info("HuggingFace token found")
        
        # Create offload directory
        offload_dir = os.path.join(os.getcwd(), "offload_dir")
        os.makedirs(offload_dir, exist_ok=True)
        logging.info(f"Created offload directory at {offload_dir}")
        
        # System info logging
        logging.info(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logging.info(f"GPU Model: {torch.cuda.get_device_name(0)}")
            logging.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        logging.info(f"Python version: {sys.version}")
        logging.info(f"PyTorch version: {torch.__version__}")
        
        # Load tokenizer
        logging.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.2",
            trust_remote_code=True
        )
        logging.info("Tokenizer loaded successfully")
        
        # Configure quantization
        logging.info("Configuring model quantization...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float32,
            bnb_4bit_use_double_quant=True
        )
        
        # Load base model
        logging.info("Loading base model...")
        base_model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.2",
            quantization_config=bnb_config,
            device_map="cpu",
            trust_remote_code=True,
            offload_folder=offload_dir,
            low_cpu_mem_usage=True
        )
        logging.info("Base model loaded successfully")
        
        # Load PEFT model
        logging.info("Loading PEFT model...")
        model = PeftModel.from_pretrained(
            base_model,
            "GRMenon/mental-health-mistral-7b-instructv0.2-finetuned-V2",
            device_map="cpu"
        )
        logging.info("PEFT model loaded successfully")
        
        return model, tokenizer
        
    except Exception as e:
        logging.error(f"Error during model loading: {str(e)}", exc_info=True)
        st.error(f"""
        An error occurred while loading the model. Details:
        
        Type: {type(e).__name__}
        Message: {str(e)}
        
        Please check the log file 'model_loading.log' for more details.
        
        System Info:
        - CUDA Available: {torch.cuda.is_available()}
        - Python Version: {sys.version}
        - PyTorch Version: {torch.__version__}
        """)
        return None, None

def generate_response(prompt, model, tokenizer):
    """Generate response from the model"""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=512,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Main UI
st.title("🧠 Mental Health Counseling Assistant")
st.write("""
Welcome to your safe space for mental health support. I'm here to listen and provide 
guidance. While I'm an AI assistant and not a replacement for professional help, 
I'll do my best to support you.
""")

# Load model
try:
    model, tokenizer = load_model()
    if model is None or tokenizer is None:
        st.error("Failed to load model. Please check the logs for details.")
        st.stop()
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Share what's on your mind..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_prompt = f"""<s>[INST] You are a compassionate mental health counseling assistant. 
                Provide supportive and empathetic responses while maintaining professional boundaries. 
                User message: {prompt} [/INST]"""
                response = generate_response(full_prompt, model, tokenizer)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

except Exception as e:
    st.error(f"""
    ⚠️ An error occurred while loading the model. This could be due to memory constraints.
    Please make sure you have sufficient GPU memory available.
    
    Error details: {str(e)}
    """)

# Disclaimer
st.sidebar.title("Important Notice")
st.sidebar.warning("""
This is an AI assistant meant for general support only. If you're experiencing a mental health crisis or 
having thoughts of self-harm, please contact emergency services or mental health crisis hotlines:

- KIRAN Hotline: 1800-599-0019
- Sumaitri Line: 011 23389090, 01146018404, and 9315767849.

Remember, professional mental health practitioners are the best resource for serious concerns.
""")
    