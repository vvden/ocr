import sys
import mysql.connector
import logging
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QProcess
import textwrap
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, host, user, password, database):
        self.host = 'localhost'
        self.user = 'mysqluser'
        self.password = 'mysqlpassword'
        self.database = 'ocr_db'

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")

    def disconnect(self):
        try:
            self.connection.close()
            logger.info("Disconnected from database")
        except Exception as e:
            logger.error(f"Failed to disconnect from database: {e}")

    def execute_query(self, query, data=None):
        try:
            cursor = self.connection.cursor()
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")

class TextPanel(QWidget):
    def __init__(self, image_path, extracted_text, query):
        super().__init__()

        # Highlight the matched terms in the extracted text
        highlighted_text = self.highlight_terms(extracted_text, query)

        # Create QLabel for image path
        self.image_path_label = QLabel(image_path)
        self.image_path_label.setStyleSheet("font-size: 8pt;")

        # Create QLabel for wrapped text with HTML formatting
        self.text_label = QLabel()
        self.text_label.setTextFormat(Qt.RichText)
        self.text_label.setStyleSheet("font-size: 8pt;")
        self.text_label.setText(highlighted_text)
        self.text_label.setWordWrap(True)

        # Create layout for image path and text labels
        layout = QVBoxLayout()
        layout.addWidget(self.image_path_label)
        layout.addWidget(self.text_label)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def highlight_terms(self, text, query):
        # Use regular expression to find and highlight the matched terms
        highlighted_text = re.sub(rf'({query})', r'<span style="background-color: yellow">\1</span>', text, flags=re.IGNORECASE)
        return highlighted_text

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Image Search")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_images)
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)

        self.results_scroll = QScrollArea()
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)  # Layout to hold search results
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setWidget(self.results_widget)

        self.layout.addLayout(self.search_layout)
        self.layout.addWidget(self.results_scroll)

        self.total_matches_label = QLabel()
        self.layout.addWidget(self.total_matches_label)

        self.db = Database("localhost", "root", "password", "ocr_db")
        self.db.connect()

    def search_images(self):
        query = self.search_input.text()
        result = self.db.execute_query(f"SELECT image_path, extracted_text FROM text_data WHERE extracted_text LIKE '%{query}%'")
        if result:
            # Clear previous results
            for i in reversed(range(self.results_layout.count())):
                self.results_layout.itemAt(i).widget().setParent(None)

            self.total_matches_label.setText(f"Total matches: {len(result)}")

            for row in result:
                image_path, extracted_text = row[0], row[1]
                thumbnail_label = QLabel()
                thumbnail_label.setFixedSize(150, 150)  # Set fixed size for thumbnail
                thumbnail_pixmap = QPixmap(image_path).scaled(150, 150, Qt.KeepAspectRatio)
                thumbnail_label.setPixmap(thumbnail_pixmap)
                thumbnail_label.mousePressEvent = lambda event, path=image_path: self.open_full_image(path)
                
                # Add thumbnail to the results layout
                self.results_layout.addWidget(thumbnail_label)

                # Add image path and extracted text below the thumbnail using TextPanel
                text_panel = TextPanel(image_path, extracted_text, query)
                self.results_layout.addWidget(text_panel)

        else:
            self.total_matches_label.setText("Total matches: 0")
            QMessageBox.information(self, "Info", "No results found.")

    def open_full_image(self, image_path):
        try:
            process = QProcess()
            process.startDetached('gpicview', [image_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open image: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
