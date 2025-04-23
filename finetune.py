# This file contains code used to finetune a HuggingFace model via Google Colab

# Run in terminal for required packages 
# pip install transformers datasets torch gradio
# pip install -U bitsandbytes

# Valid for Google Colab use only
# from google.colab import files

import pandas as pd
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from datasets import load_dataset
from transformers import Trainer, TrainingArguments
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import bitsandbytes

# Upload a CSV file - The dataset to be used for training (valid for Google Colab only)
# uploaded = files.upload()

# # Load CSV into dataframe
# csv_filename = list(uploaded.keys())[0]  # Get uploaded filename
# df = pd.read_csv(csv_filename)

# # Show first few rows of the dataframe
# df.head()

# Load Bert model & tokenizer
# model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')
# tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# # Qwen model
model_name = "Qwen/Qwen2.5-0.5B"

# # Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# # Load model in 4-bit mode
model = AutoModelForCausalLM.from_pretrained(model_name)
#     model_name,
#     torch_dtype=torch.float16,  # Use FP16 for efficiency
#     load_in_4bit=True  # Reduce memory usage
# )

# Load the imported dataset
dataset = load_dataset("csv", data_files="CSV dataset.csv")

# Print to confirm correct data format
print(dataset['train'][0])

# # Define the tokenizer function
def tokenize_function(example):
  return tokenizer(example["text"], padding="max_length", max_length=64, truncation=True)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

print("Tokenization complete")

# # Display DatasetDict object
# print(tokenizer)
# print(tokenized_dataset)
# print(tokenized_dataset['train'][50]['text'])

print()
print(tokenizer("'Evaluate")["input_ids"])
print(tokenizer("'Evaluate this")["input_ids"])
print(tokenizer("'Evaluate this requirement")["input_ids"])
print(tokenizer("'Evaluate this requirement: ")["input_ids"])
print(tokenized_dataset['train'][50])

# # Define training arguments for use at training stage
# training_args = TrainingArguments(
#     output_dir='./results',
#     learning_rate=2e-5,
#     per_device_train_batch_size=4,
#     per_device_eval_batch_size=4,
#     num_train_epochs=1,
#     weight_decay=0.01,
#     eval_strategy="epoch",
#     torch_empty_cache_steps=3,
# )

# # Confirm define training arguments
# # print(training_args)

# # Define training function
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=tokenized_dataset['train'],
#     eval_dataset=tokenized_dataset['train']
# )

# # Run training function
# trainer.train()

# # Run evaluation function
# trainer.evaluate()

# # Save the newly trained model for future use
# model.save_pretrained('./fine_tuned_incose_model')
# tokenizer.save_pretrained('./fine_tuned_incose_model')