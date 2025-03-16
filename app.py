import os
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import ollama

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
jsonl_file = "./gemma_fine_tune.jsonl"

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
            "input": f"Evaluate this requirement against {rule_name}: '{rule_description}'Requirement: '{requirement_text}'",
            "output": "Pass" if "1" in compliance_value else f"Fails {rule_name}: {rule_description}"
        }

        formatted_data.append(formatted_entry)

# Save dataset in JSONL format
with open(jsonl_file, "w") as f:
    for item in formatted_data:
        f.write(json.dumps(item) + "\n")

print(f"Fine-tuning data saved to: {jsonl_file}")

# ---------------------------
# 3️⃣ Fine-Tune Gemma with Ollama
# ---------------------------
# Convert JSONL data to Ollama's fine-tuning format
ollama_fine_tune_data = []

for item in formatted_data:
    ollama_fine_tune_data.append(f"message user {item['input']}")
    ollama_fine_tune_data.append(f"message assistant {item['output']}")

# ollama_fine_tune_data = [{"prompt": item["input"], "completion": item["output"]} for item in formatted_data]

# Save in Ollama’s format (optional step)
ollama_finetune_file = "ollama_finetune.txt"
with open(ollama_finetune_file, "w") as f:
    f.write("\n".join(ollama_fine_tune_data))

print(f"Fine-tuning data formatted for Ollama: {ollama_finetune_file}")

# # Run fine-tuning command via Ollama CLI
# model_name = "gemma2"  # Change if using a different version

# os.system(f"ollama create gemma-incose-expert -f {ollama_finetune_file}")

# print("Fine-tuning complete. Model saved as 'gemma-incose-expert' in Ollama.")

# # ---------------------------
# # 4️⃣ Use the Fine-Tuned Model in Ollama
# # ---------------------------
# def query_ollama(prompt):
#     response = ollama.chat(model="gemma-incose-expert", messages=[{"role": "user", "content": prompt}])
#     return response["message"]["content"]

# # Example Test
# test_input = "Evaluate this requirement against Rule 2: 'When stating quantities, all numbers should have appropriate and consistent units of measure.'\nRequirement: 'The system shall display the Events in a graph by time.'"
# output = query_ollama(test_input)

# print("Test Output from Fine-Tuned Model:")
# print(output)
