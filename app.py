from flask import Flask, render_template, jsonify, request, send_from_directory
from elasticsearch_client import search_magazines
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        if request.method == 'POST':
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Invalid JSON data"}), 400
            
            # Get the original query without converting to lowercase
            query = data.get('query', '')
            magazines = data.get('magazines', ['All'])
            page = data.get('page', 1)
        else:
            query = request.args.get('q', '')
            magazines = request.args.getlist('magazines[]') or ['All']
            page = int(request.args.get('page', 1))
        
        if not query:
            return jsonify({'results': []})
        
        # Search using Elasticsearch
        search_response = search_magazines(query, magazines, page)
        
        # Format results
        results = []
        for hit in search_response['hits']:
            source = hit['_source']
            results.append({
                'magazine': source['magazine_name'],
                'issue': source.get('issue_number', ''),
                'date': source.get('publication_date', ''),
                'page': source['page_number'],
                'content': source['content'],
                'cover_image': source['cover_image'],
                'search_query': query
            })
        
        # Add pagination info to response
        response = {
            'results': results,
            'total_hits': search_response['total_hits'],
            'current_page': search_response['page'],
            'total_pages': search_response['total_pages'],
            'page_size': search_response['page_size']
        }
        
        logger.debug(f"Search query '{query}' with magazine filters '{magazines}' returned {len(results)} results")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add route to serve magazine covers
@app.route('/magazine_covers/<path:filename>')
def serve_cover(filename):
    return send_from_directory('magazine_covers', filename)

if __name__ == '__main__':
    app.run(debug=True)
