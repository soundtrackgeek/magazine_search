from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import glob

app = Flask(__name__)

def load_magazines():
    magazines_data = []
    csv_files = glob.glob('magazines/*.csv')
    
    for file in csv_files:
        magazine_name = os.path.splitext(os.path.basename(file))[0]
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            magazines_data.append({
                'magazine': magazine_name,
                'page': row['Page Number'],
                'content': row['Page Information']
            })
    return magazines_data

# Load magazines data at startup
MAGAZINES_DATA = load_magazines()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    results = []
    for item in MAGAZINES_DATA:
        if query in item['content'].lower():
            results.append(item)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
