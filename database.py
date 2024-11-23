from sqlalchemy import create_engine, Column, Integer, String, Text, Index
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

    # Create a GiST index for faster text search
    __table_args__ = (
        Index('idx_content_pattern_ops', 'content', postgresql_ops={'content': 'text_pattern_ops'}),
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
