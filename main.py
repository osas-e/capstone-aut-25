import os
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer

# ---------------------------
# 1️⃣ GUI to Select CSV File
# ---------------------------
def select_csv_file():
    root = tk.Tk()
    root.withdraw()  # Hide main Tkinter window
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
    return file_path

csv_file = select_csv_file()

if not csv_file:
    print("No file selected. Exiting.")
    exit()

print(f"Selected file: {csv_file}")

# ---------------------------
# 2️⃣ Load CSV and Process Rule-by-Rule
# ---------------------------
# Define save paths
jsonl_file = "./gemma_fine_tune.jsonl"
model_save_path = "./gemma-finetuned"

# Load dataset
df = pd.read_csv(csv_file, nrows=28)

# Define the rules
rules = {
    "R1": "Need and requirement statements must conform to one of the agreed patterns, thus resulting in a well-structured complete statement.",
    "R6": "When stating quantities, all numbers should have appropriate and consistent units of measure explicitly stated using a common measurement system in terms of the thing the number refers.",
    "R11": "Use a separate clause for each condition or qualification.",
    "R12": "Use correct grammar",
    "R14": "Use correct punctuation.",
    "R16": "Avoid the use of 'not'",
    "R26": "Avoid using unachievable absolutes such as 100% reliability, 100% availability, all, every, always, never, etc.",
    "R27": "State conditions’ applicability explicitly instead of leaving applicability to be inferred from the context.",
    "R32": "Use 'each' instead of 'all', 'any', or 'both' when universal quantification is intended.",
    "R33": "Define each quantity with a range of values appropriate to the entity to which the quantity applies and against which the entity will be verified or validated.",
    "R36": "Ensure each term and unit of measure used throughout need and requirement sets as well as associated models and other SE artefacts developed across the lifecycle are consistent with the project’s defined ontology."
}

# Prepare fine-tuning dataset
formatted_data = []

for rule_name, rule_description in rules.items():
    for _, row in df.iterrows():
        requirement_text = row["RequirementText"]
        compliance_value = str(row[rule_description])  # Get compliance score (0 or 1)

        # Format as instruction-response pairs
        formatted_entry = {
            "input": row["RequirementText"],
            "output": {
            "r1": 1 if "1" in str(row[rules["R1"]]) else 0,
            "r6": 1 if "1" in str(row[rules["R6"]]) else 0,
            "r11": 1 if "1" in str(row[rules["R11"]]) else 0,
            "r12": 1 if "1" in str(row[rules["R12"]]) else 0,
            "r14": 1 if "1" in str(row[rules["R14"]]) else 0,
            "r16": 1 if "1" in str(row[rules["R16"]]) else 0,
            "r26": 1 if "1" in str(row[rules["R26"]]) else 0,
            "r27": 1 if "1" in str(row[rules["R27"]]) else 0,
            "r32": 1 if "1" in str(row[rules["R32"]]) else 0,
            "r33": 1 if "1" in str(row[rules["R33"]]) else 0,
            "r36": 1 if "1" in str(row[rules["R36"]]) else 0,
            "explanation": " | ".join([f"{rule}: {row[rules[rule]]}" for rule in rules if "0" in str(row[rules[rule]])])
            }
        }

        formatted_data.append(formatted_entry)

# Save dataset in JSONL format
with open(jsonl_file, "w") as f:
    for item in formatted_data:
        f.write(json.dumps(item) + "\n")

print(f"Fine-tuning data saved to: {jsonl_file}")

# ---------------------------
# 3️⃣ Load and Tokenize the Dataset
# ---------------------------
# Load dataset
dataset = load_dataset("json", data_files=jsonl_file)

# Load Gemma tokenizer
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

# Tokenization function
def tokenize_function(examples):
    return tokenizer(examples["input"], truncation=True, padding="max_length", max_length=2048)

# Apply tokenization
tokenized_datasets = dataset.map(tokenize_function, batched=True)
tokenized_datasets.set_format("torch")

print("Tokenization complete.")

# ---------------------------
# 4️⃣ Fine-Tune the Model
# ---------------------------
# Load pre-trained Gemma model
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

# Set training arguments
training_args = TrainingArguments(
    output_dir=model_save_path,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    num_train_epochs=2,
    logging_dir="./logs",
    evaluation_strategy="no",
    # save_strategy="epoch",
    learning_rate=5e-5,
    weight_decay=0.01,
    fp16=False
)

# Initialize Trainer
model_save_path = './qwen_incose_expert'

# Start fine-tuning

subset_size = 2
train_subset = tokenized_datasets["train"].select(range(subset_size))

trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_subset,
        tokenizer=tokenizer
)
    
trainer.train()

model.save_pretrained(model_save_path)
tokenizer.save_pretrained(model_save_path)


print(f"Fine-tuned model saved to: {model_save_path}")

# ---------------------------
# 5️⃣ Save the Fine-Tuned Model
# ---------------------------

# # Ensure save directory exists
# os.makedirs(model_save_path, exist_ok=True)

# Save model and tokenizer

