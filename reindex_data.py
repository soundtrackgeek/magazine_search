from elasticsearch_client import recreate_index
from database import SessionLocal, Magazine
from elasticsearch_client import index_document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reindex_all_data():
    """Reindex all magazine data"""
    # Recreate the index with new mapping
    if not recreate_index():
        logger.error("Failed to recreate index")
        return False
    
    # Get all magazines from the database
    db = SessionLocal()
    try:
        magazines = db.query(Magazine).all()
        logger.info(f"Found {len(magazines)} magazines to index")
        
        # Index each magazine
        for magazine in magazines:
            try:
                index_document(magazine)
            except Exception as e:
                logger.error(f"Error indexing magazine {magazine.id}: {str(e)}")
        
        logger.info("Reindexing completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during reindexing: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    reindex_all_data()
