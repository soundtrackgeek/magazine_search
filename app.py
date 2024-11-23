from flask import Flask, render_template, jsonify, request, send_from_directory
from sqlalchemy import text
from database import SessionLocal, Magazine
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
        
        db = get_db()
        
        # Build the query using full-text search
        search_query = db.query(Magazine)
        
        # Apply magazine filter if not "All"
        if magazine_filter != "All":
            search_query = search_query.filter(Magazine.magazine_name.startswith(magazine_filter))
        
        # Apply full-text search
        search_query = search_query.filter(
            text("content_tsv @@ plainto_tsquery('english', :query)")
        ).params(query=query)
        
        # Add ranking to sort by relevance
        search_query = search_query.order_by(
            text("ts_rank(content_tsv, plainto_tsquery('english', :query)) DESC")
        ).params(query=query)
        
        # Execute query and format results
        results = []
        for item in search_query.all():
            results.append({
                'magazine': item.magazine_name,
                'page': item.page_number,
                'content': item.content,
                'cover_image': item.cover_image,
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
