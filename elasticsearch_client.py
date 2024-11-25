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
        'scheme': 'https',  
        'host': ELASTICSEARCH_HOST,
        'port': ELASTICSEARCH_PORT
    }],
    basic_auth=("elastic", os.getenv('ELASTICSEARCH_PASSWORD')),
    verify_certs=False  
)

def create_index():
    """Create the magazine index with appropriate mappings"""
    index_body = {
        "mappings": {
            "properties": {
                "magazine_name": {"type": "keyword"},
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
    
    if not es_client.indices.exists(index=INDEX_NAME):
        es_client.indices.create(index=INDEX_NAME, body=index_body)
        logger.info(f"Created index {INDEX_NAME}")

def index_document(magazine_doc):
    """Index a single magazine document"""
    doc = {
        'magazine_name': magazine_doc.magazine_name,
        'page_number': magazine_doc.page_number,
        'content': magazine_doc.content,
        'cover_image': magazine_doc.cover_image
    }
    
    es_client.index(index=INDEX_NAME, body=doc)

def search_magazines(query, magazine_filter="All", page=1, page_size=100):
    """
    Search for magazines using Elasticsearch with pagination support
    
    Args:
        query (str): The search query
        magazine_filter (str): Filter by magazine name, "All" for no filter
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
    
    if magazine_filter != "All":
        if "filter" not in search_body["query"]["bool"]:
            search_body["query"]["bool"]["filter"] = []
        search_body["query"]["bool"]["filter"].append(
            {"prefix": {"magazine_name": magazine_filter}}
        )
    
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