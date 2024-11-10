# Standard library imports
import logging
import os
import gc
from datetime import datetime

# Third-party imports
import torch
import torch.utils.data
import torch.utils.data.dataset
import warnings
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
import pandas as pd
from torch.utils.data import Dataset

warnings.filterwarnings("ignore", message=".*Tried to instantiate class '__path__._path'.*")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modified device initialization
def setup_device():
    if torch.cuda.is_available():
        # Clear GPU memory
        torch.cuda.empty_cache()
        gc.collect()
        
        device = torch.device("cuda")
        logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**2:.0f}MB")
    else:
        device = torch.device("cpu")
        logger.info("No GPU available, using CPU")
    return device

# Load the model and tokenizer
def load_model_and_tokenizer():
    # Using a smaller model that can fit in 4GB GPU
    model_name = "google/gemma-2b-it"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            use_cache=False,
            low_cpu_mem_usage=True,
            max_memory={
                0: "3GB",  # Reserve 4GB for GPU
                "cpu": "12GB"  # Reserve 12GB for CPU
            }
        )
        # Enable gradient checkpointing after model initialization
        model.gradient_checkpointing_enable()
        model.config.use_cache = False
        logger.info(f"Model loaded on: {model.device}")
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading model and tokenizer: {e}")
        raise

# Create a custom dataset class with error handling
class MentalHealthDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_length=32):  # Reduced max_length to 32
        self.tokenizer = tokenizer
        # Take only first 1000 samples to reduce memory usage during training
        self.text = [str(text) for text in dataframe['text'].fillna('').tolist()[:1000]]
        self.labels = dataframe['label'].fillna(0).tolist()[:1000]
        self.max_length = max_length

    def __len__(self):
        return len(self.text)

    def __getitem__(self, idx):
        try:
            text = self.text[idx]
            label = self.labels[idx]

            encoding = self.tokenizer(
                text,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )

            # Ensure labels have the same shape as input_ids
            encoding['labels'] = encoding['input_ids'].clone()

            return {
                'input_ids': encoding['input_ids'].squeeze(),
                'attention_mask': encoding['attention_mask'].squeeze(),
                'labels': encoding['labels'].squeeze()
            }
        except Exception as e:
            logger.error(f"Error processing item {idx}: {e}")
            raise


def prepare_data():
    try:
        # Load and preprocess the dataset
        df = pd.read_csv("Assets/data.csv")
        
        # Clean and prepare the dataset
        df = df[['statement', 'status']].rename(columns={'statement': 'text', 'status': 'label'})
        
        # Remove any rows with missing values
        df = df.dropna()
        
        # Convert labels to numerical values
        label_map = {'Anxiety': 1, 'Non-Anxiety': 0}
        df['label'] = df['label'].map(label_map)
        
        # Remove any rows where label mapping failed
        df = df.dropna()
        
        return df
    except Exception as e:
        logger.error(f"Error preparing data: {e}")
        raise

def train_model(model, tokenizer, df):
    try:
        # Clear memory before training
        torch.cuda.empty_cache()
        gc.collect()

        # Take smaller subset for training
        df = df.sample(n=min(1000, len(df)), random_state=42)
        
        train_size = int(0.8 * len(df))
        train_dataset = MentalHealthDataset(df[:train_size], tokenizer)
        eval_dataset = MentalHealthDataset(df[train_size:], tokenizer)

        training_args = TrainingArguments(
            output_dir="./mental_health_model",
            num_train_epochs=2,  # Reduced epochs
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            gradient_accumulation_steps=16,  # Increased for memory efficiency
            warmup_steps=50,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=10,
            eval_strategy="steps",
            save_strategy="steps",
            save_steps=50,
            eval_steps=50,
            # Memory optimization settings
            fp16=True,
            gradient_checkpointing=True,
            optim="adamw_torch",
            max_grad_norm=0.5,
            # Disable unnecessary features
            report_to="none",
            dataloader_num_workers=0,
            dataloader_pin_memory=False,
            # Save memory during evaluation
            predict_with_generate=False,
            include_inputs_for_metrics=False
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset
        )

        # Train with memory monitoring
        try:
            trainer.train()
        except RuntimeError as e:
            if "out of memory" in str(e):
                torch.cuda.empty_cache()
                gc.collect()
                logger.error("Memory error occurred. Consider reducing dataset size or model size.")
            raise

        output_dir = "./mental_health_model_final"
        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        return model, tokenizer

    except Exception as e:
        logger.error(f"Error during training: {e}")
        raise

def analyze_mental_health(text, model, tokenizer):
    try:
        # Clear GPU cache before inference
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

        inputs = tokenizer(text, return_tensors="pt", max_length=64, truncation=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        with torch.cuda.amp.autocast():
            with torch.no_grad():  # Added to save memory during inference
                outputs = model.generate(
                    **inputs,
                    max_length=50,
                    num_beams=2,  # Reduced beam search
                    early_stopping=True
                )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return f"Anxiety Assessment: {response}"
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        return "Error processing your message. Please try again."

def main():
    try:
        # Remove the device setup since accelerate handles it
        logger.info(f"PyTorch CUDA available: {torch.cuda.is_available()}")
        
        # Load model and tokenizer
        model, tokenizer = load_model_and_tokenizer()
        
        # Check if model is already trained
        if not os.path.exists("./mental_health_model_final"):
            # Prepare and train model
            df = prepare_data()
            model, tokenizer = train_model(model, tokenizer, df)
        else:
            # Load trained model - remove .to(device)
            model = AutoModelForCausalLM.from_pretrained(
                "./mental_health_model_final",
                device_map="auto",
                torch_dtype=torch.float16
            )
            tokenizer = AutoTokenizer.from_pretrained("./mental_health_model_final")

        # Streamlit UI
        st.set_page_config(page_title="Mental Health Chat Assistant", page_icon="🧠", layout="wide")
        st.title("Mental Health Chat Assistant")

        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Chat UI
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"<div class='user-bubble'>{message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-bubble'>{message['content']}</div>", unsafe_allow_html=True)

        user_input = st.text_input("Type your message here...", key="user_input")

        if st.button("Send") or user_input:
            if user_input:
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().strftime("%H:%M")
                })
                
                with st.spinner('Processing your message...'):
                    response = analyze_mental_health(user_input, model, tokenizer)
                
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().strftime("%H:%M")
                })
                
                st.experimental_rerun()

        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An error occurred. Please check the logs for details.")

if __name__ == "__main__":
    main()