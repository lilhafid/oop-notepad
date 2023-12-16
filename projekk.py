import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QAction, QMenu, QFontDialog, QShortcut, QMessageBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
from PyQt5.QtGui import QKeySequence, QFont, QImage, QTextDocumentFragment, QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import Qt

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
        self.context_menu = QMenu(self)  

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

        edit_menu = menubar.addMenu("Alignment")


        align_left_action = QAction("Align Left", self)
        align_left_action.triggered.connect(lambda: self.set_alignment(Qt.AlignLeft))
        edit_menu.addAction(align_left_action)

        align_center_action = QAction("Align Center", self)
        align_center_action.triggered.connect(lambda: self.set_alignment(Qt.AlignHCenter))
        edit_menu.addAction(align_center_action)

        align_right_action = QAction("Align Right", self)
        align_right_action.triggered.connect(lambda: self.set_alignment(Qt.AlignRight))
        edit_menu.addAction(align_right_action)

        align_justify_action = QAction("Justify", self)
        align_justify_action.triggered.connect(lambda: self.set_alignment(Qt.AlignJustify))
        edit_menu.addAction(align_justify_action)

        increase_indent_action = QAction("Increase Indent", self)
        increase_indent_action.triggered.connect(self.increase_indent)
        edit_menu.addAction(increase_indent_action)

        decrease_indent_action = QAction("Decrease Indent", self)
        decrease_indent_action.triggered.connect(self.decrease_indent)
        edit_menu.addAction(decrease_indent_action)

        file_menu.addSeparator()

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

        # Add a context menu for changing font of selected word
        self.add_font_actions_to_menu()

        # Add a status bar at the bottom
        self.statusBar = self.statusBar()

        self.setStatusBar(self.statusBar)

        self.text.textChanged.connect(self.update_status_bar)

        self.update_status_bar()


    def set_alignment(self, alignment):
        cursor = self.text.textCursor()
        block_format = cursor.blockFormat()
        block_format.setAlignment(alignment)
        cursor.setBlockFormat(block_format)

    def increase_indent(self):
        cursor = self.text.textCursor()
        cursor.insertText("\t")

    def decrease_indent(self):
        cursor = self.text.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 1)
        selected_text = cursor.selectedText()
        if selected_text == "\t":
            cursor.removeSelectedText()



    def add_font_actions_to_menu(self):
        font_list = ["Arial", "Times New Roman", "Courier New", "Verdana", "Serif", "Sans Serif", "Monospace", "Cursive", "Fantasy"]
        for font_name in font_list:
            action = QAction(font_name, self)
            action.triggered.connect(lambda _, font_name=font_name: self.change_font_for_selected_word(font_name))
            self.context_menu.addAction(action)

    def change_font_for_selected_word(self, font_name):
        cursor = self.text.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            char_format = QTextCharFormat()
            char_format.setFont(QFont(font_name, 12))  
            cursor.mergeCharFormat(char_format)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.show_context_menu(event)

    def show_context_menu(self, event):
        self.context_menu.exec_(self.mapToGlobal(event.pos()))

    def highlight_text(self):
        cursor = self.text.textCursor()
        cursor.mergeCharFormat(QTextCharFormat().setBackground(QColor(Qt.yellow)))

    def underline_text(self):
        cursor = self.text.textCursor()
        cursor.mergeCharFormat(QTextCharFormat().setFontUnderline(True))

    def update_status_bar(self):
        # Get the text from the QTextEdit
        text = self.text.toPlainText()

        # Count words and spaces
        word_count = len(text.split())
        space_count = text.count(' ')

        # Set the status bar text
        status_text = f"Words: {word_count}, Spaces: {space_count}"
        self.statusBar.showMessage(status_text)

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

    mainWin.update_open_recent_menu() 
    mainWin.show()
    sys.exit(app.exec_())

