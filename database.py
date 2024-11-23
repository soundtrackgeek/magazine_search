from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/magazine_search"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Magazine(Base):
    __tablename__ = "magazines"

    id = Column(Integer, primary_key=True, index=True)
    magazine_name = Column(String, index=True)
    page_number = Column(Integer)
    content = Column(Text)
    cover_image = Column(String)

    # Add full-text search index
    __table_args__ = {
        'postgresql_using': 'btree',
        'postgresql_ops': {'content': 'text_pattern_ops'}
    }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
