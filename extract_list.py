import csv

def get_object_list(csv_file_path):
    objects = []

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            obj = row.get('Object')
            if obj:
                objects.append(obj.strip())

    return objects

# Example usage
csv_file_path = 'blippi_objects.csv'  # Replace with the path to your actual CSV file
object_list = get_object_list(csv_file_path)

print("Object list:")
print(object_list)
