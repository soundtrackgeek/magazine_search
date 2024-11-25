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
- Computer & Video Games
- Crash
- Dreamcast Magazine
- Edge
- Family Computing
- GamesMaster
- PC Format
- PC Gamer US
- Zzap64

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

4. Configure the application:
   
   - Copy the `.env.example` to `.env`
   - Update the Elasticsearch connection settings in `.env` if needed

5. Run the application:

   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Search Tips

- Use quotes for exact phrase matches: `"computer games"`
- Use AND/OR operators: `gaming AND reviews`
- Use wildcards: `program*` matches programming, programs, etc.
- Filter by magazine using the dropdown menu

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
