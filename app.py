import json
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import re

# Define the explanation pattern
explanation_pattern = re.compile(r"(\d+)(?:\s*-\s*(.*))?")

# Define the jsonl file path
json_file_path = "output.json"

# Open file picker window to import dataset
root = tk.Tk()
root.withdraw()  # Hide the root window
file_path = filedialog.askopenfilename(title="Select CSV or XLSX File", filetypes=[("CSV files", "*.csv"),("XLSX files", "*.xlsx")])

if file_path:
    file_extension = os.path.splitext(file_path)[1].lower()

    # Load the dataset into a DataFrame
    if file_extension == ".xlsx":
        df = pd.read_excel(file_path)
    elif file_extension == ".csv":
        df = pd.read_csv(file_path)

    # Set the requirement column to the second column
    requirement_column = df.columns[1]

    # Dynamically identify the rule columns and their descriptions
    rules = {}
    for col in df.columns[2:-1]:  # Exclude the last column for final rating
        rule_name = col
        rule_description = df.iloc[0][col]
        rules[rule_name] = rule_description

    rule_columns = list(rules.keys())
    final_rating_column = df.columns[-1]  # The last column for final rating

    with open(json_file_path, mode='w', encoding='utf-8') as out_file:
        # Loop through requirements (rows), starting from the first row after the header
        for _, row in df.iterrows():
            requirement_text = str(row[requirement_column]).strip()

            if not requirement_text or requirement_text.lower() == 'nan':
                continue

            # Create a dictionary to hold the requirement and its rules
            requirement_entry = {
                "requirement": requirement_text,
                "rules": []
            }

            # Loop through each rule
            for rule_column in rule_columns:
                rule_name = rule_column
                cell_value = str(row[rule_column]).strip()

                if cell_value.lower() in ["nan", ""]:
                    continue

                # Extract numeric value and optional explanation
                match = explanation_pattern.match(cell_value)

                if match:
                    compliance_result = match.group(1)
                    explanation = match.group(2).strip() if match.group(2) else None
                else:
                    compliance_result = cell_value
                    explanation = None

                # If compliance result is '0', read the explanation from the next cell
                if compliance_result == '0' and not explanation:
                    explanation_index = df.columns.get_loc(rule_column) + 1
                    if explanation_index < len(df.columns):
                        explanation = str(row.iloc[explanation_index]).strip()

                # Rule entry
                rule_entry = {
                    "rule": rule_name,
                    "output": compliance_result
                }

                # Add explanation if present and non-compliant (score = 0)
                if compliance_result == '0' and explanation:
                    rule_entry["explanation"] = explanation

                # Add rule entry to the requirement's rules
                requirement_entry["rules"].append(rule_entry)

            # Add final rating
            final_rating = float(row[final_rating_column])
            requirement_entry["Final rating"] = final_rating

            # Write the requirement entry to JSONL file with indentation
            out_file.write(json.dumps(requirement_entry, ensure_ascii=False, indent=4) + "\n")

def xlsx_to_json(xlsx_path, json_path):
    df = pd.read_excel(xlsx_path)
    df.to_json(json_path, orient='records', lines=True)
    return json_path

def csv_to_json(csv_path, json_path):
    df = pd.read_csv(csv_path)
    df.to_json(json_path, orient='records', lines=True)
    return json_path
