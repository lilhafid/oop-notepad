import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QAction, QMenu, QFontDialog, QShortcut, QMessageBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialogButtonBox
from PyQt5.QtGui import QKeySequence, QFont, QImage, QTextDocumentFragment
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QColor

class ImageResizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Resize Image")
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()

        self.width_label = QLabel("Width:")
        self.width_edit = QLineEdit()
        layout.addWidget(self.width_label)
        layout.addWidget(self.width_edit)

        self.height_label = QLabel("Height:")
        self.height_edit = QLineEdit()
        layout.addWidget(self.height_label)
        layout.addWidget(self.height_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_size(self):
        width = int(self.width_edit.text()) if self.width_edit.text().isdigit() else 0
        height = int(self.height_edit.text()) if self.height_edit.text().isdigit() else 0
        return width, height

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Untitled - Notepad")
        self.setGeometry(100, 100, 600, 600)

        self.text = QTextEdit(self)
        self.text.setFont(QFont("Consolas", 12))
        self.setCentralWidget(self.text)

        self.open_recent_menu = None 
        self.connectd()

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        self.open_recent_menu = QMenu("Open Recent", self)
        file_menu.addMenu(self.open_recent_menu)

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

        highlight_action = QAction("Highlight", self)
        highlight_action.triggered.connect(self.highlight_text)
        edit_menu.addAction(highlight_action)

        underline_action = QAction("Underline", self)
        underline_action.triggered.connect(self.underline_text)
        edit_menu.addAction(underline_action)


        insert_image_action = QAction("Insert Image", self)
        insert_image_action.triggered.connect(self.insert_image)
        edit_menu.addAction(insert_image_action)

        font_menu = menubar.addMenu("Font")
        font_type_action = QAction("Font Type", self)
        font_type_action.triggered.connect(self.choose_font)
        font_menu.addAction(font_type_action)

        new_action.setShortcut(QKeySequence.New)
        open_action.setShortcut(QKeySequence.Open)
        save_action.setShortcut(QKeySequence.Save)

        shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self)
        shortcut.activated.connect(self.select_all)


    def highlight_text(self):
     cursor = self.text.textCursor()
     char_format = QTextCharFormat()
     char_format.setBackground(QColor(Qt.yellow))
     cursor.setCharFormat(char_format)

    def underline_text(self):
     cursor = self.text.textCursor()
     char_format = QTextCharFormat()
     char_format.setFontUnderline(True)
     cursor.setCharFormat(char_format)



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

    def open_recent_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                contents = file.read()
                self.text.clear()
                self.text.insertPlainText(contents)
            self.setWindowTitle(f"{filename} - Notepad")
        except Exception as e:
            print(f"An error occurred while opening the file:\n{str(e)}")

    def cut(self):
        self.text.cut()

    def copy(self):
        self.text.copy()

    def paste(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasText():
            text_fragment = QTextDocumentFragment.fromHtml(mime_data.text())
            cursor = self.text.textCursor()
            cursor.insertFragment(text_fragment)

    def insert_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp *.gif);;All Files (*)", options=options)

        if file_name:
            try:
                dialog = ImageResizeDialog(self)
                if dialog.exec_() == QDialog.Accepted:
                    width, height = dialog.get_size()
                    image = QImage(file_name)
                    if width > 0 and height > 0:
                        image = image.scaled(width, height, Qt.KeepAspectRatio)
                    cursor = self.text.textCursor()
                    cursor.insertImage(image)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while inserting the image:\n{str(e)}")

    def select_all(self):
        self.text.selectAll()

    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text.setFont(font)

    def closeEvent(self, event):
        self.connection.close()
        event.accept()

    def update_open_recent_menu(self):
        self.open_recent_menu.clear()

        select_query = "SELECT filename FROM file_history ORDER BY timestamp DESC LIMIT 5"
        self.cursor.execute(select_query)
        recent_files = self.cursor.fetchall()

        for recent_file in recent_files:
            filename = recent_file[0]
            action = QAction(filename, self)
            action.triggered.connect(lambda _, filename=filename: self.open_recent_file(filename))
            self.open_recent_menu.addAction(action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = App()
    mainWin.show()

    mainWin.update_open_recent_menu()

    sys.exit(app.exec_())
