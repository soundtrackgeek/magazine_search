# Magazine Search

A web-based application that allows you to search through magazine content efficiently. This project provides a user-friendly interface to search through digitized magazine content and view magazine covers.

## Features

- Full-text search across multiple magazines using PostgreSQL
- Relevance-based search results
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
- PostgreSQL 12 or higher
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

3. Install PostgreSQL:

   - On Windows, download and install PostgreSQL from https://www.postgresql.org/download/
   - On Linux/Mac, use your package manager to install PostgreSQL

4. Set up PostgreSQL:

   - Create a database named `magazine_search`
   - Default configuration uses:
     - Username: postgres
     - Password: postgres
     - Host: localhost
     - Port: 5432
   - On Windows, use the following command to create the database:
     ```bash
     psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE magazine_search;"
     ```
   - On Linux/Mac, use the following command:
     ```bash
     sudo -u postgres createdb -h localhost -p 5432 magazine_search
     ```
   - To use different settings, update `DATABASE_URL` in `database.py`

5. Import magazine data:

   ```bash
   # First time or to add new magazines
   python import_data.py

   # To completely rebuild the database
   python import_data.py --force-reimport
   ```

## Project Structure

- `app.py` - Main Flask application file
- `database.py` - Database configuration and models
- `import_data.py` - Data import script
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
   - Results are sorted by relevance
   - View results with page numbers and magazine covers

## Adding New Magazines

1. Add new magazine CSV files to the `magazines/` directory
2. Add corresponding cover images to `magazine_covers/`
3. Run the import script:
   ```bash
   python import_data.py
   ```
   - This will only import new magazines
   - Existing magazines will be skipped
   - Use `--force-reimport` flag to rebuild everything

## Dependencies

- Flask 2.3.3 - Web framework
- SQLAlchemy 2.0.23 - Database ORM
- psycopg2-binary 2.9.9 - PostgreSQL adapter
- Pandas 2.0.3 - Data handling

## License

This project is licensed under the terms included in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
