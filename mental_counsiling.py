import streamlit as st
import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
import os
from dotenv import load_dotenv

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
def load_model():
    """Load the model and tokenizer"""
    # Get token from environment variable
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    
    if not hf_token:
        raise ValueError("Please set the HUGGINGFACE_TOKEN environment variable")
    
    login(hf_token)
    
    config = PeftConfig.from_pretrained("GRMenon/mental-health-mistral-7b-instructv0.2-finetuned-V2")
    offload_dir = "offload_dir"
    if not os.path.exists(offload_dir):
        os.makedirs(offload_dir)

    # Alternative 1: CPU-only approach
    base_model = AutoModelForCausalLM.from_pretrained(
        "mistralai/Mistral-7B-Instruct-v0.2",
        torch_dtype=torch.float16,
        device_map={"": "cpu"},  # Force CPU-only
        offload_folder=offload_dir
    )

    # Alternative 2: More aggressive memory constraints
    base_model = AutoModelForCausalLM.from_pretrained(
        "mistralai/Mistral-7B-Instruct-v0.2",
        torch_dtype=torch.float16,
        device_map="balanced_low_0",
        max_memory={
            0: "1GB",      # Even more conservative GPU usage
            "cpu": "16GB"
        },
        offload_folder=offload_dir
    )

    # Move model to the appropriate device
    base_model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

    model = PeftModel.from_pretrained(
        base_model, 
        "GRMenon/mental-health-mistral-7b-instructv0.2-finetuned-V2"
    )
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
    return model, tokenizer

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

- National Crisis Hotline (US): 988
- Crisis Text Line: Text HOME to 741741

Remember, professional mental health practitioners are the best resource for serious concerns.
""")

if not os.path.exists("offload_dir"):
    os.makedirs("offload_dir")
