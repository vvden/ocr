import os
import logging
from datetime import datetime
from PIL import Image as PILImage
import pytesseract
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import schedule
import time
import mysql.connector.errors
import sqlalchemy.exc
import fitz  # PyMuPDF library for PDF processing

# Necessary imports
import fitz  # PyMuPDF library for PDF processing
from PIL import Image as PILImage

# SQLAlchemy database setup
Base = declarative_base()

class TextData(Base):
    __tablename__ = 'text_data'

    id = Column(Integer, primary_key=True)
    image_path = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=False, default='')
    created_at = Column(DateTime, nullable=False, default=datetime.now)

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    filepath = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    words = relationship("Word", back_populates="image")

class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'))
    word = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    image = relationship("Image", back_populates="words")

def init_db():
    engine = create_engine('mysql+mysqlconnector://mysqluser:mysqlpassword@localhost/ocr_db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def perform_ocr():
    logging.info("Performing OCR...")
    session = init_db()
    try:
        for root, dirs, files in os.walk('/opt/images/'):
            for file in files:
                if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf', '.xcf')):
                    image_file = os.path.join(root, file)
                    if not session.query(TextData).filter(TextData.image_path == image_file).first():
                        extracted_text = extract_text(image_file)
                        insert_text_data(session, image_file, extracted_text)
                    else:
                        logging.info(f"Skipping {image_file} as it's already processed.")
        logging.info("OCR completed successfully.")
    except Exception as e:
        logging.error(f"Error performing OCR: {e}")
        img_base_path = '/opt/images/'
        rm_path = img_base_path + file
        os.remove(rm_path)
        perform_ocr()
    finally:
        session.close()

def extract_text(image_file):
    logging.info(f"Extracting text from {image_file}...")
    if image_file.lower().endswith('.pdf'):
        # For PDF files, read text directly
        try:
            with fitz.open(image_file) as pdf_file:
                extracted_text = ""
                for page in pdf_file:
                    extracted_text += page.get_text()
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
            return ""
    elif image_file.lower().endswith('.xcf'):
        # For XCF files, convert to image and use OCR
        try:
            image = PILImage.open(image_file)
            extracted_text = pytesseract.image_to_string(image, lang='eng')
        except Exception as e:
            logging.error(f"Error extracting text from XCF: {e}")
            return ""
    else:
        # For other image files, use pytesseract for OCR
        try:
            image = PILImage.open(image_file)
            extracted_text = pytesseract.image_to_string(image, lang='eng')
        except Exception as e:
            logging.error(f"Error performing OCR: {e}")
            return ""
    logging.info("Text extracted successfully.")
    return extracted_text

def insert_text_data(session, image_file, extracted_text):
    logging.info(f"Inserting data into database for {image_file}...")
    text_data = TextData(image_path=image_file, extracted_text=extracted_text)
    session.add(text_data)
    session.commit()
    logging.info("Data inserted successfully.")

def scheduler():
    logging.info("Starting scheduler...")
    schedule.every().hour.do(perform_ocr)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(filename='ocr.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    tessdata_prefix = "/usr/share/tessdata"
    os.environ["TESSDATA_PREFIX"] = tessdata_prefix

    try:
        perform_ocr()
        logging.info("Tesseract initialized with language packs successfully.")
    except Exception as e:
        logging.error(f"Error initializing Tesseract: {e}")
    perform_ocr()
