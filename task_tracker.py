import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import locale
from datetime import datetime
from database import add_task_to_db, get_tasks_from_db, update_task_in_db, delete_task_from_db
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

        self.tasks_frame = ttk.Frame(self.main_frame)
        self.tasks_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.tasks_canvas = tk.Canvas(self.tasks_frame)
        self.tasks_scrollbar = ttk.Scrollbar(self.tasks_frame, orient='vertical', command=self.tasks_canvas.yview)
        self.tasks_listbox_frame = ttk.Frame(self.tasks_canvas)

        self.tasks_listbox_frame.bind("<Configure>", lambda e: self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all")))

        self.tasks_canvas.create_window((0, 0), window=self.tasks_listbox_frame, anchor="nw")
        self.tasks_canvas.configure(yscrollcommand=self.tasks_scrollbar.set)

        self.tasks_canvas.grid(row=0, column=0, sticky="nsew")
        self.tasks_scrollbar.grid(row=0, column=1, sticky="ns")

        self.load_tasks()

        self.language_var = tk.StringVar(value=self.language)
        self.language_combobox = ttk.Combobox(self.main_frame, textvariable=self.language_var, values=['en', 'ru'],
                                              state='readonly')
        self.language_combobox.grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.language_combobox.bind('<<ComboboxSelected>>', self.change_language)

        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8' if self.language == 'ru' else 'en_US.UTF-8')

        self.tooltip = None

    def change_language(self, _):
        self.language = self.language_var.get()
        self.update_ui()
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8' if self.language == 'ru' else 'en_US.UTF-8')
        self.date_entry.config(locale=locale.getlocale(locale.LC_TIME)[0])

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
                messagebox.showwarning(translations[self.language]['warning'], translations[self.language]['invalid_date_warning'])
        else:
            messagebox.showwarning(translations[self.language]['warning'], translations[self.language]['missing_title_warning'])

    def load_tasks(self):
        for widget in self.tasks_listbox_frame.winfo_children():
            widget.destroy()

        tasks = get_tasks_from_db()
        for task in tasks:
            self.add_task_to_frame(task)

    def add_task_to_frame(self, task, task_id=None):
        task_frame = ttk.Frame(self.tasks_listbox_frame)
        task_frame.pack(fill='x', padx=5, pady=2)

        task_id = task[0]
        title = task[1]
        due_date = task[3]
        priority = task[4]
        creation_time = task[5]

        task_label = tk.Label(task_frame, text=f"{task_id}: {title} - Приоритет: {priority}, Срок: {due_date}, Создано: {creation_time}", anchor='w')
        task_label.pack(side='left', fill='x', expand=True)
        task_label.bind('<Enter>', lambda e, task_id=task_id: self.show_task_tooltip(e, task_id))
        task_label.bind('<Leave>', self.hide_tooltip)
        task_label.bind('<Double-1>', lambda e, task_id=task_id: self.edit_task(e, task_id))

        delete_button = ttk.Button(task_frame, text="🗑️", width=3, command=lambda task_id=task_id: self.delete_task(task_id))
        delete_button.pack(side='right')

    def delete_task(self, task_id):
        delete_task_from_db(task_id)
        self.load_tasks()

    def edit_task(self, event, task_id):
        task_details = [task for task in get_tasks_from_db() if task[0] == task_id][0]
        if task_details:
            self.edit_task_dialog(task_id, task_details)

    def edit_task_dialog(self, task_id, task_details):
        edit_window = tk.Toplevel(self.root)
        edit_window.title(translations[self.language]['edit_task'])

        title_label = ttk.Label(edit_window, text=translations[self.language]['title_label'])
        title_label.grid(row=0, column=0, padx=5, pady=5)

        title_entry = ttk.Entry(edit_window, width=30)
        title_entry.grid(row=0, column=1, padx=5, pady=5)
        title_entry.insert(0, task_details[1])

        desc_label = ttk.Label(edit_window, text=translations[self.language]['desc_label'])
        desc_label.grid(row=1, column=0, padx=5, pady=5)

        desc_entry = ttk.Entry(edit_window, width=30)
        desc_entry.grid(row=1, column=1, padx=5, pady=5)
        desc_entry.insert(0, task_details[2])

        date_label = ttk.Label(edit_window, text=translations[self.language]['date_label'])
        date_label.grid(row=2, column=0, padx=5, pady=5)

        date_entry = DateEntry(edit_window, width=30, date_pattern='yyyy-mm-dd')
        date_entry.grid(row=2, column=1, padx=5, pady=5)
        date_entry.set_date(task_details[3])

        priority_label = ttk.Label(edit_window, text=translations[self.language]['priority_label'])
        priority_label.grid(row=3, column=0, padx=5, pady=5)

        priority_var = tk.StringVar(edit_window)
        priority_var.set(task_details[4])
        priority_option = ttk.OptionMenu(edit_window, priority_var, task_details[4], "1", "2", "3", "4", "5")
        priority_option.grid(row=3, column=1, padx=5, pady=5)

        def save_changes():
            new_title = title_entry.get()
            new_desc = desc_entry.get()
            new_date = date_entry.get()
            new_priority = priority_var.get()
            if new_title and new_priority.isdigit():
                update_task_in_db(task_id, new_title, new_desc, new_date, int(new_priority))
                self.load_tasks()
                edit_window.destroy()
            else:
                messagebox.showwarning(translations[self.language]['warning'], translations[self.language]['missing_title_warning'])

        save_button = ttk.Button(edit_window, text=translations[self.language]['save_button'], command=save_changes)
        save_button.grid(row=4, column=1, padx=5, pady=5)

    def show_task_tooltip(self, event, task_id):
        task_details = [task for task in get_tasks_from_db() if task[0] == task_id][0]
        if task_details:
            tooltip_text = (f"ID: {task_details[0]}\nНазвание: {task_details[1]}\nОписание: {task_details[2]}"
                            f"\nСрок: {task_details[3]}\nПриоритет: {task_details[4]}\nСоздано: {task_details[5]}")
            x, y, width, height = event.widget.bbox("insert")
            self.tooltip = tk.Toplevel(self.root)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root}+{event.y_root}")
            ttk.Label(self.tooltip, text=tooltip_text, background="white", relief="solid", borderwidth=1).pack()

    def hide_tooltip(self, event=None):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            del self.tooltip

# Пример кода для запуска TaskTracker
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTracker(root, language='ru')
    root.mainloop()
