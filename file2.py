import io
import sys
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QDialog, QTableWidgetItem, QLabel
from PyQt5.QtGui import QPixmap
import sqlite3
template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QWidget" name="">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>2</y>
      <width>641</width>
      <height>541</height>
     </rect>
    </property>
    <layout class="QGridLayout" name="gridLayout">
     <item row="0" column="0">
      <widget class="QComboBox" name="comboBox"/>
     </item>
     <item row="0" column="1">
      <widget class="QPushButton" name="pushButton">
       <property name="text">
        <string>Искать</string>
       </property>
      </widget>
     </item>
     <item row="1" column="0">
      <widget class="QLineEdit" name="lineEdit"/>
     </item>
     <item row="2" column="0" colspan="2">
      <widget class="QTableWidget" name="tableWidget"/>
     </item>
    </layout>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>800</width>
     <height>21</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>
"""



class LibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)  

        self.conn = sqlite3.connect("library.db")
        self.cur = self.conn.cursor()

        self.create_table()
        self.load_data()

        self.pushButton.clicked.connect(self.search_by_author)
        self.lineEdit.returnPressed.connect(self.search_by_title)

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                year INTEGER,
                genre TEXT,
                image_path TEXT
            )
        """)
        self.conn.commit()

    def load_data(self):
        self.cur.execute("SELECT * FROM books")
        books = self.cur.fetchall()
        self.tableWidget.setRowCount(len(books))
        self.tableWidget.setColumnCount(5)
        for row, book in enumerate(books):
            for col, data in enumerate(book[1:6]):
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row, col, item)

    def search_by_author(self):
        author = self.comboBox.currentText()
        self.cur.execute("SELECT * FROM books WHERE author=?", (author,))
        books = self.cur.fetchall()
        self.display_books(books)

    def search_by_title(self):
        title = self.lineEdit.text()
        self.cur.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + title + '%',))
        books = self.cur.fetchall()
        self.display_books(books)

    def display_books(self, books):
        self.tableWidget.setRowCount(len(books))
        for row, book in enumerate(books):
            for col, data in enumerate(book[1:6]):
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row, col, item)

    def show_book_info(self, row, col):
        title_item = self.tableWidget.item(row, 0)
        title = title_item.text()

        self.cur.execute("SELECT * FROM books WHERE title=?", (title,))
        book = self.cur.fetchone()

        # Отображение информации о книге
        self.show_info_dialog(book)

    def show_info_dialog(self, book):
        dialog = BookInfoDialog(book)
        dialog.exec_()

class BookInfoDialog(QDialog):
    def __init__(self, book):
        super().__init__()

        # Информация о книге
        title, author, year, genre, image_path = book
        self.setWindowTitle(f"Информация о книге: {title}")

        layout = QVBoxLayout()

        # Добавление информации
        layout.addWidget(QLabel(f"Название: {title}"))
        layout.addWidget(QLabel(f"Автор: {author}"))
        layout.addWidget(QLabel(f"Год издания: {year}"))
        layout.addWidget(QLabel(f"Жанр: {genre}"))

        # Отображение изображения
        pixmap = QPixmap(image_path) if os.path.exists(image_path) else QPixmap("no_image.png")
        pixmap = pixmap.scaledToWidth(200)
        layout.addWidget(QLabel(pixmap=pixmap))

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryApp()
    window.show()
    sys.exit(app.exec_())