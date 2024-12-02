import csv
import os
import shutil
from pathlib import Path
import re
from collections import defaultdict

def pad_page_number(page_num):
    # Convert to int to remove leading zeros if any
    num = int(page_num)
    # Return both possible formats (01 and 001)
    return [f"{num:02d}", f"{num:03d}"]

def build_file_cache(source_dir):
    """Build a cache of all files and their paths"""
    file_cache = defaultdict(list)
    print("Building file cache...")
    for root, _, files in os.walk(source_dir):
        root_path = Path(root)
        root_lower = root_path.as_posix().lower()
        for file in files:
            file_cache[root_lower].append((file, root_path / file))
    print("File cache built.")
    return file_cache

def find_and_copy_files():
    # Ensure destination directory exists
    dest_dir = Path(r"c:\_code\magazine_scraper\_TOFIX")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Build cache of files
    source_dir = Path(r"m:\pdftoimagebackup")
    file_cache = build_file_cache(source_dir)
    
    # Process CSV file
    copied_count = 0
    with open("magazine_errors.csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        magazines_to_process = list(reader)
        total_magazines = len(magazines_to_process)
        
        for idx, row in enumerate(magazines_to_process, 1):
            magazine_name = row['Magazine Name']
            page_number = row['Page Number']
            page_formats = pad_page_number(page_number)
            
            # Find matching directory
            magazine_lower = magazine_name.lower()
            matching_dirs = [path for path in file_cache.keys() if magazine_lower in path]
            
            for dir_path in matching_dirs:
                for file, full_path in file_cache[dir_path]:
                    file_lower = file.lower()
                    # Check each page format
                    for fmt in page_formats:
                        # Create exact match patterns
                        patterns = [
                            f"{magazine_name} Page {fmt}.jpg".lower(),
                            f"{magazine_name} page {fmt}.jpg".lower()
                        ]
                        
                        # Check for exact match
                        if file_lower in patterns:
                            dest_file = dest_dir / file
                            try:
                                if not dest_file.exists():
                                    shutil.copy2(full_path, dest_file)
                                    copied_count += 1
                                    print(f"[{idx}/{total_magazines}] Copied: {file}")
                            except Exception as e:
                                print(f"Error copying {file}: {str(e)}")
                            break  # Found a match, no need to check other formats
            
            if idx % 10 == 0:
                print(f"Processed {idx}/{total_magazines} magazines...")

    print(f"\nFinished! Copied {copied_count} files.")

if __name__ == "__main__":
    print("Starting to copy error pages...")
    find_and_copy_files()
    print("Finished copying error pages.")
