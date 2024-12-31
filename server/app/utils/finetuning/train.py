import os
import glob
import json
import torch
import gc
import logging
from torch.optim import AdamW
from datasets import Dataset
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import TrainingArguments, Trainer

# Disable symlinks warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import warnings

# Suppress specific warnings
warnings.filterwarnings(
    "ignore",
    message="`resume_download` is deprecated and will be removed in version 1.0.0.*",
    category=FutureWarning,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data directory and model
DATA_DIR = r"/server/app/utils/finetuning/documentation_llm/trainingsdaten/duplicated"
MODEL_NAME = "gpt2"  # Verwende GPT-2 Base für weniger Speicherverbrauch

def load_data(data_dir):
    logger.info("Loading data from directory: %s", data_dir)
    conversation_files = glob.glob(os.path.join(data_dir, "*.json"))
    examples = []

    for file in conversation_files:
        logger.info("Processing file: %s", file)
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            convs = data.get("conversations", [])

            system_context = ""
            for msg in convs:
                role = msg["role"]
                content = msg["content"]

                if role == "system":
                    system_context = content
                elif role == "user":
                    user_message = content
                elif role == "assistant":
                    assistant_response = content

                    # Create an example for every USER-ASSISTANT pair
                    if system_context and user_message and assistant_response:
                        prompt = f"{system_context}\n{user_message}\n"
                        completion = assistant_response
                        examples.append({"prompt": prompt, "completion": completion})
                        user_message = ""  # Reset for the next pair
    logger.info("Loaded %d examples", len(examples))
    return examples

examples = load_data(DATA_DIR)
if len(examples) == 0:
    raise ValueError("No training examples found. Check the data directory or JSON structure.")

dataset = Dataset.from_list(examples)

# Load tokenizer
logger.info("Loading tokenizer for model: %s", MODEL_NAME)
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

def tokenize(example):
    text = example["prompt"] + example["completion"]
    tokenized = tokenizer(
        text, truncation=True, padding="max_length", max_length=256  # Etwas größere Länge
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

logger.info("Tokenizing the dataset...")
tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=["prompt", "completion"])
logger.info(f"Number of samples in the tokenized dataset: {len(tokenized_dataset)}")

# Load model
logger.info("Loading model...")
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)
model.resize_token_embeddings(len(tokenizer))

# Aktivieren von Gradient Checkpointing
model.gradient_checkpointing_enable()

# Training arguments
training_args = TrainingArguments(
    output_dir="llm_finetuned",
    overwrite_output_dir=True,
    per_device_train_batch_size=4,  # Batch-Größe erhöht
    gradient_accumulation_steps=8,  # Weniger Gradient Accumulation
    num_train_epochs=5,
    fp16=True,  # Mixed Precision
    evaluation_strategy="no",
    save_strategy="steps",
    save_steps=500,
    logging_steps=100,
    save_total_limit=1,
    learning_rate=2e-5,  # Angepasste Lernrate
    logging_dir="./logs",
)

# Define optimizer
optimizer = AdamW(model.parameters(), lr=2e-5)  # Optimierer mit angepasster Lernrate

# Function to print GPU memory usage
def print_gpu_usage():
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**2  # in MB
        cached = torch.cuda.memory_reserved() / 1024**2  # in MB
        logger.info(f"GPU Memory Allocated: {allocated:.2f} MB")
        logger.info(f"GPU Memory Cached: {cached:.2f} MB")
    else:
        logger.info("CUDA is not available. Using CPU.")

# Trainer setup
logger.info("Initializing Trainer...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=lambda data: {
        "input_ids": torch.tensor([f["input_ids"] for f in data]),
        "attention_mask": torch.tensor([f["attention_mask"] for f in data]),
        "labels": torch.tensor([f["labels"] for f in data]),
    },
    optimizers=(optimizer, None),  # Optimizer bleibt unverändert
)

# Start training
logger.info("Starting training...")
for epoch in range(training_args.num_train_epochs):
    logger.info(f"Epoch {epoch+1}")
    trainer.train()  # Trainiere das Modell
    print_gpu_usage()  # GPU-Verwendung nach jeder Epoche anzeigen

# Save model and tokenizer manually to ensure it is saved
logger.info("Saving model and tokenizer manually...")
trainer.save_model(training_args.output_dir)
logger.info("Model and tokenizer saved to: %s", training_args.output_dir)

# Free up GPU memory
logger.info("Clearing GPU memory...")
torch.cuda.empty_cache()
gc.collect()
logger.info("Training completed.")
