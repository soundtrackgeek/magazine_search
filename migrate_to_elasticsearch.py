from database import SessionLocal, Magazine
from elasticsearch_client import es_client, create_index, INDEX_NAME
from elasticsearch.helpers import bulk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_documents():
    """Generator function to fetch documents from PostgreSQL"""
    db = SessionLocal()
    try:
        magazines = db.query(Magazine).all()
        for magazine in magazines:
            yield {
                "_index": INDEX_NAME,
                "_source": {
                    "magazine_name": magazine.magazine_name,
                    "page_number": magazine.page_number,
                    "content": magazine.content,
                    "cover_image": magazine.cover_image
                }
            }
    finally:
        db.close()

def migrate_data():
    """Migrate data from PostgreSQL to Elasticsearch"""
    logger.info("Creating Elasticsearch index...")
    create_index()
    
    logger.info("Starting data migration...")
    success, failed = bulk(es_client, get_documents())
    logger.info(f"Migration completed. Successfully indexed {success} documents. Failed: {failed}")

if __name__ == "__main__":
    migrate_data()
