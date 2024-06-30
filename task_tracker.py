import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import locale
from database import add_task_to_db, get_tasks_from_db, update_task_in_db, delete_task_from_db, get_task_details_from_db
from translations import translations

class TaskTracker:
    def __init__(self, root, language='en'):
        self.root = root
        self.language = language
        self.root.title(translations[self.language]['task_manager_title'])

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.title_label = ttk.Label(self.main_frame, text=translations[self.language]['title_label'])
        self.title_label.grid(row=0, column=0, padx=5, pady=5)

        self.title_entry = ttk.Entry(self.main_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        self.desc_label = ttk.Label(self.main_frame, text=translations[self.language]['desc_label'])
        self.desc_label.grid(row=1, column=0, padx=5, pady=5)

        self.desc_entry = ttk.Entry(self.main_frame, width=30)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        self.date_label = ttk.Label(self.main_frame, text=translations[self.language]['date_label'])
        self.date_label.grid(row=2, column=0, padx=5, pady=5)

        self.date_entry = DateEntry(self.main_frame, width=30, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        self.priority_label = ttk.Label(self.main_frame, text=translations[self.language]['priority_label'])
        self.priority_label.grid(row=3, column=0, padx=5, pady=5)

        self.priority_var = tk.StringVar(self.main_frame)
        self.priority_var.set("1")
        self.priority_option = ttk.OptionMenu(self.main_frame, self.priority_var, "1", "1", "2", "3", "4", "5")
        self.priority_option.grid(row=3, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(self.main_frame, text=translations[self.language]['add_task_button'], command=self.add_task)
        self.add_button.grid(row=4, column=1, padx=5, pady=5)

        self.tasks_listbox = tk.Listbox(self.main_frame, height=10, width=50)
        self.tasks_listbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self.tasks_listbox.bind('<Double-1>', self.edit_task)
        self.tasks_listbox.bind('<Motion>', self.show_task_tooltip)

        self.load_tasks()

        self.language_var = tk.StringVar(value=self.language)
        self.language_combobox = ttk.Combobox(self.main_frame, textvariable=self.language_var, values=['en', 'ru'],
                                              state='readonly')
        self.language_combobox.grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.language_combobox.bind('<<ComboboxSelected>>', self.change_language)

        locale.setlocale(locale.LC_TIME, 'ru_RU' if self.language == 'ru' else 'en_US')

    def change_language(self, _):
        self.language = self.language_var.get()
        self.update_ui()

    def update_ui(self):
        self.root.title(translations[self.language]['task_manager_title'])
        self.title_label.config(text=translations[self.language]['title_label'])
        self.desc_label.config(text=translations[self.language]['desc_label'])
        self.date_label.config(text=translations[self.language]['date_label'])
        self.priority_label.config(text=translations[self.language]['priority_label'])
        self.add_button.config(text=translations[self.language]['add_task_button'])
        self.load_tasks()

    def add_task(self):
        title = self.title_entry.get()
        description = self.desc_entry.get()
        due_date = self.date_entry.get()
        priority = self.priority_var.get()

        if title and priority.isdigit():
            if due_date:
                add_task_to_db(title, description, due_date, int(priority))
                self.load_tasks()
            else:
                messagebox.showerror(translations[self.language]['error_message'], translations[self.language]['select_due_date_message'])
        else:
            messagebox.showerror(translations[self.language]['error_message'], translations[self.language]['fill_all_fields_message'])

        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.set_date('')
        self.priority_var.set("1")

    def load_tasks(self):
        self.tasks_listbox.delete(0, tk.END)
        tasks = get_tasks_from_db()
        for index, task in enumerate(tasks):
            task_str = f"{task[0]}: {task[1]} - Приоритет: {task[4]}, Срок: {task[3]}"
            self.tasks_listbox.insert(tk.END, task_str)

    def delete_task(self, task_id):
        delete_task_from_db(task_id)
        self.load_tasks()

    def edit_task(self, event=None):
        selected_index = self.tasks_listbox.curselection()
        if selected_index:
            selected_task = self.tasks_listbox.get(selected_index[0])
            task_id, task_title, task_priority, task_due_date = selected_task.split(' - ')
            task_id = int(task_id.split(':')[0])

            # Создаем новое окно для редактирования задачи
            edit_window = tk.Toplevel(self.root)
            edit_window.title(translations[self.language]['task_manager_title'])

            # Добавляем поля для редактирования
            title_label = ttk.Label(edit_window, text=translations[self.language]['title_label'])
            title_label.grid(row=0, column=0, padx=5, pady=5)
            title_entry = ttk.Entry(edit_window, width=30)
            title_entry.grid(row=0, column=1, padx=5, pady=5)
            title_entry.insert(0, task_title)

            desc_label = ttk.Label(edit_window, text=translations[self.language]['desc_label'])
            desc_label.grid(row=1, column=0, padx=5, pady=5)
            desc_entry = ttk.Entry(edit_window, width=30)
            desc_entry.grid(row=1, column=1, padx=5, pady=5)

            date_label = ttk.Label(edit_window, text=translations[self.language]['date_label'])
            date_label.grid(row=2, column=0, padx=5, pady=5)
            date_entry = DateEntry(edit_window, width=30, date_pattern='yyyy-mm-dd')
            date_entry.grid(row=2, column=1, padx=5, pady=5)
            date_entry.set_date(task_due_date.split(': ')[-1])

            priority_label = ttk.Label(edit_window, text=translations[self.language]['priority_label'])
            priority_label.grid(row=3, column=0, padx=5, pady=5)
            priority_var = tk.StringVar(edit_window)
            priority_var.set(task_priority.split(': ')[-1])
            priority_option = ttk.OptionMenu(edit_window, priority_var, task_priority.split(': ')[-1], "1", "2", "3", "4", "5")
            priority_option.grid(row=3, column=1, padx=5, pady=5)

            def save_task():
                new_title = title_entry.get()
                new_description = desc_entry.get()
                new_due_date = date_entry.get()
                new_priority = priority_var.get()

                if new_title and new_priority.isdigit():
                    if new_due_date:
                        update_task_in_db(task_id, new_title, new_description, new_due_date, int(new_priority))
                        self.load_tasks()
                        edit_window.destroy()
                    else:
                        messagebox.showerror(translations[self.language]['error_message'], translations[self.language]['select_due_date_message'])
                else:
                    messagebox.showerror(translations[self.language]['error_message'], translations[self.language]['fill_all_fields_message'])

            save_button = ttk.Button(edit_window, text=translations[self.language]['save_button'], command=save_task)
            save_button.grid(row=4, column=1, padx=5, pady=5)

    def show_task_tooltip(self, event):
        # Получение индекса задачи
        index = self.tasks_listbox.index(tk.ACTIVE)
        if index >= 0:
            task_id = self.tasks_listbox.get(index).split(':')[0]

            # Получение деталей задачи
            task_details = get_task_details_from_db(int(task_id))

            if task_details:
                # Создание и отображение тултипа
                tooltip_text = f"ID: {task_details[0]}\nНазвание: {task_details[1]}\nОписание: {task_details[2]}\nСрок: {task_details[3]}\nПриоритет: {task_details[4]}"
                x, y, _, _ = self.tasks_listbox.bbox(index)
                self.tooltip = tk.Toplevel(self.root)
                self.tooltip.wm_overrideredirect(True)
                self.tooltip.wm_geometry(f"+{x + self.tasks_listbox.winfo_rootx()}+{y + self.tasks_listbox.winfo_rooty()}")
                ttk.Label(self.tooltip, text=tooltip_text, background="white", relief="solid", borderwidth=1).pack()

    def hide_tooltip(self, event=None):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            del self.tooltip

# Пример кода для запуска TaskTracker
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTracker(root, language='en')
    root.mainloop()
