from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
import urllib3
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Elasticsearch configuration
ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200
INDEX_NAME = "magazines"

# Initialize Elasticsearch client
es_client = Elasticsearch(
    hosts=[{
        'scheme': 'http',  
        'host': ELASTICSEARCH_HOST,
        'port': ELASTICSEARCH_PORT
    }],
    basic_auth=("elastic", os.getenv('ELASTICSEARCH_PASSWORD')),
    verify_certs=False,
    retry_on_timeout=True,
    max_retries=5,
    request_timeout=300
)

def recreate_index():
    """Delete and recreate the magazine index"""
    try:
        if es_client.indices.exists(index=INDEX_NAME):
            es_client.indices.delete(index=INDEX_NAME)
            logger.info(f"Deleted index {INDEX_NAME}")
        create_index()
        logger.info("Index recreated successfully")
        return True
    except Exception as e:
        logger.error(f"Error recreating index: {str(e)}")
        return False

def create_index():
    """Create the magazine index with appropriate mappings if it doesn't exist"""
    index_body = {
        "mappings": {
            "properties": {
                "magazine_name": {
                    "type": "keyword",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "issue_number": {
                    "type": "keyword"
                },
                "publication_date": {
                    "type": "keyword"
                },
                "page_number": {"type": "integer"},
                "content": {
                    "type": "text",
                    "analyzer": "english"
                },
                "cover_image": {"type": "keyword"}
            }
        },
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
    }
    
    try:
        # Only create the index if it doesn't exist
        if not es_client.indices.exists(index=INDEX_NAME):
            es_client.indices.create(index=INDEX_NAME, body=index_body)
            logger.info(f"Created new index {INDEX_NAME}")
        else:
            logger.info(f"Index {INDEX_NAME} already exists")
            
    except Exception as e:
        logger.error(f"Error during index creation: {str(e)}")

def index_document(magazine_doc):
    """Index a single magazine document"""
    doc = {
        'magazine_name': magazine_doc.magazine_name,
        'issue_number': magazine_doc.issue_number,
        'publication_date': magazine_doc.publication_date,
        'page_number': magazine_doc.page_number,
        'content': magazine_doc.content,
        'cover_image': magazine_doc.cover_image
    }
    
    es_client.index(index=INDEX_NAME, body=doc)

def search_magazines(query, magazines=["All"], page=1, page_size=100):
    """
    Search for magazines using Elasticsearch with pagination support
    
    Args:
        query (str): The search query
        magazines (list): List of magazine names to filter by, ["All"] for no filter
        page (int): Page number (1-based)
        page_size (int): Number of results per page
        
    Returns:
        dict: Contains search hits and pagination info
    """
    from_idx = (page - 1) * page_size
    
    # Parse the query to handle NOT operations
    must_terms = []
    must_not_terms = []
    
    # Split the query into terms, preserving quoted phrases
    # First replace "NOT" with "-" for consistency
    query = query.replace(" NOT ", " -")
    
    # Split by spaces but preserve quoted phrases
    terms = []
    current_term = []
    in_quotes = False
    
    for char in query + ' ':  # Add space to handle last term
        if char == '"':
            in_quotes = not in_quotes
            current_term.append(char)
        elif char == ' ' and not in_quotes:
            if current_term:
                terms.append(''.join(current_term))
                current_term = []
        else:
            current_term.append(char)
    
    # Process each term
    for term in terms:
        # Convert content terms to lowercase but preserve operators
        if term in ('AND', 'OR', 'NOT'):
            continue
        
        if term.startswith('-'):
            # Remove the - and add to must_not
            clean_term = term[1:].lower()
            if clean_term:  # Only add if there's something after the -
                must_not_terms.append(clean_term)
        else:
            # Remove quotes if present and convert to lowercase
            clean_term = term.strip('"').lower()
            if clean_term:
                must_terms.append(clean_term)
    
    # Construct the bool query
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "content": {
                                "query": " ".join(must_terms),
                                "operator": "and"
                            }
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {
                "content": {}
            }
        }
    }
    
    # Add must_not clauses if there are any NOT terms
    if must_not_terms:
        search_body["query"]["bool"]["must_not"] = [
            {"match": {"content": {"query": term, "operator": "and"}}} 
            for term in must_not_terms
        ]
    
    # Add magazine filter if not "All"
    if "All" not in magazines:
        if "filter" not in search_body["query"]["bool"]:
            search_body["query"]["bool"]["filter"] = []
        
        # Log magazine names being filtered
        logger.debug(f"Filtering for magazines: {magazines}")
        
        magazine_filter = {
            "bool": {
                "should": [
                    {
                        "prefix": {
                            "magazine_name": magazine
                        }
                    } for magazine in magazines
                ]
            }
        }
        search_body["query"]["bool"]["filter"].append(magazine_filter)
        
        # Log the magazine filter
        logger.debug(f"Magazine filter: {magazine_filter}")
    
    # Log the search body for debugging
    logger.debug(f"Elasticsearch query: {search_body}")
    
    # First, let's check what magazine names exist in the index
    sample_query = {
        "size": 0,
        "aggs": {
            "magazine_names": {
                "terms": {
                    "field": "magazine_name",
                    "size": 100
                }
            }
        }
    }
    
    sample_results = es_client.search(
        index=INDEX_NAME,
        body=sample_query
    )
    
    logger.debug("Available magazine names in index:")
    for bucket in sample_results['aggregations']['magazine_names']['buckets']:
        logger.debug(f"- {bucket['key']} ({bucket['doc_count']} documents)")
    
    results = es_client.search(
        index=INDEX_NAME,
        body=search_body,
        size=page_size,
        from_=from_idx
    )
    
    total_hits = results['hits']['total']['value']
    total_pages = (total_hits + page_size - 1) // page_size
    
    return {
        'hits': results['hits']['hits'],
        'total_hits': total_hits,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages
    }
