from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database setup
DATABASE_URL = "sqlite:///quiz_data.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()


# Table to store extracted PDF text
class PDFText(Base):
    __tablename__ = "pdf_texts"
    id = Column(Integer, primary_key=True)
    pdf_text = Column(Text)  # Store the entire extracted text from the PDF


# Create the database
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Function to add extracted text to the database
def add_pdf_text(text):
    session = Session()
    pdf_entry = PDFText(pdf_text=text)
    session.add(pdf_entry)
    session.commit()
    session.close()


# Function to get the latest extracted text
def get_latest_pdf_text():
    session = Session()
    pdf_text = session.query(PDFText).order_by(PDFText.id.desc()).first()
    session.close()
    return pdf_text.pdf_text if pdf_text else ""
