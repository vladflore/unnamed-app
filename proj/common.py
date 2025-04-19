import csv
import json

def csv_to_json(csv_file_path):
    """
    Reads a CSV file and converts its data to a JSON object.

    Args:
        csv_file_path (str): Path to the CSV file.

    Returns:
        dict: JSON object containing the CSV data.
    """
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        data = [row for row in reader]
    return json.loads(json.dumps(data))

if __name__ == "__main__":
    csv_file_path = 'exercises_library.csv'
    json_data = csv_to_json(csv_file_path)
    print(json.dumps(json_data, indent=4))