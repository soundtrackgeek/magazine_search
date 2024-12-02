import os
import csv
import re

def find_errors_in_magazines():
    # Error patterns to search for
    error_patterns = [
        r'Error: block_reason',
        r'Error: finish_reason',
        r'Error: The read operation timed out',
        r'Error: 500',
        r'Error: 503',
        r'Error: EOF',
        r'HttpError 503',
        r'Error: 429',
        r'WinError 10060'
    ]
    
    # Compile all patterns
    compiled_patterns = [re.compile(pattern) for pattern in error_patterns]
    
    # Results list to store all findings
    results = []
    
    # Walk through the magazines directory
    magazines_dir = os.path.join(os.path.dirname(__file__), 'magazines')
    
    for root, _, files in os.walk(magazines_dir):
        for file in files:
            if file.endswith('.csv'):
                magazine_name = os.path.splitext(file)[0]
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        csv_reader = csv.DictReader(f)
                        for row in csv_reader:
                            page_number = row.get('Page Number', '')
                            # Check each field in the row for errors
                            row_text = str(row)
                            for pattern in compiled_patterns:
                                match = pattern.search(row_text)
                                if match:
                                    error_msg = match.group(0)
                                    results.append([magazine_name, page_number, error_msg])
                                
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
    
    # Write results to CSV
    output_file = os.path.join(os.path.dirname(__file__), 'magazine_errors.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Magazine Name', 'Page Number', 'Error Message'])
        writer.writerows(results)
    
    print(f"Error analysis complete. Results written to {output_file}")
    print(f"Found {len(results)} errors across all magazine files.")

if __name__ == '__main__':
    find_errors_in_magazines()
