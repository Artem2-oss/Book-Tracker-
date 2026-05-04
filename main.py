import json
import os
from tkinter import *
from tkinter import messagebox, ttk

# Имя файла для хранения данных
DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x500")

        self.books = []          # список книг (словарей)
        self.filters = {"genre": "", "pages_min": 0}  # текущие фильтры

        # --- Поля ввода ---
        frame_input = LabelFrame(root, text="Добавить книгу", padx=10, pady=10)
        frame_input.pack(fill="x", padx=10, pady=5)

        Label(frame_input, text="Название:").grid(row=0, column=0, sticky="e")
        self.entry_title = Entry(frame_input, width=30)
        self.entry_title.grid(row=0, column=1, padx=5, pady=2)

        Label(frame_input, text="Автор:").grid(row=0, column=2, sticky="e")
        self.entry_author = Entry(frame_input, width=30)
        self.entry_author.grid(row=0, column=3, padx=5, pady=2)

        Label(frame_input, text="Жанр:").grid(row=1, column=0, sticky="e")
        self.entry_genre = Entry(frame_input, width=30)
        self.entry_genre.grid(row=1, column=1, padx=5, pady=2)

        Label(frame_input, text="Страниц:").grid(row=1, column=2, sticky="e")
        self.entry_pages = Entry(frame_input, width=30)
        self.entry_pages.grid(row=1, column=3, padx=5, pady=2)

        btn_add = Button(frame_input, text="➕ Добавить книгу", command=self.add_book, bg="#4CAF50", fg="white")
        btn_add.grid(row=2, column=0, columnspan=4, pady=10)

        # --- Панель фильтров ---
        frame_filter = LabelFrame(root, text="Фильтры", padx=10, pady=10)
        frame_filter.pack(fill="x", padx=10, pady=5)

        Label(frame_filter, text="Фильтр по жанру:").grid(row=0, column=0, sticky="e")
        self.filter_genre = Entry(frame_filter, width=20)
        self.filter_genre.grid(row=0, column=1, padx=5)

        Label(frame_filter, text="Страниц больше:").grid(row=0, column=2, sticky="e")
        self.filter_pages = Entry(frame_filter, width=10)
        self.filter_pages.grid(row=0, column=3, padx=5)

        btn_filter = Button(frame_filter, text="🔍 Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=4, padx=10)

        btn_reset = Button(frame_filter, text="❌ Сбросить", command=self.reset_filter)
        btn_reset.grid(row=0, column=5)

        # --- Таблица для отображения книг ---
        self.tree = ttk.Treeview(root, columns=("title", "author", "genre", "pages"), show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=100)
        self.tree.column("pages", width=80)

        scrollbar = Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=RIGHT, fill=Y, pady=5)

        # --- Кнопки управления ---
        frame_buttons = Frame(root)
        frame_buttons.pack(fill="x", padx=10, pady=5)

        btn_save = Button(frame_buttons, text="💾 Сохранить в JSON", command=self.save_to_json)
        btn_save.pack(side=LEFT, padx=5)

        btn_load = Button(frame_buttons, text="📂 Загрузить из JSON", command=self.load_from_json)
        btn_load.pack(side=LEFT, padx=5)

        # Загружаем данные при старте
        self.load_from_json()
        self.refresh_table()

    # ------------------ Валидация ------------------
    def validate_inputs(self, title, author, genre, pages_str):
        if not title or not author or not genre:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return False
        if not pages_str.isdigit():
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
            return False
        return True

    # ------------------ Добавление книги ------------------
    def add_book(self):
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        genre = self.entry_genre.get().strip()
        pages_str = self.entry_pages.get().strip()

        if not self.validate_inputs(title, author, genre, pages_str):
            return

        pages = int(pages_str)
        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)
        self.refresh_table()

        # Очистка полей
        self.entry_title.delete(0, END)
        self.entry_author.delete(0, END)
        self.entry_genre.delete(0, END)
        self.entry_pages.delete(0, END)

        messagebox.showinfo("Успех", "Книга добавлена!")

    # ------------------ Фильтрация ------------------
    def apply_filter(self):
        genre_filter = self.filter_genre.get().strip()
        pages_filter = self.filter_pages.get().strip()

        self.filters["genre"] = genre_filter
        self.filters["pages_min"] = int(pages_filter) if pages_filter.isdigit() else 0

        self.refresh_table()

    def reset_filter(self):
        self.filter_genre.delete(0, END)
        self.filter_pages.delete(0, END)
        self.filters = {"genre": "", "pages_min": 0}
        self.refresh_table()

    def get_filtered_books(self):
        filtered = self.books[:]
        if self.filters["genre"]:
            filtered = [b for b in filtered if self.filters["genre"].lower() in b["genre"].lower()]
        if self.filters["pages_min"] > 0:
            filtered = [b for b in filtered if b["pages"] > self.filters["pages_min"]]
        return filtered

    def refresh_table(self):
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered_books = self.get_filtered_books()
        for book in filtered_books:
            self.tree.insert("", END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    # ------------------ Работа с JSON ------------------
    def save_to_json(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранено", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_json(self):
        if not os.path.exists(DATA_FILE):
            self.books = []
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
            self.books = []


# ------------------ Запуск приложения ------------------
if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()