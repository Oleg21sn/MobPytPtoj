import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from db import get_lessons, load_words, save_word, create_lesson, rename_lesson, toggle_word_learned
from datetime import datetime
import random

class WordTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Вивчення англійських слів")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f8ff")
        self.words = {}
        self.current_lesson = None
        self.training_data = []
        self.training_index = 0
        self.training_mode = "EN-UA"
        self.mistake_count = 0
        self.current_word = None
        self.correct_answer = ""
        self.score = 0
        self.attempts_count = 0  
        self.create_main_menu()

        # Гарячі клавіші
        self.root.bind("<Control-Key-1>", lambda event: self.add_word_ui())
        self.root.bind("<Control-Key-2>", lambda event: self.show_dictionary())
        self.root.bind("<Control-Key-3>", lambda event: self.select_mode())
        self.root.bind("<Control-Key-4>", lambda event: self.show_learned_words())
        self.root.bind("<Escape>", lambda event: self.create_main_menu())

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_window()
        self.root.unbind("<Return>")

        # Головний контейнер
        main_container = tk.Frame(self.root, bg="#f0f8ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Заголовок
        tk.Label(main_container, text="📚 Word Trainer", 
                font=("Arial", 24, "bold"), bg="#f0f8ff", fg="#2c3e50").pack(pady=20)

        # Кнопки меню
        buttons = [
            ("➕ Додати слово", "#3498db", self.add_word_ui),
            ("📖 Словник", "#2ecc71", self.show_dictionary),
            ("🏋️ Тренування", "#e67e22", self.select_mode),
            ("📝 Вивчені слова", "#f1c40f", self.show_learned_words),
            ("🚪 Вихід", "#e74c3c", self.root.quit)
        ]

        for text, color, command in buttons:
            btn = tk.Button(main_container, text=text,
                          font=("Arial", 14),
                          bg=color,
                          fg="white",
                          relief=tk.FLAT,
                          width=20,
                          command=command)
            btn.pack(pady=10)

            # Ховер-ефект
            def on_enter(e, btn=btn, color=color):
                btn['bg'] = self.darken_color(color)
            def on_leave(e, btn=btn, color=color):
                btn['bg'] = color

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def darken_color(self, hex_color):
        """Затемнює колір для ховер-ефекту."""
        # Конвертуємо HEX в RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Затемнюємо
        factor = 0.8
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # Конвертуємо назад в HEX
        return f"#{r:02x}{g:02x}{b:02x}"

    def select_mode(self):
        """Вибір режиму тренування."""
        self.clear_window()
        
        # Головний контейнер
        main_container = tk.Frame(self.root, bg="#f0f8ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Заголовок
        tk.Label(main_container, text="🏋️ Тренування", 
                font=("Arial", 24, "bold"), bg="#f0f8ff", fg="#2c3e50").pack(pady=20)
                
        # Вибір уроку
        tk.Label(main_container, text="Оберіть урок:", 
                font=("Arial", 14), bg="#f0f8ff", fg="#34495e").pack(pady=(0, 5))
        
        # Отримуємо список уроків
        lessons = [lesson["name"] for lesson in get_lessons()]
        
        # Якщо список уроків порожній, створюємо урок "Головний"
        if not lessons:
            print("UI: Список уроків порожній у select_mode. Створюємо урок 'Головний'")
            result = create_lesson("Головний")
            print(f"UI: Результат створення уроку 'Головний': {result}")
            
            if result:
                lessons = [lesson["name"] for lesson in get_lessons()]
            else:
                messagebox.showerror("Помилка", "❌ Не вдалося створити урок! Можливо, є проблема з базою даних.")
                self.create_main_menu()
                return
                
            if not lessons:  # Якщо все ще немає уроків, використовуємо замінник
                lessons = ["Головний"]
            
        self.lesson_var = tk.StringVar(value=lessons[0])
        
        lesson_dropdown = ttk.Combobox(main_container, textvariable=self.lesson_var, 
                                     values=lessons, state="readonly", 
                                     width=30, font=("Arial", 12))
        lesson_dropdown.pack(pady=(0, 20))
        
        # Вибір режиму
        tk.Label(main_container, text="Оберіть режим:", 
                font=("Arial", 14), bg="#f0f8ff", fg="#34495e").pack(pady=(0, 10))
        
        # Кнопки режимів
        modes = [
            ("🇬🇧 Англійська ➡️ 🇺🇦 Українська", "#3498db", "EN-UA"),
            ("🇺🇦 Українська ➡️ 🇬🇧 Англійська", "#2ecc71", "UA-EN")
        ]

        for text, color, mode in modes:
            btn = tk.Button(main_container, text=text,
                          font=("Arial", 12),
                          bg=color,
                          fg="white",
                          relief=tk.FLAT,
                          width=30,
                          command=lambda m=mode: self.start_training(m))
            btn.pack(pady=5)

            # Ховер-ефект
            def on_enter(e, btn=btn, color=color):
                btn['bg'] = self.darken_color(color)
            def on_leave(e, btn=btn, color=color):
                btn['bg'] = color

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Кнопка "Назад"
        back_btn = tk.Button(main_container, text="🔙 Назад",
                           font=("Arial", 12),
                           bg="#e74c3c",
                           fg="white",
                           relief=tk.FLAT,
                           width=15,
                           command=self.create_main_menu)
        back_btn.pack(pady=20)
        
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg=self.darken_color("#e74c3c")))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#e74c3c"))

    def start_training(self, mode):
        """Початок тренування."""
        self.training_mode = mode
        self.training_data = []
        self.training_index = 0
        self.mistake_count = 0
        self.score = 0
        
        # Завантажуємо слова для тренування
        selected_lesson = self.lesson_var.get()
        words = load_words(selected_lesson)
        
        if not words:
            messagebox.showwarning("Увага", f"Немає слів для тренування в уроці '{selected_lesson}'!")
            self.create_main_menu()
            return
            
        # Створюємо список слів для тренування
        for en_word, details in words.items():
            if not details.get("learned", False):  # Тренуємо тільки невивчені слова
                self.training_data.append({
                    "english": en_word,
                    "ukrainian": details["translation"],
                    "lesson": details["lesson"]
                })
                
        if not self.training_data:
            messagebox.showinfo("Вітаємо!", f"Ви вивчили всі слова в уроці '{selected_lesson}'!")
            self.create_main_menu()
            return
            
        # Перемішуємо слова у випадковому порядку
        random.shuffle(self.training_data)
            
        self.training_ui()

    def training_ui(self):
        """Інтерфейс тренування."""
        self.clear_window()
        
        if self.training_index >= len(self.training_data):
            # Тренування завершено
            accuracy = ((len(self.training_data) - self.mistake_count) / len(self.training_data)) * 100
            
            # Створюємо вікно результатів
            result_window = tk.Toplevel(self.root)
            result_window.title("Результати тренування")
            result_window.geometry("400x350")
            result_window.configure(bg="#f0f8ff")
            
            # Центруємо вікно відносно головного вікна
            def center_window(window, parent):
                parent.update_idletasks()
                width = window.winfo_width()
                height = window.winfo_height()
                x = parent.winfo_x() + (parent.winfo_width() - width) // 2
                y = parent.winfo_y() + (parent.winfo_height() - height) // 2
                window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Чекаємо поки вікно буде створено і центруємо його
            result_window.update_idletasks()
            center_window(result_window, self.root)
            
            # Робимо вікно модальним
            result_window.transient(self.root)
            result_window.grab_set()
            result_window.focus_set()
            
            # Контейнер для всього вмісту з відступами
            content_frame = tk.Frame(result_window, bg="#f0f8ff")
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Додаємо статистику
            tk.Label(content_frame, 
                    text="🎉 Тренування завершено!",
                    font=("Arial", 20, "bold"),
                    bg="#f0f8ff",
                    fg="#2c3e50").pack(pady=(0, 20))
                    
            stats_frame = tk.Frame(content_frame, bg="#f0f8ff")
            stats_frame.pack(fill=tk.X, pady=(0, 20))
            
            tk.Label(stats_frame,
                    text=f"✅ Правильних відповідей з першого разу: {len(self.training_data) - self.mistake_count}",
                    font=("Arial", 12),
                    bg="#f0f8ff",
                    fg="#27ae60").pack(pady=5)
                    
            tk.Label(stats_frame,
                    text=f"❌ Слів з помилками: {self.mistake_count}",
                    font=("Arial", 12),
                    bg="#f0f8ff",
                    fg="#c0392b").pack(pady=5)
                    
            tk.Label(stats_frame,
                    text=f"📈 Точність: {accuracy:.1f}%",
                    font=("Arial", 12),
                    bg="#f0f8ff",
                    fg="#2980b9").pack(pady=5)
            
            # Кнопки дій
            buttons_frame = tk.Frame(content_frame, bg="#f0f8ff")
            buttons_frame.pack(fill=tk.X, padx=20, pady=20)
            
            def restart_training():
                result_window.destroy()
                self.training_index = 0
                self.mistake_count = 0
                self.score = 0
                self.attempts_count = 0
                random.shuffle(self.training_data)  # Перемішуємо слова знову
                self.training_ui()
            
            def return_to_menu():
                result_window.destroy()
                self.create_main_menu()
            
            # Кнопка "Спробувати ще раз"
            retry_btn = tk.Button(buttons_frame,
                                text="🔄 Спробувати ще раз",
                                font=("Arial", 12),
                                bg="#3498db",
                                fg="white",
                                relief=tk.FLAT,
                                command=restart_training)
            retry_btn.pack(fill=tk.X, pady=5)
            
            # Кнопка "Повернутися в меню"
            menu_btn = tk.Button(buttons_frame,
                               text="🏠 Повернутися в меню",
                               font=("Arial", 12),
                               bg="#95a5a6",
                               fg="white",
                               relief=tk.FLAT,
                               command=return_to_menu)
            menu_btn.pack(fill=tk.X, pady=5)
            
            # Ховер-ефекти для кнопок
            for btn, color in [(retry_btn, "#3498db"), (menu_btn, "#95a5a6")]:
                btn.bind("<Enter>", lambda e, btn=btn, color=color: 
                        btn.configure(bg=self.darken_color(color)))
                btn.bind("<Leave>", lambda e, btn=btn, color=color: 
                        btn.configure(bg=color))
            
            return
            
        # Продовження тренування...
        # Головний контейнер
        main_container = tk.Frame(self.root, bg="#f0f8ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Прогрес
        progress_frame = tk.Frame(main_container, bg="#f0f8ff")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        progress = f"Слово {self.training_index + 1} з {len(self.training_data)}"
        tk.Label(progress_frame, text=progress, 
                font=("Arial", 12), bg="#f0f8ff", fg="#7f8c8d").pack()
        
        # Прогрес-бар
        progress_value = (self.training_index + 1) / len(self.training_data) * 100
        progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        progress_bar.pack(pady=5)
        progress_bar['value'] = progress_value
        
        word = self.training_data[self.training_index]
        self.current_word = word
        
        # Показуємо слово для перекладу
        if self.training_mode == "EN-UA":
            question = word["english"]
            self.correct_answer = word["ukrainian"]
            flag_from, flag_to = "🇬🇧", "🇺🇦"
        else:
            question = word["ukrainian"]
            self.correct_answer = word["english"]
            flag_from, flag_to = "🇺🇦", "🇬🇧"
        
        # Урок
        lesson_name = word.get("lesson", "Головний")
        if lesson_name != "Головний":
            tk.Label(main_container, text=f"📚 Урок: {lesson_name}",
                    font=("Arial", 10), bg="#f0f8ff", fg="#7f8c8d").pack()
        
        # Напрямок перекладу
        tk.Label(main_container, text=f"{flag_from} ➡️ {flag_to}",
                font=("Arial", 14), bg="#f0f8ff").pack(pady=5)
        
        # Слово для перекладу
        tk.Label(main_container, text=question,
                font=("Arial", 24, "bold"), bg="#f0f8ff", fg="#2c3e50").pack(pady=20)
        
        # Підказка (якщо є спроби)
        if self.attempts_count > 1:
            hint = self.correct_answer[:min(self.attempts_count-1, len(self.correct_answer))]
            tk.Label(main_container, text=f"💡 Підказка: {hint}...",
                    font=("Arial", 12), bg="#f0f8ff", fg="#e67e22").pack(pady=5)
        
        # Поле для введення
        answer_frame = tk.Frame(main_container, bg="#f0f8ff")
        answer_frame.pack(fill=tk.X, pady=10)
        
        answer_entry = tk.Entry(answer_frame, 
                              font=("Arial", 14),
                              width=30,
                              justify='center')
        answer_entry.pack()
        answer_entry.focus()
        
        def check_answer(event=None):
            user_answer = answer_entry.get().strip().lower()
            correct = self.correct_answer.lower()
            
            if user_answer == correct:
                if self.attempts_count == 0:  # Правильно з першого разу
                    self.score += 1
                else:  # Правильно, але не з першого разу
                    self.mistake_count += 1
                    
                messagebox.showinfo("✅ Правильно!", "Молодець! 👍")
                self.training_index += 1
                self.attempts_count = 0  # Скидаємо лічильник спроб
                self.training_ui()
            else:
                self.attempts_count += 1  # Збільшуємо лічильник спроб
                messagebox.showwarning("❌ Неправильно!", "Спробуйте ще раз!")
                self.training_ui()
        
        # Кнопка перевірки
        check_btn = tk.Button(main_container, text="Перевірити ✓",
                            font=("Arial", 12),
                            bg="#3498db",
                            fg="white",
                            relief=tk.FLAT,
                            width=15,
                            command=check_answer)
        check_btn.pack(pady=10)
        
        # Кнопка виходу
        exit_btn = tk.Button(main_container, text="🚪 Вийти",
                           font=("Arial", 12),
                           bg="#e74c3c",
                           fg="white",
                           relief=tk.FLAT,
                           width=15,
                           command=self.create_main_menu)
        exit_btn.pack(pady=5)
        
        # Ховер-ефекти
        check_btn.bind("<Enter>", lambda e: check_btn.configure(bg=self.darken_color("#3498db")))
        check_btn.bind("<Leave>", lambda e: check_btn.configure(bg="#3498db"))
        exit_btn.bind("<Enter>", lambda e: exit_btn.configure(bg=self.darken_color("#e74c3c")))
        exit_btn.bind("<Leave>", lambda e: exit_btn.configure(bg="#e74c3c"))
        
        # Прив'язуємо Enter до перевірки
        self.root.bind("<Return>", check_answer)

    def add_word_ui(self):
        """Інтерфейс додавання нового слова."""
        self.clear_window()
        
        # Головний контейнер
        main_container = tk.Frame(self.root, bg="#f0f8ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Заголовок
        tk.Label(main_container, text="➕ Додати нове слово", 
                font=("Arial", 24, "bold"), bg="#f0f8ff", fg="#2c3e50").pack(pady=20)
        
        # Вибір уроку
        tk.Label(main_container, text="Урок:", 
                font=("Arial", 14), bg="#f0f8ff", fg="#34495e").pack(pady=(0, 5))
        
        lessons = [lesson["name"] for lesson in get_lessons()]
        
        # Якщо список уроків порожній, створюємо урок "Головний"
        if not lessons:
            print("UI: Список уроків порожній. Створюємо урок 'Головний'")
            create_lesson("Головний")
            lessons = [lesson["name"] for lesson in get_lessons()]
            if not lessons:  # Якщо все ще немає уроків, використовуємо замінник
                lessons = ["Головний"]
        
        self.lesson_var = tk.StringVar(value=lessons[0])
        
        lesson_dropdown = ttk.Combobox(main_container, textvariable=self.lesson_var, 
                                      values=lessons, state="readonly", 
                                      width=30, font=("Arial", 12))
        lesson_dropdown.pack(pady=(0, 20))
        
        # Поле для англійського слова
        tk.Label(main_container, text="🇬🇧 Англійське слово:", 
                font=("Arial", 14), bg="#f0f8ff", fg="#34495e").pack(pady=(0, 5))
        
        english_entry = tk.Entry(main_container, 
                               font=("Arial", 14),
                               width=30,
                               justify='center')
        english_entry.pack(pady=(0, 20))
        
        # Поле для українського перекладу
        tk.Label(main_container, text="🇺🇦 Український переклад:", 
                font=("Arial", 14), bg="#f0f8ff", fg="#34495e").pack(pady=(0, 5))
        
        ukrainian_entry = tk.Entry(main_container, 
                                 font=("Arial", 14),
                                 width=30,
                                 justify='center')
        ukrainian_entry.pack(pady=(0, 20))
        
        def save_new_word():
            english = english_entry.get().strip()
            ukrainian = ukrainian_entry.get().strip()
            lesson = self.lesson_var.get()
            
            if not english or not ukrainian:
                messagebox.showwarning("Помилка", "Будь ласка, заповніть обидва поля!")
                return
                
            # Зберігаємо нове слово
            print(f"UI: Спроба зберегти слово: {english} - {ukrainian} в урок {lesson}")
            result = save_word(english, ukrainian, lesson)
            print(f"UI: Результат збереження слова: {result}")
            
            if result:
                # Очищаємо поля
                english_entry.delete(0, tk.END)
                ukrainian_entry.delete(0, tk.END)
                
                messagebox.showinfo("Успіх", "✅ Слово успішно додано!")
            else:
                messagebox.showerror("Помилка", "❌ Не вдалося зберегти слово! Можливо, таке слово вже існує або є проблема з базою даних.")
            
        # Кнопка збереження
        save_btn = tk.Button(main_container, text="💾 Зберегти",
                           font=("Arial", 12),
                           bg="#2ecc71",
                           fg="white",
                           relief=tk.FLAT,
                           width=15,
                           command=save_new_word)
        save_btn.pack(pady=10)
        
        # Кнопка створення нового уроку
        def create_new_lesson():
            lesson_name = simpledialog.askstring("Новий урок", "Введіть назву нового уроку:")
            if lesson_name:
                print(f"UI: Спроба створити урок: {lesson_name}")
                result = create_lesson(lesson_name)
                print(f"UI: Результат створення уроку: {result}")
                
                if result:
                    # Оновлюємо список уроків
                    lessons = [lesson["name"] for lesson in get_lessons()]
                    lesson_dropdown['values'] = lessons
                    self.lesson_var.set(lesson_name)
                    messagebox.showinfo("Успіх", "✅ Урок успішно створено!")
                else:
                    messagebox.showerror("Помилка", "❌ Не вдалося створити урок! Можливо, урок з такою назвою вже існує або є проблема з базою даних.")
        
        new_lesson_btn = tk.Button(main_container, text="📚 Створити урок",
                                font=("Arial", 12),
                                bg="#3498db",
                                fg="white",
                                relief=tk.FLAT,
                                width=15,
                                command=create_new_lesson)
        new_lesson_btn.pack(pady=5)
        
        # Кнопка "Назад"
        back_btn = tk.Button(main_container, text="🔙 Назад",
                           font=("Arial", 12),
                           bg="#e74c3c",
                           fg="white",
                           relief=tk.FLAT,
                           width=15,
                           command=self.create_main_menu)
        back_btn.pack(pady=5)
        
        # Ховер-ефекти
        for btn, color in [(save_btn, "#2ecc71"), 
                          (new_lesson_btn, "#3498db"), 
                          (back_btn, "#e74c3c")]:
            btn.bind("<Enter>", lambda e, btn=btn, color=color: 
                    btn.configure(bg=self.darken_color(color)))
            btn.bind("<Leave>", lambda e, btn=btn, color=color: 
                    btn.configure(bg=color))
        
        # Фокус на перше поле
        english_entry.focus()

    def show_dictionary(self):
        """Показує словник з усіма невивченими словами."""
        self.clear_window()
        
        # Головний контейнер
        main_container = tk.Frame(self.root, bg="#f0f8ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Заголовок
        tk.Label(main_container, text="📖 Словник", 
                font=("Arial", 24, "bold"), bg="#f0f8ff", fg="#2c3e50").pack(pady=20)

        # Фрейм для вибору уроку
        lesson_frame = tk.Frame(main_container, bg="#f0f8ff")
        lesson_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Мітка для уроку
        tk.Label(lesson_frame, text="Урок:", 
                font=("Arial", 12), bg="#f0f8ff", fg="#34495e").pack(side=tk.LEFT, padx=5)
        
        # Отримуємо список уроків
        lessons = ["Всі уроки"] + [lesson["name"] for lesson in get_lessons()]
        lesson_var = tk.StringVar(value="Головний")
        
        # Комбобокс для вибору уроку
        lesson_combo = ttk.Combobox(lesson_frame, 
                                  textvariable=lesson_var,
                                  values=lessons,
                                  state="readonly",
                                  font=("Arial", 12),
                                  width=20)
        lesson_combo.pack(side=tk.LEFT, padx=5)

        def rename_current_lesson():
            current_lesson = lesson_var.get()
            if current_lesson == "Всі уроки":
                messagebox.showwarning("Попередження", "Виберіть конкретний урок для перейменування!")
                return
                
            new_name = simpledialog.askstring("Перейменування уроку", 
                                            f"Введіть нову назву для уроку '{current_lesson}':",
                                            initialvalue=current_lesson)
            
            if new_name and new_name != current_lesson:
                if rename_lesson(current_lesson, new_name):
                    # Оновлюємо список уроків
                    lessons = ["Всі уроки"] + [lesson["name"] for lesson in get_lessons()]
                    lesson_combo['values'] = lessons
                    lesson_var.set(new_name)
                    # Оновлюємо список слів
                    update_words_list()
                    messagebox.showinfo("Успіх", "✅ Урок успішно перейменовано!")
                else:
                    messagebox.showerror("Помилка", "Не вдалося перейменувати урок!")
        
        # Кнопка для перейменування уроку
        rename_btn = tk.Button(lesson_frame,
                             text="📝",
                             font=("Arial", 12),
                             bg="#f39c12",
                             fg="white",
                             relief=tk.FLAT,
                             command=rename_current_lesson)
        rename_btn.pack(side=tk.LEFT, padx=5)
        
        # Ховер-ефект для кнопки перейменування
        rename_btn.bind("<Enter>", lambda e: rename_btn.configure(bg=self.darken_color("#f39c12")))
        rename_btn.bind("<Leave>", lambda e: rename_btn.configure(bg="#f39c12"))
        
        def filter_words(event=None):
            """Фільтрує слова за вибраним уроком."""
            selected_lesson = lesson_var.get()
            if selected_lesson == "Всі уроки":
                selected_lesson = None
            update_words_list(lesson_name=selected_lesson)
        
        lesson_combo.bind('<<ComboboxSelected>>', filter_words)
        
        # Фрейм для списку слів
        words_frame = tk.Frame(main_container, bg="#f0f8ff")
        words_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Створюємо скроллбар
        scrollbar = ttk.Scrollbar(words_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Створюємо список
        words_list = tk.Listbox(words_frame, 
                      font=("Consolas", 14),
                      bg="white",
                      selectmode=tk.SINGLE,
                      height=15,
                      width=40,
                      selectbackground="#e0e0e0",
                      selectforeground="#00d303",
                      activestyle="none",
                      highlightthickness=0,
                      yscrollcommand=scrollbar.set)
        words_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=words_list.yview)

        # Додаємо обробник клавіш для коректної роботи стрілок
        def on_key_press(event):
            if event.keysym == 'Up' or event.keysym == 'Down':
            # Отримуємо поточний вибір
                selection = words_list.curselection()
                if selection:
                    index = selection[0]
                    if event.keysym == 'Up' and index > 0:
                            words_list.selection_clear(0, tk.END)
                            words_list.selection_set(index - 1)
                            words_list.see(index - 1)
                            words_list.event_generate('<<ListboxSelect>>')
                    elif event.keysym == 'Down' and index < words_list.size() - 1:
                            words_list.selection_clear(0, tk.END)
                            words_list.selection_set(index + 1)
                            words_list.see(index + 1)
                            words_list.event_generate('<<ListboxSelect>>')
                return 'break'  # Забороняємо стандартну обробку

            # Прив'язуємо обробник подій клавіатури
        words_list.bind('<KeyPress>', on_key_press)
        
        def update_words_list(select_index=None, lesson_name=None):
            """Оновлює список невивчених слів."""
            words_list.delete(0, tk.END)
            words = load_words(lesson_name, show_learned=False)  # Показуємо тільки невивчені слова
            # Знаходимо найдовше англійське слово для вирівнювання
            max_eng_len = max(len(word) for word in words.keys()) if words else 0
            fixed_width = max_eng_len + 10  # Додаємо відступ після англійського слова
            
            # Сортуємо слова за англійським алфавітом
            sorted_words = sorted(words.items(), key=lambda x: x[0].lower())
            
            for en_word, details in sorted_words:
                ua_word = details["translation"]
                words_list.insert(tk.END, f"❌ {en_word:<{fixed_width}}{ua_word}")
            if select_index is not None and select_index < words_list.size():
                words_list.selection_set(select_index)
                create_word_buttons(select_index)
        
        # Початкове завантаження слів для уроку "Головний"
        update_words_list(lesson_name="Головний")
        
        # Фрейм для кнопок дій зі словами
        word_actions_frame = tk.Frame(main_container, bg="#f0f8ff")
        word_actions_frame.pack(fill=tk.X, pady=10)
        
        def create_word_buttons(index):
            """Створює кнопки для вибраного слова."""
            for widget in word_actions_frame.winfo_children():
                widget.destroy()
                
            if not (0 <= index < words_list.size()):
                return
                
            item = words_list.get(index)
            # Отримуємо англійське слово (між статусом і перекладом)
            # Формат рядка: "❌ {en_word:<{fixed_width}}{ua_word}"
            # Видаляємо символ статусу і пробіл
            cleaned_item = item[2:].strip()
            # Розділяємо на англійське слово та переклад (англійське слово має фіксовану ширину з пробілами)
            en_word = cleaned_item.strip().split()[0]
            
            def toggle_learned_state():
                if toggle_word_learned(en_word):
                    # Оновлюємо список слів, зберігаючи поточний урок
                    current_lesson = lesson_var.get()
                    if current_lesson == "Всі уроки":
                        current_lesson = None
                    update_words_list(lesson_name=current_lesson)
                else:
                    messagebox.showerror("Помилка", "Не вдалося змінити статус слова!")
            
            # Кнопка позначення слова як вивченого
            learn_btn = tk.Button(word_actions_frame,
                                text="✅ Позначити як вивчене",
                                font=("Arial", 12),
                                bg="#2ecc71",
                                fg="white",
                                relief=tk.FLAT,
                                command=toggle_learned_state)
            learn_btn.pack(side=tk.LEFT, padx=5, expand=True)
            
            # Кнопка редагування
            edit_btn = tk.Button(word_actions_frame,
                               text="✏️ Змінити",
                               font=("Arial", 12),
                               bg="#3498db",
                               fg="white",
                               relief=tk.FLAT,
                               command=lambda: edit_word(en_word, index))
            edit_btn.pack(side=tk.LEFT, padx=5, expand=True)
            
            # Кнопка видалення
            delete_btn = tk.Button(word_actions_frame,
                                text="🗑️ Видалити",
                                font=("Arial", 12),
                                bg="#e74c3c",
                                fg="white",
                                relief=tk.FLAT,
                                command=lambda: delete_word(en_word, index))
            delete_btn.pack(side=tk.LEFT, padx=5, expand=True)
            
            # Ховер-ефекти
            for btn, color in [(learn_btn, "#2ecc71"), (edit_btn, "#3498db"), (delete_btn, "#e74c3c")]:
                btn.bind("<Enter>", lambda e, btn=btn, color=color: 
                        btn.configure(bg=self.darken_color(color)))
                btn.bind("<Leave>", lambda e, btn=btn, color=color: 
                        btn.configure(bg=color))
        
        def on_select(event):
            selection = words_list.curselection()
            if selection:
                create_word_buttons(selection[0])
        
        words_list.bind('<<ListboxSelect>>', on_select)
        
        def edit_word(en_word, index):
            """Редагує вибране слово."""
            # Отримуємо деталі слова
            words = load_words()
            if en_word not in words:
                messagebox.showerror("Помилка", "Слово не знайдено!")
                return
                
            word_details = words[en_word]
            ua_word = word_details["translation"]
            current_lesson = word_details.get("lesson", "Головний")
            
            # Створюємо діалогове вікно для редагування
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Редагування слова")
            edit_window.geometry("400x300")
            edit_window.configure(bg="#f0f8ff")
            edit_window.resizable(False, False)
            edit_window.transient(self.root)  # Робимо вікно модальним
            edit_window.grab_set()  # Блокуємо головне вікно
            
            # Центруємо вікно
            def center_window(window, parent):
                parent_x = parent.winfo_x()
                parent_y = parent.winfo_y()
                parent_width = parent.winfo_width()
                parent_height = parent.winfo_height()
                
                width = window.winfo_width()
                height = window.winfo_height()
                
                x = parent_x + (parent_width - width) // 2
                y = parent_y + (parent_height - height) // 2
                
                window.geometry(f"+{x}+{y}")
            
            # Викликаємо після того, як вікно буде створено
            edit_window.update_idletasks()
            center_window(edit_window, self.root)
            
            # Заголовок
            tk.Label(edit_window, text="✏️ Редагування слова", 
                   font=("Arial", 16, "bold"), bg="#f0f8ff", fg="#2c3e50").pack(pady=10)
            
            # Фрейм для полів вводу
            input_frame = tk.Frame(edit_window, bg="#f0f8ff")
            input_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Поле для англійського слова
            tk.Label(input_frame, text="🇬🇧 Англійське слово:", 
                   font=("Arial", 12), bg="#f0f8ff", fg="#34495e").pack(anchor=tk.W, pady=(0, 5))
            
            english_entry = tk.Entry(input_frame, 
                                  font=("Arial", 12),
                                  width=30,
                                  justify='left')
            english_entry.pack(fill=tk.X, pady=(0, 10))
            english_entry.insert(0, en_word)  # Встановлюємо поточне значення
            
            # Поле для українського перекладу
            tk.Label(input_frame, text="🇺🇦 Український переклад:", 
                   font=("Arial", 12), bg="#f0f8ff", fg="#34495e").pack(anchor=tk.W, pady=(0, 5))
            
            ukrainian_entry = tk.Entry(input_frame, 
                                    font=("Arial", 12),
                                    width=30,
                                    justify='left')
            ukrainian_entry.pack(fill=tk.X, pady=(0, 10))
            ukrainian_entry.insert(0, ua_word)  # Встановлюємо поточне значення
            
            # Вибір уроку
            tk.Label(input_frame, text="Урок:", 
                   font=("Arial", 12), bg="#f0f8ff", fg="#34495e").pack(anchor=tk.W, pady=(0, 5))
            
            lessons = [lesson["name"] for lesson in get_lessons()]
            lesson_var = tk.StringVar(value=current_lesson)
            
            lesson_dropdown = ttk.Combobox(input_frame, textvariable=lesson_var, 
                                       values=lessons, state="readonly", 
                                       width=30, font=("Arial", 12))
            lesson_dropdown.pack(fill=tk.X, pady=(0, 10))
            
            # Фрейм для кнопок
            button_frame = tk.Frame(edit_window, bg="#f0f8ff")
            button_frame.pack(fill=tk.X, pady=10, padx=20)
            
            # Функція для збереження змін
            def save_changes():
                new_english = english_entry.get().strip()
                new_ukrainian = ukrainian_entry.get().strip()
                new_lesson = lesson_var.get()
                
                if not new_english or not new_ukrainian:
                    messagebox.showwarning("Помилка", "Будь ласка, заповніть обидва поля!")
                    return
                
                # Імпортуємо функцію оновлення слова
                from db import update_word
                
                # Оновлюємо слово в базі даних
                if update_word(en_word, new_english, new_ukrainian, new_lesson):
                    messagebox.showinfo("Успіх", "✅ Слово успішно оновлено!")
                    edit_window.destroy()
                    
                    # Оновлюємо список слів
                    current_lesson_filter = lesson_var.get()
                    if current_lesson_filter == "Всі уроки":
                        current_lesson_filter = None
                    update_words_list(lesson_name=current_lesson_filter)
                else:
                    messagebox.showerror("Помилка", "Не вдалося оновити слово! Можливо, слово з такою назвою вже існує.")
            
            # Кнопка збереження
            save_btn = tk.Button(button_frame, text="💾 Зберегти",
                              font=("Arial", 12),
                              bg="#2ecc71",
                              fg="white",
                              relief=tk.FLAT,
                              width=10,
                              command=save_changes)
            save_btn.pack(side=tk.LEFT, padx=5, expand=True)
            
            # Кнопка скасування
            cancel_btn = tk.Button(button_frame, text="❌ Скасувати",
                                font=("Arial", 12),
                                bg="#e74c3c",
                                fg="white",
                                relief=tk.FLAT,
                                width=10,
                                command=edit_window.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5, expand=True)
            
            # Ховер-ефекти
            for btn, color in [(save_btn, "#2ecc71"), (cancel_btn, "#e74c3c")]:
                btn.bind("<Enter>", lambda e, btn=btn, color=color: 
                        btn.configure(bg=self.darken_color(color)))
                btn.bind("<Leave>", lambda e, btn=btn, color=color: 
                        btn.configure(bg=color))
            
            # Фокус на перше поле
            english_entry.focus()
        
        def delete_word(en_word, index):
            if messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете видалити слово '{en_word}'?"):
                words = load_words()
                if en_word in words:
                    del words[en_word]
                    from db import save_words
                    save_words(words)
                    update_words_list()
                    # Очищаємо фрейм з кнопками
                    for widget in word_actions_frame.winfo_children():
                        widget.destroy()
                    messagebox.showinfo("Успіх", "✅ Слово успішно видалено!")
        
        # Кнопка "Назад"
        back_btn = tk.Button(main_container, 
                           text="🔙 Назад",
                           font=("Arial", 12),
                           bg="#95a5a6",
                           fg="white",
                           relief=tk.FLAT,
                           command=self.create_main_menu)
        back_btn.pack(pady=10)
        
        # Ховер-ефект для кнопки "Назад"
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg=self.darken_color("#95a5a6")))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#95a5a6"))

    def show_learned_words(self):
        """Показує вивчені слова."""
        self.clear_window()
        
        # Головний контейнер
        main_container = tk.Frame(self.root, bg="#f0f8ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Заголовок
        tk.Label(main_container, text="📚 Вивчені слова", 
                font=("Arial", 24, "bold"), bg="#f0f8ff", fg="#2c3e50").pack(pady=20)

        # Фрейм для вибору уроку
        lesson_frame = tk.Frame(main_container, bg="#f0f8ff")
        lesson_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Мітка для уроку
        tk.Label(lesson_frame, text="Урок:", 
                font=("Arial", 12), bg="#f0f8ff", fg="#34495e").pack(side=tk.LEFT, padx=5)
        
        # Отримуємо список уроків
        lessons = ["Всі уроки"] + [lesson["name"] for lesson in get_lessons()]
        lesson_var = tk.StringVar(value="Головний")  # Встановлюємо "Головний" за замовчуванням
        
        # Комбобокс для вибору уроку
        lesson_combo = ttk.Combobox(lesson_frame, 
                                  textvariable=lesson_var,
                                  values=lessons,
                                  state="readonly",
                                  font=("Arial", 12),
                                  width=20)
        lesson_combo.pack(side=tk.LEFT, padx=5)
        
        # Фрейм для списку слів
        words_frame = tk.Frame(main_container, bg="#f0f8ff")
        words_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Створюємо скроллбар
        scrollbar = ttk.Scrollbar(words_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Створюємо список
        words_list = tk.Listbox(words_frame, 
                              font=("Arial", 12),
                              bg="white",
                              selectmode=tk.SINGLE,
                              height=15,
                              width=40,
                              yscrollcommand=scrollbar.set)
        words_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=words_list.yview)
        
        # Фрейм для кнопок дій зі словами
        word_actions_frame = tk.Frame(main_container, bg="#f0f8ff")
        word_actions_frame.pack(fill=tk.X, pady=10)
        
        def create_word_buttons(index):
            """Створює кнопки для вибраного слова."""
            for widget in word_actions_frame.winfo_children():
                widget.destroy()
                
            if not (0 <= index < words_list.size()):
                return
                
            item = words_list.get(index)
            # Отримуємо англійське слово (між статусом і перекладом)
            # Формат рядка: "❌ {en_word:<{fixed_width}}{ua_word}"
            # Видаляємо символ статусу і пробіл
            cleaned_item = item[2:].strip()
            # Розділяємо на англійське слово та переклад (англійське слово має фіксовану ширину з пробілами)
            en_word = cleaned_item.strip().split()[0]
            
            def toggle_learned_state():
                if toggle_word_learned(en_word):
                    messagebox.showinfo("Успіх", "✅ Слово повернуто в словник!")
                    # Оновлюємо список слів, зберігаючи поточний урок
                    current_lesson = lesson_var.get()
                    if current_lesson == "Всі уроки":
                        current_lesson = None
                    update_learned_words_list(lesson_name=current_lesson)
                else:
                    messagebox.showerror("Помилка", "Не вдалося змінити статус слова!")
            
            # Кнопка повернення слова в словник
            unlearn_btn = tk.Button(word_actions_frame,
                                text="❌ Повернути в словник",
                                font=("Arial", 12),
                                bg="#e74c3c",
                                fg="white",
                                relief=tk.FLAT,
                                command=toggle_learned_state)
            unlearn_btn.pack(side=tk.LEFT, padx=5, expand=True)
            
            # Ховер-ефект
            unlearn_btn.bind("<Enter>", lambda e: unlearn_btn.configure(bg=self.darken_color("#e74c3c")))
            unlearn_btn.bind("<Leave>", lambda e: unlearn_btn.configure(bg="#e74c3c"))
        
        def on_select(event):
            selection = words_list.curselection()
            if selection:
                create_word_buttons(selection[0])
        
        words_list.bind('<<ListboxSelect>>', on_select)
        
        def update_learned_words_list(lesson_name=None):
            """Оновлює список вивчених слів."""
            words_list.delete(0, tk.END)
            words = load_words(lesson_name, show_learned=True)
            
            # Сортуємо слова за англійським алфавітом
            sorted_words = sorted(words.items(), key=lambda x: x[0].lower())
            
            for en_word, details in sorted_words:
                ua_word = details["translation"]
                words_list.insert(tk.END, f"✅ {en_word} - {ua_word}")
            # Очищаємо фрейм з кнопками
            for widget in word_actions_frame.winfo_children():
                widget.destroy()
        
        def filter_words(event=None):
            """Фільтрує слова за вибраним уроком."""
            selected_lesson = lesson_var.get()
            if selected_lesson == "Всі уроки":
                selected_lesson = None
            update_learned_words_list(selected_lesson)
        
        lesson_combo.bind('<<ComboboxSelected>>', filter_words)
        
        # Початкове завантаження вивчених слів для уроку "Головний"
        update_learned_words_list("Головний")
        
        # Кнопка "Назад"
        back_btn = tk.Button(main_container, 
                           text="🔙 Назад",
                           font=("Arial", 12),
                           bg="#95a5a6",
                           fg="white",
                           relief=tk.FLAT,
                           command=self.create_main_menu)
        back_btn.pack(pady=10)
        
        # Ховер-ефект для кнопки "Назад"
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg=self.darken_color("#95a5a6")))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#95a5a6"))

def run_ui():
    root = tk.Tk()
    app = WordTrainerApp(root)
    root.mainloop()     