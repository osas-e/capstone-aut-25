import csv
import json
import os
import pandas as pd
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

# Convert .xlsx to JSON
def xlsx_to_json(xlsx_file_path, json_file_path):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(xlsx_file_path, engine='openpyxl')  # engine='openpyxl' is recommended for xlsx

    # Process columns 2 to 14
    headers = df.columns[1:14].tolist()
    print(f"Detected Headers (Columns 2-14): {headers}")

    data = []

    # Iterate over rows
    for _, row in df.iterrows():
        # Create a dictionary for columns 2-14
        row_dict = {headers[i]: row[i+1] for i in range(len(headers))}

        # Skip rows where all values in the selected columns are empty
        if all(pd.isna(value) or value == '' for value in row_dict.values()):
            continue

        data.append(row_dict)

    print(f"Total Rows Processed: {len(data)}")

    # Write JSON output
    with open(json_file_path, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return json_file_path

# Open file picker window to import dataset
root = tk.Tk()
root.withdraw()  # Hide the root window
file_path = filedialog.askopenfilename(title="Select CSV or XLSX File", filetypes=[("CSV files", "*.csv"),("XLSX files", "*.xlsx")])

if file_path:

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".xlsx":
        json_file_path = file_path.replace(".xlsx", ".json")
        output_path = xlsx_to_json(file_path, json_file_path)
        print(f"JSON file saved at: {output_path}")

    elif file_extension == ".csv":     
        json_file_path = file_path.replace(".csv", ".json")
        output_path = csv_to_json(file_path, json_file_path)
        print(f"JSON file saved at: {output_path}")

else:
    print("No file selected.")
