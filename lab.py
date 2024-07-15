import pandas as pd
import re

# Function to parse the file and create a DataFrame
def parse_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    data = []
    pattern = re.compile(r"\((\d+), '([\d-]+ [\d:]+)'\)")
    
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            id = int(match.group(1))
            date = match.group(2)
            data.append((id, date))
    
    return pd.DataFrame(data, columns=['ID', 'DATE'])

# Read and parse the file
file_path = 'file.txt'
data = parse_file(file_path)

# Convert the DATE column to datetime
data['DATE'] = pd.to_datetime(data['DATE'])

# Find the minimum date for each ID
min_dates = data.groupby('ID')['DATE'].min().reset_index()

# Sort the results by ID
min_dates = min_dates.sort_values(by='ID')

# Format the output with parentheses and commas
formatted_min_dates = min_dates.apply(lambda row: f"({row['ID']},'{row['DATE']}'),", axis=1)

# Write the result to a new file
output_file_path = 'min_dates.txt'
with open(output_file_path, 'w') as file:
    for line in formatted_min_dates:
        file.write(f"{line}\n")

print(f'Minimum dates for each ID have been written to {output_file_path}')
