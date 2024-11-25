import pandas as pd
import os
import glob
import logging
from elasticsearch_client import es_client, create_index, INDEX_NAME
from elasticsearch.helpers import bulk
import json
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_processed_files():
    """Get list of already processed files and their last modified times"""
    processed_file = "processed_files.json"
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            return json.load(f)
    return {}

def save_processed_files(processed):
    """Save the list of processed files"""
    with open("processed_files.json", 'w') as f:
        json.dump(processed, f)

def get_documents_from_csv(file_path):
    """Generator function to create Elasticsearch documents from CSV"""
    full_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Parse magazine name, issue number, and date from filename
    # Example formats: "Magazine Name Issue XX" or "Magazine Name - Volume X"
    parts = full_name.split(" Issue ")
    if len(parts) > 1:
        magazine_name = parts[0]
        issue_number = f"Issue {parts[1]}"
    else:
        parts = full_name.split(" - Volume ")
        if len(parts) > 1:
            magazine_name = parts[0]
            issue_number = f"Volume {parts[1]}"
        else:
            magazine_name = full_name
            issue_number = ""
    
    # Extract date if present (assuming it's in parentheses at the end)
    date_match = re.search(r'\((.*?)\)$', magazine_name)
    if date_match:
        publication_date = date_match.group(1)
        magazine_name = magazine_name.replace(f"({publication_date})", "").strip()
    else:
        publication_date = ""
    
    cover_path = f'/magazine_covers/{os.path.splitext(os.path.basename(file_path))[0]}.jpg'
    
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        yield {
            "_index": INDEX_NAME,
            "_source": {
                "magazine_name": magazine_name,
                "issue_number": issue_number,
                "publication_date": publication_date,
                "page_number": row['Page Number'],
                "content": row['Page Information'],
                "cover_image": cover_path
            }
        }

def import_magazines(force_reimport=False):
    """Import magazines from CSV files into Elasticsearch
    
    Args:
        force_reimport (bool): If True, recreate the index and import all files
    """
    if force_reimport:
        logger.info("Dropping existing index for complete reimport")
        if es_client.indices.exists(index=INDEX_NAME):
            es_client.indices.delete(index=INDEX_NAME)
    
    # Create index if it doesn't exist
    create_index()
    
    # Get list of processed files
    processed_files = {} if force_reimport else get_processed_files()
    
    # Find all CSV files
    csv_files = glob.glob(os.path.join(os.path.dirname(__file__), 'magazines', '*.csv'))
    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    for file in csv_files:
        try:
            # Check if file has been modified since last import
            last_modified = os.path.getmtime(file)
            if not force_reimport and file in processed_files and processed_files[file] >= last_modified:
                logger.info(f"Skipping {file} - already processed")
                continue
            
            logger.info(f"Processing {file}")
            
            # Delete existing documents for this magazine if any
            magazine_name = os.path.splitext(os.path.basename(file))[0]
            es_client.delete_by_query(index=INDEX_NAME, body={
                "query": {
                    "term": {"magazine_name": magazine_name}
                }
            })
            
            # Bulk index the documents
            success, failed = bulk(es_client, get_documents_from_csv(file))
            logger.info(f"Indexed {success} documents. Failed: {failed}")
            
            # Update processed files list
            processed_files[file] = last_modified
            save_processed_files(processed_files)
            
        except Exception as e:
            logger.error(f"Error processing {file}: {str(e)}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import magazine data directly into Elasticsearch')
    parser.add_argument('--force-reimport', action='store_true', 
                      help='Drop existing index and reimport all files')
    args = parser.parse_args()
    
    import_magazines(args.force_reimport)
