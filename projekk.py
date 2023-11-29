import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Untitled - Notepad")
        self.wm_attributes('-alpha', 0.9)
        self.geometry("600x600")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")  # Use 'clam' theme for ttk widgets

        self.text = tk.Text(self, wrap="word", font=("Consolas", 12))
        self.text.pack(side="top", fill="both", expand=True)

        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)

        # Bind Ctrl+N, Ctrl+O, Ctrl+S to corresponding methods
        self.text.bind("<Control-n>", lambda event: self.new_file())
        self.text.bind("<Control-o>", lambda event: self.open_file())
        self.text.bind("<Control-s>", lambda event: self.save_file())
        # Bind Ctrl+A to the select_all method
        self.text.bind("<Control-a>", self.select_all)

    def new_file(self):
        self.text.delete(1.0, tk.END)
        self.title("Untitled - Notepad")

    def open_file(self):
        filename = filedialog.askopenfilename(parent=self, mode="r", title="Select a File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            with open(filename, 'r') as file:
                contents = file.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(1.0, contents)
            self.title(f"{filename} - Notepad")

    def save_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if filename:
            with open(filename, 'w') as file:
                contents = self.text.get(1.0, tk.END)
                file.write(contents)
            self.title(f"{filename} - Notepad")

    def cut(self):
        self.text.event_generate("<<Cut>>")

    def copy(self):
        self.text.event_generate("<<Copy>>")

    def paste(self):
        self.text.event_generate("<<Paste>>")

    def select_all(self, event=None):
        self.text.tag_add(tk.SEL, "1.0", tk.END)
        self.text.mark_set(tk.SEL_FIRST, "1.0")
        self.text.mark_set(tk.SEL_LAST, tk.END)
        return "break"  # To prevent default behavior

if __name__ == "__main__":
    app = App()
    app.mainloop()
