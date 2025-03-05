import json
import tkinter as tk
from tkinter import filedialog
import pandas as pd


def xlsx_to_json(xlsx_file_path, json_file_path):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(xlsx_file_path, engine='openpyxl')  # engine='openpyxl' is recommended for xlsx

    # Assuming you want to process columns 2 to 14 (index 1 to 13, since pandas uses 0-based indexing)
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

# File selection and processing
root = tk.Tk()
root.withdraw()
xlsx_file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx")])

if xlsx_file_path:
    json_file_path = xlsx_file_path.replace(".xlsx", ".json")
    output_path = xlsx_to_json(xlsx_file_path, json_file_path)
    print(f"JSON file saved at: {output_path}")
else:
    print("No file selected.")
    




