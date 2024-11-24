import pandas as pd
import os
import glob
from database import SessionLocal, Magazine, engine, Base
import logging
from sqlalchemy import text, exists

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Create tables and triggers if they don't exist"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create trigger for automatic tsvector updates if it doesn't exist
    with engine.connect() as conn:
        # Check if trigger exists
        trigger_exists = conn.execute(text("""
            SELECT 1 FROM pg_trigger WHERE tgname = 'magazines_tsvector_update';
        """)).scalar() is not None
        
        if not trigger_exists:
            conn.execute(text("""
                CREATE TRIGGER magazines_tsvector_update BEFORE INSERT OR UPDATE
                ON magazines FOR EACH ROW EXECUTE FUNCTION
                tsvector_update_trigger(content_tsv, 'pg_catalog.english', content);
            """))
            conn.commit()
            logger.info("Created tsvector update trigger")

def import_magazines(force_reimport=False):
    """Import magazines from CSV files and update existing entries if content has changed
    
    Args:
        force_reimport (bool): If True, drop and recreate all tables
    """
    if force_reimport:
        logger.info("Dropping existing tables for complete reimport")
        Base.metadata.drop_all(bind=engine)
    
    setup_database()
    
    # Get database session
    db = SessionLocal()
    
    try:
        csv_files = glob.glob(os.path.join(os.path.dirname(__file__), 'magazines', '*.csv'))
        logger.info(f"Found {len(csv_files)} CSV files to process")
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for file in csv_files:
            try:
                magazine_name = os.path.splitext(os.path.basename(file))[0]
                logger.info(f"Processing {magazine_name}")
                
                # Add cover image path
                cover_path = f'/magazine_covers/{magazine_name}.jpg'
                df = pd.read_csv(file)
                
                # Get existing magazine entries
                existing_entries = {
                    (entry.page_number, entry.content): entry 
                    for entry in db.query(Magazine).filter(Magazine.magazine_name == magazine_name)
                }
                
                # Track processed pages to identify deleted pages
                processed_pages = set()
                
                # Import/update each row
                for _, row in df.iterrows():
                    page_number = row['Page Number']
                    content = row['Page Information']
                    key = (page_number, content)
                    processed_pages.add(page_number)
                    
                    if key in existing_entries:
                        # Content hasn't changed, skip
                        skipped_count += 1
                        continue
                    
                    # Check if page exists but content is different
                    existing_page = next(
                        (entry for (p, _), entry in existing_entries.items() if p == page_number),
                        None
                    )
                    
                    if existing_page:
                        # Update existing page
                        existing_page.content = content
                        updated_count += 1
                        logger.info(f"Updated {magazine_name} page {page_number}")
                    else:
                        # Add new page
                        magazine_entry = Magazine(
                            magazine_name=magazine_name,
                            page_number=page_number,
                            content=content,
                            cover_image=cover_path
                        )
                        db.add(magazine_entry)
                        imported_count += 1
                
                # Remove pages that no longer exist in the CSV
                for (page_number, _), entry in existing_entries.items():
                    if page_number not in processed_pages:
                        db.delete(entry)
                        logger.info(f"Deleted {magazine_name} page {page_number} - no longer in CSV")
                
                # Commit after each file
                db.commit()
                logger.info(f"Successfully processed {magazine_name}")
                
            except Exception as e:
                logger.error(f"Error processing file {file}: {str(e)}")
                db.rollback()
                error_count += 1
        
        logger.info(f"""Import complete:
            - {imported_count} new pages imported
            - {updated_count} pages updated
            - {skipped_count} pages unchanged
            - {error_count} errors""")
        
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import magazine data into PostgreSQL database')
    parser.add_argument('--force-reimport', action='store_true', 
                      help='Drop and recreate all tables before importing')
    args = parser.parse_args()
    
    import_magazines(force_reimport=args.force_reimport)
