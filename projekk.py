import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QAction, QMenu, QFontDialog, QShortcut
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtCore import Qt

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Untitled - Notepad")
        self.setGeometry(100, 100, 600, 600)

        self.text = QTextEdit(self)
        self.text.setFont(QFont("Consolas", 12))
        self.setCentralWidget(self.text)

        self.connectd()

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("Edit")
        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)

        font_menu = menubar.addMenu("Font")
        font_type_action = QAction("Font Type", self)
        font_type_action.triggered.connect(self.choose_font)
        font_menu.addAction(font_type_action)

        new_action.setShortcut(QKeySequence.New)
        open_action.setShortcut(QKeySequence.Open)
        save_action.setShortcut(QKeySequence.Save)

        shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self)
        shortcut.activated.connect(self.select_all)

    def connectd(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="history"
        )
        self.cursor = self.connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS file_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def new_file(self):
        self.text.clear()
        self.setWindowTitle("Untitled - Notepad")

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select a File", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    contents = file.read()
                    self.text.clear()
                    self.text.insertPlainText(contents)
                self.setWindowTitle(f"{filename} - Notepad")
            except Exception as e:
                print(f"An error occurred while opening the file:\n{str(e)}")

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Documents (*.txt);;All Files (*)")
        if filename:
            with open(filename, 'w') as file:
                contents = self.text.toPlainText()
                file.write(contents)
            self.setWindowTitle(f"{filename} - Notepad")

            # Save file history to the database
            self.save_history_to_database(filename, contents)

    def save_history_to_database(self, filename, contents):
        insert_query = "INSERT INTO file_history (filename, content) VALUES (%s, %s)"
        data = (filename, contents)
        self.cursor.execute(insert_query, data)
        self.connection.commit()

    def cut(self):
        self.text.cut()

    def copy(self):
        self.text.copy()

    def paste(self):
        self.text.paste()

    def select_all(self):
        self.text.selectAll()

    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text.setFont(font)

    def closeEvent(self, event):
        self.connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = App()
    mainWin.show()
    sys.exit(app.exec_())
