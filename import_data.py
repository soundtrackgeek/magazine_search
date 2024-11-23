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
    """Import magazines from CSV files
    
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
        skipped_count = 0
        error_count = 0
        
        for file in csv_files:
            try:
                magazine_name = os.path.splitext(os.path.basename(file))[0]
                
                # Check if any pages from this magazine already exist
                if not force_reimport and db.query(exists().where(Magazine.magazine_name == magazine_name)).scalar():
                    logger.info(f"Skipping {magazine_name} - already imported")
                    skipped_count += 1
                    continue
                
                logger.info(f"Importing {magazine_name}")
                
                # Add cover image path
                cover_path = f'/magazine_covers/{magazine_name}.jpg'
                df = pd.read_csv(file)
                
                # Import each row
                for _, row in df.iterrows():
                    magazine_entry = Magazine(
                        magazine_name=magazine_name,
                        page_number=row['Page Number'],
                        content=row['Page Information'],
                        cover_image=cover_path
                    )
                    db.add(magazine_entry)
                
                # Commit after each file
                db.commit()
                logger.info(f"Successfully imported {magazine_name}")
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Error importing file {file}: {str(e)}")
                db.rollback()
                error_count += 1
        
        logger.info(f"""Import complete:
            - {imported_count} magazines imported
            - {skipped_count} magazines skipped (already existed)
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
