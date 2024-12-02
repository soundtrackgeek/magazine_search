import csv
import os
import re

def extract_info_from_filename(filename):
    # Extract magazine name, date, and page number using regex
    pattern = r"(.*?)\s*\((.*?)\)\s*Page\s*(\d+)\.jpg"
    match = re.match(pattern, filename)
    if match:
        mag_name = match.group(1).strip()
        date = match.group(2).strip()
        page_num = int(match.group(3))  # Convert to int to remove leading zeros
        return mag_name, date, page_num
    return None

def update_magazine_info():
    # Read the fixed_mags.csv file
    fixed_mags = {}
    with open('fixed_mags.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Filename'] and row['Page Information']:
                fixed_mags[row['Filename']] = row['Page Information']

    # Process each entry in fixed_mags
    for filename, page_info in fixed_mags.items():
        info = extract_info_from_filename(filename)
        if not info:
            print(f"Could not parse filename: {filename}")
            continue

        mag_name, date, page_num = info
        csv_filename = f"{mag_name} ({date}).csv"
        csv_path = os.path.join('magazines', csv_filename)

        if not os.path.exists(csv_path):
            print(f"Magazine CSV not found: {csv_path}")
            continue

        # Read the magazine CSV
        rows = []
        updated = False
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            for row in reader:
                if row['Page Number'].isdigit() and int(row['Page Number']) == page_num:
                    row['Page Information'] = page_info
                    updated = True
                rows.append(row)

        if updated:
            # Write back the updated content
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
            print(f"Updated page {page_num} in {csv_filename}")
        else:
            print(f"Page {page_num} not found in {csv_filename}")

if __name__ == "__main__":
    update_magazine_info()
