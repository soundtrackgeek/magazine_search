# Magazine Search

A web-based application that allows you to search through magazine content efficiently. This project provides a user-friendly interface to search through digitized magazine content and view magazine covers.

## Features

- Full-text search across multiple magazines
- Magazine cover image display
- Filter search results by specific magazines
- Page number references for search results
- Web-based interface for easy access

## Prerequisites

- Python 3.8 or higher
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

## Project Structure

- `app.py` - Main Flask application file
- `magazines/` - Directory containing CSV files with magazine content
- `magazine_covers/` - Directory containing magazine cover images
- `templates/` - HTML templates for the web interface
- `requirements.txt` - Python dependencies

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use the search bar to find content across magazines
   - Enter your search query
   - Optionally filter by specific magazine
   - View results with page numbers and magazine covers

## Dependencies

- Flask 2.3.3 - Web framework
- Pandas 2.0.3 - Data handling

## License

This project is licensed under the terms included in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
