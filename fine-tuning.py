# Install necessary libraries
# pip install transformers datasets torch sentencepiece huggingface_hub protobuf python-dotenv

import pandas as pd
import json
from transformers import GPT2Tokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, HfArgumentParser, DataCollatorWithPadding
from datasets import Dataset
import os
import tkinter as tk
from tkinter import filedialog
from huggingface_hub import login, HfApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Hugging Face token from environment variables
token = os.getenv("HUGGING_FACE_TOKEN")
if not token:
    token = input("Please enter your Hugging Face token: ")
    if not token:
        print("Hugging Face token not provided.")
        exit(1)

# Verify the token
api = HfApi()
try:
    user_info = api.whoami(token=token)
    print(f"Authenticated as {user_info['name']}")
except Exception as e:
    print(f"Invalid token: {e}")
    exit(1)

# Authenticate with Hugging Face
login(token=token)

# Open file picker window to import JSON file
root = tk.Tk()
root.withdraw()  # Hide the root window
file_path = filedialog.askopenfilename(title="Select JSON File", filetypes=[("JSON files", "*.json")])

if file_path:
    try:
        # Check if the file is empty
        if os.path.getsize(file_path) == 0:
            raise ValueError("The selected file is empty.")
        
        # Read the file content to check for valid JSON
        with open(file_path, 'r', encoding='utf-8-sig') as file:  # 'utf-8-sig' to handle BOM
            content = file.read()
            try:
                data = json.loads(content)
            except ValueError:
                print(f"Invalid JSON content: {content.strip()}")
                raise ValueError(f"Invalid JSON content - Please ensure the JSON format is correct.")
        
        # Load your dataset
        df = pd.DataFrame(data)
    except ValueError as e:
        print(f"Error reading JSON file: {e}")
        exit(1)

    # Convert the DataFrame to a Hugging Face Dataset
    dataset = Dataset.from_pandas(df)

    # Load the pre-trained model and tokenizer
    model_name = "facebook/opt-1.3b"  # Valid model name
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)  # Correct tokenizer class

    # Load the fine-tuned model if it exists
    fine_tuned_model_path = "./fine-tuned-llama3.1-8b"
    if os.path.exists(fine_tuned_model_path):
        model = AutoModelForCausalLM.from_pretrained(fine_tuned_model_path)
        tokenizer = GPT2Tokenizer.from_pretrained(fine_tuned_model_path)
    else:
        model = AutoModelForCausalLM.from_pretrained(model_name)

    # Inspect the dataset to find the correct key
    print("Dataset columns:", dataset.column_names)

    # Tokenize the dataset
    def tokenize_function(examples):
        return tokenizer(examples['requirement'], padding="max_length", truncation=True, max_length=512)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    # Add labels to the tokenized dataset
    def add_labels(examples):
        examples["labels"] = examples["input_ids"].copy()
        return examples

    tokenized_datasets = tokenized_datasets.map(add_labels, batched=True)

    # Create a data collator that handles padding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # Set up training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",  # Updated to use evaluation_strategy
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        num_train_epochs=3,
        weight_decay=0.01,
    )

    # Initialize the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets,
        eval_dataset=tokenized_datasets,
        data_collator=data_collator,  # Use the data collator
    )

    # Fine-tune the model
    trainer.train()

    # Save the fine-tuned model
    model.save_pretrained(fine_tuned_model_path)
    tokenizer.save_pretrained(fine_tuned_model_path)

    # Load new data
    new_file_path = filedialog.askopenfilename(title="Select New JSON File", filetypes=[("JSON files", "*.json")])
    if new_file_path:
        try:
            # Check if the file is empty
            if os.path.getsize(new_file_path) == 0:
                raise ValueError("The selected file is empty.")
            
            # Read the file content to check for valid JSON
            with open(new_file_path, 'r', encoding='utf-8-sig') as file:  # 'utf-8-sig' to handle BOM
                new_content = file.read()
                try:
                    new_data = json.loads(new_content)
                except ValueError:
                    print(f"Invalid JSON content: {new_content.strip()}")
                    raise ValueError(f"Invalid JSON content - Please ensure the JSON format is correct.")
            
            # Load your new dataset
            new_df = pd.DataFrame(new_data)
        except ValueError as e:
            print(f"Error reading JSON file: {e}")
            exit(1)

        # Convert the new DataFrame to a Hugging Face Dataset
        new_dataset = Dataset.from_pandas(new_df)

        # Combine the new dataset with the existing dataset
        combined_dataset = Dataset.from_pandas(pd.concat([df, new_df], ignore_index=True))

        # Tokenize the combined dataset
        tokenized_combined_datasets = combined_dataset.map(tokenize_function, batched=True)

        # Add labels to the tokenized combined dataset
        tokenized_combined_datasets = tokenized_combined_datasets.map(add_labels, batched=True)

        # Initialize the Trainer with the combined dataset
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_combined_datasets,
            eval_dataset=tokenized_combined_datasets,
            data_collator=data_collator,  # Use the data collator
        )

        # Fine-tune the model with the combined dataset
        trainer.train()

        # Save the fine-tuned model
        model.save_pretrained(fine_tuned_model_path)
        tokenizer.save_pretrained(fine_tuned_model_path)
    else:
        print("No new file selected.")
else:
    print("No file selected.")