import pandas as pd
import os
import glob
from database import SessionLocal, Magazine, engine, Base
import logging
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_magazines():
    # Create tables
    Base.metadata.drop_all(bind=engine)  # Drop existing tables
    Base.metadata.create_all(bind=engine)
    
    # Create trigger for automatic tsvector updates
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TRIGGER magazines_tsvector_update BEFORE INSERT OR UPDATE
            ON magazines FOR EACH ROW EXECUTE FUNCTION
            tsvector_update_trigger(content_tsv, 'pg_catalog.english', content);
        """))
        conn.commit()
    
    # Get database session
    db = SessionLocal()
    
    try:
        csv_files = glob.glob(os.path.join(os.path.dirname(__file__), 'magazines', '*.csv'))
        logger.info(f"Found {len(csv_files)} CSV files to import")
        
        for file in csv_files:
            try:
                magazine_name = os.path.splitext(os.path.basename(file))[0]
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
                
            except Exception as e:
                logger.error(f"Error importing file {file}: {str(e)}")
                db.rollback()
        
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    import_magazines()
