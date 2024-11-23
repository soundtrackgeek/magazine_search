from sqlalchemy import create_engine, Column, Integer, String, Text, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import TSVECTOR

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
    content_tsv = Column(TSVECTOR)

    __table_args__ = (
        Index(
            'idx_content_fts',
            'content_tsv',
            postgresql_using='gin'
        ),
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
