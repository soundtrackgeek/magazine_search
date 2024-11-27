# Magazine Search

A web-based application that allows you to search through magazine content efficiently. This project provides a user-friendly interface to search through digitized magazine content and view magazine covers.

## Features

- Full-text search across multiple magazines using Elasticsearch
- Advanced text analysis and relevance scoring
- Magazine cover image display
- Filter search results by specific magazines
- Page number references for search results
- Web-based interface for easy access

## Magazines

- ACE
- Amiga Format
- Amiga Power
- Byte
- Commodore User
- COMPUTE!'s Gazette
- Computer & Video Games
- Crash
- Dreamcast Magazine
- Edge
- Family Computing
- GamesMaster
- Hyper
- Info
- Kilobaud Microcomputing
- Laserbug
- MacFormat
- Nintendo World
- Official Xbox UK
- PC Format
- PC Gamer US
- RAZE
- Sinclair User
- The One
- Ultimate Future Games
- VIC Computing
- X360 Magazine
- Your Computer
- Zzap64

## Data Setup

### Magazine Data
1. Add your magazine data in CSV format to the `magazines` folder. Each CSV file should contain the magazine content with appropriate fields.

### Magazine Covers
1. Place your magazine cover images in the `magazine_covers` folder. The images should match the magazine entries in your CSV files.

### Importing Data to Elasticsearch
1. Use the import script to load your magazine data into Elasticsearch:
   ```bash
   python import_to_elasticsearch.py
   ```
2. To force a complete reimport of all data (this will delete existing data first):
   ```bash
   python import_to_elasticsearch.py --force-reimport
   ```

## Prerequisites

- Python 3.8 or higher
- Elasticsearch 8.x
- pip (Python package installer)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/magazine_search.git
   cd magazine_search
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install and Start Elasticsearch:

   - Download Elasticsearch 8.x from the [official website](https://www.elastic.co/downloads/elasticsearch)
   - Extract the downloaded file
   - Start Elasticsearch:
     ```bash
     ./elasticsearch-8.x.x/bin/elasticsearch
     ```
   - Wait for Elasticsearch to start (usually takes a few seconds)

4. Set up environment variables:

   - Copy the `.env-example` file to `.env`:
     ```bash
     cp .env-example .env
     ```
   - Open the `.env` file and replace `your_elasticsearch_password_here` with your actual Elasticsearch password
   - The `.env` file is ignored by git to keep your credentials secure
   - Never commit the `.env` file to version control

5. Run the application:

   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Search Tips

- Use quotes for exact phrase matches: `"computer games"`
- Use AND to require both terms: `gaming AND reviews`
- Use NOT or - to exclude terms: `ocean NOT amiga` or `ocean -amiga`
- Combine operators: `"ocean software" AND games NOT amstrad`
- Filter results by magazine using the dropdown menu

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
