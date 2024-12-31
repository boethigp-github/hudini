import os
import glob
import json
import logging
from datasets import Dataset
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import TrainingArguments, Trainer
import torch

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data directory and model
DATA_DIR = r"/server/app/utils/finetuning/documentation_llm/trainingsdaten/routers"
MODEL_NAME = "gpt2-medium"


def load_data(data_dir, duplication_factor=1):
    """
    Load and optionally duplicate data in memory.
    """
    logger.info("Loading data from directory: %s", data_dir)
    conversation_files = glob.glob(os.path.join(data_dir, "*.json"))
    examples = []

    for file in conversation_files:
        logger.info("Processing file: %s", file)
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            convs = data.get("conversations", [])

            for conv in convs:
                system_context = ""
                user_message = ""
                assistant_response = ""

                role = conv["role"]
                content = conv["content"]

                if role == "system":
                    system_context = content
                elif role == "user":
                    user_message = content
                elif role == "assistant":
                    assistant_response = content

                if user_message and assistant_response:
                    prompt = f"{system_context}\n{user_message}\n"
                    completion = assistant_response
                    examples.append({"prompt": prompt, "completion": completion})

    # **Sicherstellen, dass die Duplizierung im Speicher stattfindet**
    original_count = len(examples)
    examples = examples * duplication_factor  # Dupliziere die geladenen Daten
    logger.debug(
        "Loaded %d examples after duplication (Original: %d, Duplication Factor: %d)",
        len(examples),
        original_count,
        duplication_factor,
    )
    return examples


# Load and duplicate data
duplication_factor = 100  # Increase this factor for more data
examples = load_data(DATA_DIR, duplication_factor)

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
        text, truncation=True, padding="max_length", max_length=256
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized


logger.info("Tokenizing the dataset...")
tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=["prompt", "completion"])
logger.info(f"Number of samples in the tokenized dataset: {len(tokenized_dataset)}")

# Load model
logger.info("Loading model...")
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)

# Training arguments
training_args = TrainingArguments(
    output_dir="llm_finetuned",
    overwrite_output_dir=True,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=5,
    fp16=False,
    evaluation_strategy="no",
    save_strategy="steps",
    save_steps=50,
    logging_steps=10,
    save_total_limit=1,
    learning_rate=5e-5,
    logging_dir="./logs",
)

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
)

# Start training
logger.info("Starting training...")
trainer.train()

# Save model and tokenizer manually
logger.info("Saving model and tokenizer manually...")
trainer.save_model(training_args.output_dir)
logger.info("Model and tokenizer saved to: %s", training_args.output_dir)
