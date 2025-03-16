import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from datetime import datetime
import os
import tkinter.font as tkFont
from tkinter import PhotoImage
import locale
import configparser
import winsound

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SimpleEdit")
        self.file_path = None
        self.is_unsaved = False
        self.word_wrap = False  # Переменная для отслеживания состояния Word Wrap
        self.is_unsaved = False  # Состояние: файл изменён
        self.is_modified = False  # Новый флаг для отслеживания изменений

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

        # Создаем текстовое поле с полосой прокрутки
        self.text_area_frame = tk.Frame(self.root)
        self.text_area_frame.pack(expand=True, fill='both')

        self.text_area = tk.Text(self.text_area_frame, wrap=tk.NONE, undo=True)  # Шрифт для текстового поля
        self.scrollbar = tk.Scrollbar(self.text_area_frame, command=self.text_area.yview)  # Вертикальная полоса прокрутки
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        self.text_area.pack(expand=True, fill='both', side=tk.LEFT)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')

        # Привязка событий
        self.root.bind("<Control-Key-F1>", lambda event: self.easter_egg.check_flower_activation())
        self.root.bind("<Control-Key-F2>", lambda event: self.easter_egg.show_flower_window())

        # Привязываем события клавиш
        self.root.bind("<KeyPress-Control_L>", lambda event: setattr(self, "is_ctrl_pressed", True))
        self.root.bind("<KeyRelease-Control_L>", lambda event: setattr(self, "is_ctrl_pressed", False))

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
        self.add_menu_command(self.file_menu, "New", "new", self.new_file)
        self.add_menu_command(self.file_menu, "Open...", "open", self.open_file)
        self.add_menu_command(self.file_menu, "Save", "save", self.save_file)
        self.add_menu_command(self.file_menu, "Save As...", "save_as", self.save_as)
        self.file_menu.add_separator()
        self.add_menu_command(self.file_menu, "Exit", "exit", self.exit_app)

        # Меню "Edit"
        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.add_menu_command(self.edit_menu, "Undo", "undo", self.undo)
        self.add_menu_command(self.edit_menu, "Redo", "redo", self.redo)
        self.edit_menu.add_separator()
        self.add_menu_command(self.edit_menu, "Cut", "cut", self.cut)
        self.add_menu_command(self.edit_menu, "Copy", "copy", self.copy)
        self.add_menu_command(self.edit_menu, "Paste", "paste", self.paste)
        self.add_menu_command(self.edit_menu, "Delete", "delete", self.delete)
        self.edit_menu.add_separator()
        self.add_menu_command(self.edit_menu, "Select All", "select_all", self.select_all)
        self.add_menu_command(self.edit_menu, "Insert Time and Date", "date_time", self.insert_time_date)

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
        self.search_menu.add_separator()
        self.add_menu_command(self.search_menu, "Replace", "replace", self.replace)

        # Меню "Help"
        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.add_menu_command(self.help_menu, "Help", "help", self.open_help)
        self.add_menu_command(self.help_menu, "About", "about", self.show_about_wrapper)

        # Привязываем сочетание клавиш Ctrl + H
        self.root.bind("<Control-Alt-h>", self.show_alternative_about)

        """Создает контекстное меню."""
        self.context_menu = tk.Menu(self.root, tearoff=0)

        # Добавляем команды в контекстное меню
        self.add_menu_command(self.context_menu, "Undo", "undo", self.undo)
        self.context_menu.add_separator()
        self.add_menu_command(self.context_menu, "Cut", "cut", self.cut)
        self.add_menu_command(self.context_menu, "Copy", "copy", self.copy)
        self.add_menu_command(self.context_menu, "Paste", "paste", self.paste)
        self.add_menu_command(self.context_menu, "Delete", "delete", self.delete)
        self.context_menu.add_separator()
        self.add_menu_command(self.context_menu, "Select All", "select_all", self.select_all)

        # Привязываем контекстное меню к текстовому полю
        self.text_area.bind("<Button-3>", self.show_context_menu)  # Правая кнопка мыши
        self.bind_shortcuts()
        # Отслеживание изменений
        self.text_area.bind("<Key>", self.mark_as_modified)

    def load_localization(self):
        """Загружает локализацию на основе выбранного языка."""
        system_lang = locale.getdefaultlocale()[0]  # Определяем системный язык (например, 'ru_RU')
        lang_code = self.get_lang_code_from_settings()  # Загружаем язык из настроек (если есть)
        lang_code = lang_code or system_lang  # Используем системный язык по умолчанию

        # Если язык не указан, используем английский
        if not lang_code:
            return self.get_default_localization()

        # Пытаемся загрузить пользовательский файл локализации
        if lang_code == "custom":
            return self.load_custom_localization()

        # Загружаем локализацию из файла
        locale_file = f"locales/{lang_code}.nls"
        if os.path.exists(locale_file):
            return self.parse_localization_file(locale_file)
        else:
            # Если файл не найден, используем встроенный английский
            return self.get_default_localization()

    def get_default_localization(self):
        """Возвращает встроенные английские строки."""
        return {
            "File": "File",
            "New": "New",
            "Open": "Open...",
            "Save": "Save",
            "Exit": "Exit",
            "Edit": "Edit",
            "Undo": "Undo",
            "Redo": "Redo",
            "Cut": "Cut",
            "Copy": "Copy",
            "Paste": "Paste",
            "Help": "Help",
            "About": "About",
            "ErrorLoadingFile": "Error loading file",
            "NotFoundError": "Text not found",
            "ErrorLoadingIcon": "Error loading Icon",
            "Unsaved:": "Unsaved changes",
            "UnsavedConfirm": "You have unsaved changes. Do you want to save them?"
        }

    def parse_localization_file(self, file_path):
        """Читает файл локализации и возвращает словарь строк."""
        config = configparser.ConfigParser()
        config.read(file_path, encoding="utf-8")
        return dict(config.items("Strings"))

    def load_custom_localization(self):
        """Загружает пользовательский файл локализации через диалог."""
        file_path = filedialog.askopenfilename(
            defaultextension=".nls",
            filetypes=[("Localization Files", "*.nls")]
        )
        if file_path:
            return self.parse_localization_file(file_path)
        else:
            return self.get_default_localization()

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
            "new": "icons/new.png",
            "open": "icons/open.png",
            "save": "icons/save.png",
            "save_as": "icons/save_as.png",
            "cut": "icons/cut.png",
            "copy": "icons/copy.png",
            "paste": "icons/paste.png",
            "about": "icons/about.png",
            "exit": "icons/exit.png",
            "undo": "icons/undo.png",
            "redo": "icons/redo.png",
            "help": "icons/help.png",
            "delete": "icons/delete.png",
            "find": "icons/find.png",
            "find_next": "icons/find_next.png",
            "replace": "icons/replace.png",
            "word_wrap": "icons/word_wrap.png",
            "select_all": "icons/select_all.png",
            "date_time": "icons/date_time.png",
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

        # Кнопка "New"
        new_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["new"],
            command=self.new_file
        )
        new_button.grid(row=0, column=0, padx=2, pady=2)
        new_button.image = loaded_icons["new"]

        # Кнопка "Open"
        open_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["open"],
            command=self.open_file
        )
        open_button.grid(row=0, column=1, padx=2, pady=2)
        open_button.image = loaded_icons["open"]

        # Кнопка "Save"
        save_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["save"],
            command=self.save_file
        )
        save_button.grid(row=0, column=2, padx=2, pady=2)
        save_button.image = loaded_icons["save"]

        # Кнопка "Save As"
        save_as_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["save_as"],
            command=self.save_as
        )
        save_as_button.grid(row=0, column=3, padx=2, pady=2)
        save_as_button.image = loaded_icons["save_as"]

        # Разделитель
        separator1 = tk.Frame(self.toolbar_frame, width=2, bg="gray")
        separator1.grid(row=0, column=4, padx=5, pady=2, sticky="ns")

        # Кнопка "Cut"
        cut_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["cut"],
            command=self.cut
        )
        cut_button.grid(row=0, column=5, padx=2, pady=2)
        cut_button.image = loaded_icons["cut"]

        # Кнопка "Copy"
        copy_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["copy"],
            command=self.copy
        )
        copy_button.grid(row=0, column=6, padx=2, pady=2)
        copy_button.image = loaded_icons["copy"]

        # Кнопка "Paste"
        paste_button = tk.Button(
            self.toolbar_frame,
            image=loaded_icons["paste"],
            command=self.paste
        )
        paste_button.grid(row=0, column=7, padx=2, pady=2)
        paste_button.image = loaded_icons["paste"]

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
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-S>", lambda event: self.save_as())  # Ctrl+Shift+S
        self.root.bind("<Control-f>", lambda event: self.find())
        self.root.bind("<F3>", lambda event: self.find_next())
        self.root.bind("<Control-a>", lambda event: self.select_all())
        self.root.bind("<Control-c>", lambda event: self.copy())
        self.root.bind("<Control-x>", lambda event: self.cut())
        self.root.bind("<Control-v>", lambda event: self.paste())
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Alt-F4>", lambda event: self.exit_app())

    def check_unsaved_changes(self):
        if self.is_modified:
            response = messagebox.askyesnocancel(
                "Unsaved changes",
                "You have unsaved changes. Do you want to save them?",
                icon=messagebox.WARNING
            )
            if response is None:  # Cancel
                return False
            elif response:  # Yes
                if not self.save_file():  # Если сохранение не удалось
                    return False
        return True

    def new_file(self):
        if not self.check_unsaved_changes():
            return
        self.text_area.delete(1.0, tk.END)
        self.file_path = None
        self.is_modified = False
        self.update_status_bar()

    def open_file(self):
        if not self.check_unsaved_changes():
            return
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.file_path = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.config(state=tk.NORMAL)  # Разблокируем поле
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
                self.is_modified = False
                self.update_status_bar()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")

    def mark_as_modified(self, event=None):
        """Отмечает файл как изменённый."""
        self.is_modified = True
        self.update_status_bar()

    def update_status_bar(self):
        if self.file_path:
            file_size = os.path.getsize(self.file_path)
            status_text = f"{self.file_path}{'*' if self.is_modified else ''} ({file_size} bytes)"
        else:
            status_text = "Новый" + ('*' if self.is_modified else '')
        self.status_bar.config(text=status_text)

    def save_file(self):
        if self.file_path:
            try:
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.is_modified = False
                self.update_status_bar()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")
            return False
        else:
            return self.save_as()
        return True

    def save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.file_path = file_path
                self.is_modified = False
                self.update_status_bar()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

    def exit_app(self):
        if not self.check_unsaved_changes():
            return
        self.root.quit()

    def undo(self):
        self.text_area.event_generate("<<Undo>>")

    def redo(self):
        self.text_area.event_generate("<<Redo>>")

    def cut(self):
        self.text_area.event_generate("<<Cut>>")

    def copy(self):
        self.text_area.event_generate("<<Copy>>")

    def paste(self):
        self.text_area.event_generate("<<Paste>>")

    def delete(self):
        self.text_area.delete("sel.first", "sel.last")

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

    def replace(self):
        """Окно для ввода текста для замены"""
        def do_replace():
            find_text = find_entry.get()
            replace_text = replace_entry.get()

            # Позиция для начала поиска
            pos = "1.0"
            
            while True:
                # Ищем следующее вхождение
                pos = self.text_area.search(find_text, pos, stopindex=tk.END)
                if not pos:
                    break
                # Заменяем текст на новый
                end_pos = f"{pos}+{len(find_text)}c"
                self.text_area.delete(pos, end_pos)
                self.text_area.insert(pos, replace_text)
                pos = end_pos  # обновляем позицию поиска

        # Создаем новое окно для ввода текста
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Replace Text")
        
        # Заголовки и поля ввода
        find_label = tk.Label(replace_window, text="Find:")
        find_label.grid(row=0, column=0, padx=5, pady=5)

        find_entry = tk.Entry(replace_window)
        find_entry.grid(row=0, column=1, padx=5, pady=5)

        replace_label = tk.Label(replace_window, text="Replace with:")
        replace_label.grid(row=1, column=0, padx=5, pady=5)

        replace_entry = tk.Entry(replace_window)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)

        # Кнопка для выполнения замены
        replace_button = tk.Button(replace_window, text="Replace", command=do_replace)
        replace_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Кнопка для закрытия окна
        close_button = tk.Button(replace_window, text="Close", command=replace_window.destroy)
        close_button.grid(row=3, column=0, columnspan=2, pady=5)


    def select_all(self):
        self.text_area.tag_add("sel", "1.0", "end")

    def insert_time_date(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.text_area.insert(tk.INSERT, current_time)

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
            messagebox.showerror(self.loc("Error"), self.loc("HelpFileNotFound"))

    def show_about_wrapper(self, event=None):
        """Обертка для вызова правильного метода 'About'."""
        if event and event.state & 0x4:  # Проверка зажатия Ctrl
            self.show_alternative_about()
        else:
            self.show_standard_about()

    def show_alternative_about(self, event=None):
        """Альтернативное окно 'О программе'."""
        about_window = tk.Toplevel(self.root)
        about_window.title("Alternative About")
        about_window.geometry("400x300")
        about_window.resizable(False, False)

        try:
            about_icon = PhotoImage(file="icons/flower.png")  # Альтернативная иконка
        except Exception as e:
            print(f"Error loading image: {e}")
            about_icon = None

        if about_icon:
            image_label = tk.Label(about_window, image=about_icon)
            image_label.image = about_icon
            image_label.pack(pady=10)

        title_label = tk.Label(
            about_window,
            text="SimpleEdit (Secret Mode)",
            font=("Microsoft Sans Serif", 16, "bold")
        )
        title_label.pack(pady=5)

        description_label = tk.Label(
            about_window,
            text=(
                "(c) Параметры 2025\n\n"
                "This is a secret version of the About window.\n"
                "You found it by pressing Ctrl+Alt+H! This is just a simple easter egg.\n\n"
                "Check out the project here: https://github.com/WinXP655/SimpleEdit"
            ),
            wraplength=350,
            justify="center"
        )
        description_label.pack(pady=10)

        close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=10)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
    
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
        description_label = tk.Label(about_window, text="(c) Параметры 2025\n\nA simple text editor made with Python. Inspired by a Windows Notepad from Windows 95", wraplength=250, justify="center")
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