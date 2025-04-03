import requests
import os

def verify_tika(file_path, tika_url):
    try:
        with open(file_path, 'rb') as file:
            response = requests.put(tika_url, files={'file': file})

        if response.status_code == 200:
            print("Apache Tika successfully analyzed the file.")
            print("Response from Apache Tika:")
            print(response.text)
        else:
            print("Error analyzing the file:")
            print(f"Status code: {response.status_code}")
            print(f"Response from Apache Tika: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    folder_path = "documents"  # Specify the "documents" folder
    tika_url = "http://localhost:9998/tika"

    # Create the 'documents' folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Get all files in the 'documents' folder
    file_names = os.listdir(folder_path)
    file_paths = [os.path.join(folder_path, file_name) for file_name in file_names if os.path.isfile(os.path.join(folder_path, file_name))]

    for file_path in file_paths:
        verify_tika(file_path, tika_url)
        print(f"Processed file: {file_path}")