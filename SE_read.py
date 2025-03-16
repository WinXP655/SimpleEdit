import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import tkinter.font as tkFont
from tkinter import PhotoImage

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SimpleEdit (Read-only)")
        self.file_path = None
        self.word_wrap = False  # Переменная для отслеживания состояния Word Wrap

        # Переменные для состояния интерфейса
        self.show_toolbar = tk.BooleanVar(value=True)
        self.show_statusbar = tk.BooleanVar(value=True)
        self.word_wrap = tk.BooleanVar(value=False)

        # Устанавливаем шрифт Microsoft Sans Serif
        self.default_font = tkFont.nametofont("TkDefaultFont")
        self.default_font.config(family="Microsoft Sans Serif", size=8)

        # Панель инструментов
        self.toolbar_frame = tk.Frame(self.root)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        self.create_toolbar()  # Создаем панель инструментов

        # Текстовое поле (только для чтения)
        self.text_area_frame = tk.Frame(self.root)
        self.text_area_frame.pack(expand=True, fill='both')
        self.text_area = tk.Text(self.text_area_frame, wrap=tk.NONE, state=tk.DISABLED)
        self.scrollbar = tk.Scrollbar(self.text_area_frame, command=self.text_area.yview)
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.text_area.pack(expand=True, fill='both', side=tk.LEFT)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')

        # Статусная панель
        self.status_bar = tk.Label(self.root, text="New", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=self.default_font, height=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=2)  # Добавляем отступы
        
        # Устанавливаем минимальный размер окна
        self.root.minsize(width=320, height=200)

        # Меню
        self.menu = tk.Menu(self.root, font=self.default_font)
        self.root.config(menu=self.menu)

        # Инициализация состояния элементов
        self.toggle_toolbar()
        self.toggle_statusbar()
        self.toggle_word_wrap()

        """Создает главное меню."""
        self.icons = self.load_icons()  # Загружаем иконки

        # Меню "File"
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.add_menu_command(self.file_menu, "Open...", "open", self.open_file)
        self.file_menu.add_separator()
        self.add_menu_command(self.file_menu, "Exit", "exit", self.exit_app)

        # Меню "Edit"
        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.add_menu_command(self.edit_menu, "Copy", "copy", self.copy)
        self.edit_menu.add_separator()
        self.add_menu_command(self.edit_menu, "Select All", "select_all", self.select_all)

        # Меню "View"
        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_checkbutton(
            label="Show Toolbar",
            image=self.icons["toolbar"],
            compound=tk.LEFT if self.icons["toolbar"] else None,
            variable=self.show_toolbar,
            command=self.toggle_toolbar
        )
        self.view_menu.add_checkbutton(
            label="Show Status Bar",
            image=self.icons["statusbar"],
            compound=tk.LEFT if self.icons["statusbar"] else None,
            variable=self.show_statusbar,
            command=self.toggle_statusbar
        )
        self.view_menu.add_separator()
        self.view_menu.add_checkbutton(
            label="Word Wrap",
            image=self.icons["word_wrap"],
            compound=tk.LEFT if self.icons["word_wrap"] else None,
            variable=self.word_wrap,
            command=self.toggle_word_wrap
        )

        # Меню "Search"
        self.search_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Search", menu=self.search_menu)
        self.add_menu_command(self.search_menu, "Find", "find", self.find)
        self.add_menu_command(self.search_menu, "Find Next", "find_next", self.find_next)

        # Меню "Help"
        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.add_menu_command(self.help_menu, "Help", "help", self.open_help)
        self.add_menu_command(self.help_menu, "About", "about", self.show_about)

        """Создает контекстное меню."""
        self.context_menu = tk.Menu(self.root, tearoff=0)

        # Добавляем команды в контекстное меню
        self.add_menu_command(self.context_menu, "Copy", "copy", self.copy)
        self.context_menu.add_separator()
        self.add_menu_command(self.context_menu, "Select All", "select_all", self.select_all)

        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", image=self.icons["copy"], compound=tk.LEFT, command=self.copy)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", image=self.icons["select_all"], compound=tk.LEFT, command=self.select_all)

        # Привязываем контекстное меню к текстовому полю
        self.text_area.bind("<Button-3>", self.show_context_menu)  # Правая кнопка мыши
        self.bind_shortcuts()

    def load_icons(self):
        """Загружает все иконки из файлов."""
        icons = {
            "new": "icons/new.png",
            "open": "icons/open.png",
            "save": "icons/save.png",
            "save_as": "icons/save_as.png",
            "exit": "icons/exit.png",
            "undo": "icons/undo.png",
            "redo": "icons/redo.png",
            "cut": "icons/cut.png",
            "copy": "icons/copy.png",
            "paste": "icons/paste.png",
            "help": "icons/help.png",
            "delete": "icons/delete.png",
            "find": "icons/find.png",
            "find_next": "icons/find_next.png",
            "replace": "icons/replace.png",
            "about": "icons/about.png",
            "word_wrap": "icons/word_wrap.png",
            "select_all": "icons/select_all.png",
            "date_time": "icons/date_time.png",
            "toolbar": "icons/toolbar.png",
            "statusbar": "icons/statusbar.png",
            "print": "icons/print.png"
        }

        loaded_icons = {}
        for name, path in icons.items():
            loaded_icons[name] = self.load_icon(path)  # Используем метод load_icon
        return loaded_icons

    def add_menu_command(self, menu, label, icon_name, command):
        """
        Добавляет команду в меню с проверкой наличия иконки.
        """
        icon = self.icons.get(icon_name)
        menu.add_command(
            label=label,
            image=icon,
            compound=tk.LEFT if icon else None,  # Добавляем иконку только если она загружена
            command=command
        )

    def load_icon(self, icon_path):
        """Загружает иконку из файла или возвращает None, если файл не найден."""
        try:
            return tk.PhotoImage(file=icon_path)
        except Exception as e:
            print(f"Error loading icon: {icon_path} - {e}")
            return None

    def show_context_menu(self, event):
        """Отображает контекстное меню при правом клике."""
        self.context_menu.post(event.x_root, event.y_root)

    def create_toolbar(self):
        """Создает панель инструментов с кнопками и иконками."""
        self.toolbar_frame.pack_forget()
        self.toolbar_frame = tk.Frame(self.root)

        # Загружаем иконки
        icons = {
            "open": "icons/open.png",
            "copy": "icons/copy.png",
            "about": "icons/about.png",
            "exit": "icons/exit.png",
            "help": "icons/help.png",
            "delete": "icons/delete.png",
            "find": "icons/find.png",
            "find_next": "icons/find_next.png",
            "word_wrap": "icons/word_wrap.png",
            "select_all": "icons/select_all.png",
            "toolbar": "icons/toolbar.png",
            "statusbar": "icons/statusbar.png",
            "print": "icons/print.png"
        }

        loaded_icons = {}
        for name, path in icons.items():
            try:
                loaded_icons[name] = tk.PhotoImage(file=path)
            except Exception as e:
                print(f"Error loading icon: {path} - {e}")
                loaded_icons[name] = None  # Если иконка не загружена, оставляем None

        # Кнопка "Open"
        open_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["open"],
            command=self.open_file
        )
        open_button.grid(row=0, column=1, padx=2, pady=2)
        open_button.image = loaded_icons["open"]

        # Разделитель
        separator1 = tk.Frame(self.toolbar_frame, width=2, bg="gray")
        separator1.grid(row=0, column=4, padx=5, pady=2, sticky="ns")

        # Кнопка "Copy"
        copy_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["copy"],
            command=self.copy
        )
        copy_button.grid(row=0, column=6, padx=2, pady=2)
        copy_button.image = loaded_icons["copy"]

        # Разделитель
        separator2 = tk.Frame(self.toolbar_frame, width=2, bg="gray")
        separator2.grid(row=0, column=8, padx=5, pady=2, sticky="ns")

        # Кнопка "About"
        about_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["about"],
            command=self.show_about
        )
        about_button.grid(row=0, column=9, padx=2, pady=2)
        about_button.image = loaded_icons["about"]

        # Кнопка "Exit"
        exit_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["exit"],
            command=self.exit_app
        )
        exit_button.grid(row=0, column=10, padx=2, pady=2)
        exit_button.image = loaded_icons["exit"]

        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

    def bind_shortcuts(self):
        """Привязывает сочетания клавиш к командам."""
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-f>", lambda event: self.find())
        self.root.bind("<F3>", lambda event: self.find_next())
        self.root.bind("<Control-a>", lambda event: self.select_all())
        self.root.bind("<Control-c>", lambda event: self.copy())
        self.root.bind("<Alt-F4>", lambda event: self.exit_app())

    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # Временно разблокируем поле для изменения содержимого
                    self.text_area.config(state=tk.NORMAL)
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
                    self.text_area.config(state=tk.DISABLED)  # Блокируем снова
                    self.update_status_bar()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")

    def update_status_bar(self):
        status_text = "New"
        if self.file_path:
            file_size = os.path.getsize(self.file_path)
            status_text = f"{self.file_path} ({file_size} bytes)"
        self.status_bar.config(text=status_text)

    def exit_app(self):
        self.root.quit()

    def copy(self):
        self.text_area.event_generate("<<Copy>>")

    def find(self):
        search_term = simpledialog.askstring("Find", "Enter text to find:")
        if search_term:
            self.last_search_term = search_term  # Сохраняем поисковый запрос
            index = self.text_area.search(search_term, "1.0", tk.END)
            if index:
                self.text_area.tag_add("found", index, f"{index}+{len(search_term)}c")
                self.text_area.tag_config("found", background="yellow")

    def find_next(self):
        """Ищет следующее вхождение текста."""
        if not self.last_search_term:  # Если нет сохраненного запроса
            search_term = simpledialog.askstring("Find Next", "Enter text to find next:")
            if not search_term:
                return
            self.last_search_term = search_term

        # Используем сохраненный запрос
        search_term = self.last_search_term
        current_pos = self.text_area.index(tk.INSERT)

        # Поиск с текущей позиции
        index = self.text_area.search(search_term, current_pos, tk.END)

        if index:
            end_index = f"{index}+{len(search_term)}c"
            self.text_area.tag_remove("found", "1.0", tk.END)
            self.text_area.tag_add("found", index, end_index)
            self.text_area.tag_config("found", background="yellow")
            self.text_area.mark_set(tk.INSERT, end_index)
            self.text_area.see(index)
        else:
            if messagebox.askyesno("Search", "Reached end. Continue from beginning?"):
                self.text_area.mark_set(tk.INSERT, "1.0")
                self.find_next()

            # Получаем текущую позицию курсора
            current_pos = self.text_area.index(tk.INSERT)
            # Ищем следующее вхождение текста после текущей позиции
            index = self.text_area.search(search_term, current_pos, tk.END)

            if index:
                # Если найдено, выделяем текст
                end_index = f"{index}+{len(search_term)}c"
                self.text_area.tag_add("found", index, end_index)
                self.text_area.tag_config("found", background="yellow")
                # Перемещаем курсор к найденному тексту
                self.text_area.mark_set(tk.INSERT, end_index)
                self.text_area.see(index)  # Прокручиваем текстовое поле, чтобы показать найденное
            else:
                # Если ничего не найдено, начинаем поиск сначала
                restart_search = messagebox.askyesno("Search", "Reached the end of the document. Continue from the beginning?")
                if restart_search:
                    self.text_area.mark_set(tk.INSERT, "1.0")  # Возвращаем курсор в начало
                    self.find_next()  # Рекурсивно вызываем поиск снова

        # Получаем текущую позицию курсора
        current_pos = self.text_area.index(tk.INSERT)
        # Ищем следующее вхождение текста после текущей позиции
        index = self.text_area.search(search_term, current_pos, tk.END)

        if index:
            # Если найдено, выделяем текст
            end_index = f"{index}+{len(search_term)}c"
            self.text_area.tag_add("found", index, end_index)
            self.text_area.tag_config("found", background="yellow")
            # Перемещаем курсор к найденному тексту
            self.text_area.mark_set(tk.INSERT, end_index)
            self.text_area.see(index)  # Прокручиваем текстовое поле, чтобы показать найденное
        else:
            # Если ничего не найдено, начинаем поиск сначала
            restart_search = messagebox.askyesno("Search", "Reached the end of the document. Continue from the beginning?")
            if restart_search:
                self.text_area.mark_set(tk.INSERT, "1.0")  # Возвращаем курсор в начало
                self.find_next()  # Рекурсивно вызываем поиск снова

    def select_all(self):
        self.text_area.tag_add("sel", "1.0", "end")

    def toggle_word_wrap(self):
        """Переключает состояние Word Wrap."""
        wrap_mode = tk.WORD if self.word_wrap.get() else tk.NONE
        self.text_area.config(wrap=wrap_mode)

    def toggle_toolbar(self):
        """Переключает видимость панели инструментов."""
        if self.show_toolbar.get():
            # Показываем панель инструментов
            self.toolbar_frame.pack(side=tk.TOP, fill=tk.X, before=self.text_area_frame)
        else:
            # Скрываем панель инструментов
            self.toolbar_frame.pack_forget()

    def toggle_statusbar(self):
        """Переключает видимость строки состояния."""
        if self.show_statusbar.get():
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.status_bar.pack_forget()

    def open_help(self):
        """Открывает файл справки (help.rtf)."""
        help_file_path = "help.rtf"  # Убедитесь, что файл находится в той же директории, что и скрипт
        if os.path.exists(help_file_path):
            try:
                # Открываем файл с помощью стандартной программы
                os.startfile(help_file_path)  # Для Windows
            except Exception as e:
                messagebox.showerror("Error", f"Could not open help file:\n{e}")
        else:
            messagebox.showerror("Error", "Help file not found. Please make sure 'help.rtf' exists.")

    def show_about(self):
        # Создаем новое окно
        about_window = tk.Toplevel(self.root)
        about_window.title("SimpleEdit (Read-only)")
    
        # Устанавливаем размеры окна
        about_window.geometry("350x250")
    
        # Запрещаем изменять размер окна
        about_window.resizable(False, False)

        # Загружаем изображение
        try:
            about_icon = PhotoImage(file="icons/se.png")
        except Exception as e:
            print(f"Error loading image: {e}")
            about_icon = None  # Если изображение не загружено, можно оставить None

        # Если изображение удалось загрузить, добавляем его в окно
        if about_icon:
            image_label = tk.Label(about_window, image=about_icon)
            image_label.image = about_icon  # Сохраняем ссылку на изображение
            image_label.pack(pady=10)  # Располагаем картинку в окне

        # Заголовок с текстом
        title_label = tk.Label(about_window, text="SimpleEdit", font=("Microsoft Sans Serif", 16, "bold"))
        title_label.pack(pady=5)

        # Текстовое описание
        description_label = tk.Label(about_window, text="(c) Параметры 2025\n\nA simple text editor made with Python. Inspired by a Windows Notepad from Windows 95. Read-only version.", wraplength=250, justify="center")
        description_label.pack(pady=10)

        # Кнопка для закрытия окна
        close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=10)

        # Центрируем окно на экране
        window_width = 350
        window_height = 250  # Увеличим высоту окна, чтобы поместилось изображение
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        about_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadApp(root)
    root.mainloop()