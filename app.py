from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import glob
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_magazines():
    magazines_data = []
    csv_files = glob.glob(os.path.join(os.path.dirname(__file__), 'magazines', '*.csv'))
    logger.debug(f"Found CSV files: {csv_files}")
    
    for file in csv_files:
        try:
            magazine_name = os.path.splitext(os.path.basename(file))[0]
            logger.debug(f"Reading file: {file}")
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                magazines_data.append({
                    'magazine': magazine_name,
                    'page': row['Page Number'],
                    'content': row['Page Information']
                })
        except Exception as e:
            logger.error(f"Error reading file {file}: {str(e)}")
    
    logger.debug(f"Total entries loaded: {len(magazines_data)}")
    return magazines_data

# Load magazines data at startup
MAGAZINES_DATA = load_magazines()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    try:
        query = request.args.get('q', '').lower()
        magazine_filter = request.args.get('magazine', 'All')
        
        if not query:
            return jsonify([])
        
        results = []
        for item in MAGAZINES_DATA:
            # Apply magazine filter if not "All"
            if magazine_filter != "All" and not item['magazine'].startswith(magazine_filter):
                continue
                
            # Only search in the content, not in the magazine title
            if query in str(item['content']).lower():
                # Add the original query to help with highlighting
                item_copy = item.copy()
                item_copy['search_query'] = query
                results.append(item_copy)
        
        logger.debug(f"Search query '{query}' with magazine filter '{magazine_filter}' returned {len(results)} results")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
