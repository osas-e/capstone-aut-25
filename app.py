import csv
import json
import os
import tkinter as tk
from tkinter import filedialog

# Convert .csv to JSON
def csv_to_json(csv_file_path, json_file_path):
    data = []
    
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)[1:14]  # Columns 2-14 selected which contain INCOSE rules
        
        for row in reader:
            data.append({headers[i]: row[i+1] for i in range(len(headers))})

    with open(json_file_path, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return json_file_path

# Open file picker window
root = tk.Tk()
root.withdraw()  # Hide the root window
csv_file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])

if csv_file_path:
    json_file_path = csv_file_path.replace(".csv", ".json")
    output_path = csv_to_json(csv_file_path, json_file_path)
    print(f"JSON file saved at: {output_path}")
else:
    print("No file selected.")
