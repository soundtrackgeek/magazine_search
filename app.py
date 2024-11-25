from flask import Flask, render_template, jsonify, request, send_from_directory
from database import SessionLocal, Magazine
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
            query = data.get('query', '').lower()
            magazine_filter = data.get('magazine', 'All')
        else:
            query = request.args.get('q', '').lower()
            magazine_filter = request.args.get('magazine', 'All')
        
        if not query:
            return jsonify({'results': []})
        
        # Search using Elasticsearch
        search_results = search_magazines(query, magazine_filter)
        
        # Format results
        results = []
        for hit in search_results:
            source = hit['_source']
            results.append({
                'magazine': source['magazine_name'],
                'page': source['page_number'],
                'content': source['content'],
                'cover_image': source['cover_image'],
                'search_query': query
            })
        
        logger.debug(f"Search query '{query}' with magazine filter '{magazine_filter}' returned {len(results)} results")
        return jsonify({'results': results})
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add route to serve magazine covers
@app.route('/magazine_covers/<path:filename>')
def serve_cover(filename):
    return send_from_directory('magazine_covers', filename)

if __name__ == '__main__':
    app.run(debug=True)
