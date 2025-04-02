import os
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer

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
