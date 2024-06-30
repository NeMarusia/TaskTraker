import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import *
from translations import translations

class TaskTracker:
    def __init__(self, root, language='en'):
        self.root = root
        self.language = language
        print(f"Initializing TaskTracker with language: {self.language}")
        self.root.title(translations[self.language]['task_manager_title'])

        self.main_frame = ttk.Frame(self.root, padding="10")
        print("Creating main_frame")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.title_label = ttk.Label(self.main_frame, text=translations[self.language]['title_label'])
        print("Creating title_label")
        self.title_label.grid(row=0, column=0, padx=5, pady=5)

        self.title_entry = ttk.Entry(self.main_frame, width=30)
        print("Creating title_entry")
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        self.desc_label = ttk.Label(self.main_frame, text=translations[self.language]['desc_label'])
        print("Creating desc_label")
        self.desc_label.grid(row=1, column=0, padx=5, pady=5)

        self.desc_entry = ttk.Entry(self.main_frame, width=30)
        print("Creating desc_entry")
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        self.date_label = ttk.Label(self.main_frame, text=translations[self.language]['date_label'])
        print("Creating date_label")
        self.date_label.grid(row=2, column=0, padx=5, pady=5)

        self.date_entry = DateEntry(self.main_frame, width=30, date_pattern='yyyy-mm-dd')
        print("Creating date_entry")
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        self.priority_label = ttk.Label(self.main_frame, text=translations[self.language]['priority_label'])
        print("Creating priority_label")
        self.priority_label.grid(row=3, column=0, padx=5, pady=5)

        self.priority_var = tk.StringVar(self.main_frame)
        print("Creating priority_var")
        self.priority_var.set("1")
        print("Setting priority_var to default value: 1")
        self.priority_option = ttk.OptionMenu(self.main_frame, self.priority_var, "1", "1", "2", "3", "4", "5")
        print("Creating priority_option")
        self.priority_option.grid(row=3, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(self.main_frame, text=translations[self.language]['add_task_button'],
                                     command=self.add_task)
        print("Creating add_button")
        self.add_button.grid(row=4, column=1, padx=5, pady=5)

        self.tasks_listbox = tk.Listbox(self.main_frame, height=10, width=50)
        print("Creating tasks_listbox")
        self.tasks_listbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        self.tasks_listbox.bind('<Double-Button-1>', self.edit_task)
        print("Binding edit_task to tasks_listbox")

        print("Loading tasks")
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
        for task in tasks:
            task_str = f"{task[1]} - Приоритет: {task[4]}, Срок: {task[3]}"
            self.tasks_listbox.insert(tk.END, task_str)

            delete_button = tk.Button(self.tasks_listbox, text=translations[self.language]['delete_task_button'], command=lambda t=task[0]: self.delete_task(t))
            delete_button.grid(row=self.tasks_listbox.size() - 1, column=1, sticky=tk.W)

    def delete_task(self, task_id):
        delete_task_from_db(task_id)
        self.load_tasks()

    def edit_task(self, event=None):
        selected_index = self.tasks_listbox.curselection()
        if selected_index:
            selected_task = self.tasks_listbox.get(selected_index)
            task_id = selected_task.split(":")[0]

            entry = ttk.Entry(self.tasks_listbox, width=len(selected_task))
            entry.insert(0, selected_task)
            entry.grid(row=selected_index[0], column=0, sticky="nsew")

            def save_edit():
                new_value = entry.get()
                task_details = new_value.split(": ")[1].split(" - ")

                new_title = task_details[0]
                new_description = task_details[1] if len(task_details) > 1 else ""
                new_due_date = task_details[2] if len(task_details) > 2 else ""
                new_priority = task_details[3] if len(task_details) > 3 else ""

                if new_priority.isdigit():
                    update_task_in_db(task_id, new_title, new_description, new_due_date, int(new_priority))
                    entry.grid_remove()
                    self.load_tasks()
                else:
                    messagebox.showerror(translations[self.language]['error_message'], translations[self.language]['priority_must_be_number'])

            save_button = ttk.Button(self.tasks_listbox, text=translations[self.language]['save_button'], command=save_edit)
            save_button.grid(row=selected_index[0], column=1, sticky="nsew")

            def cancel_edit():
                entry.grid_remove()
                save_button.grid_remove()
                pass  # Placeholder to avoid syntax error

            cancel_button = ttk.Button(self.tasks_listbox, text=translations[self.language]['cancel_button'], command=cancel_edit)
            cancel_button.grid(row=selected_index[0], column=2, sticky="nsew")

# Необходимые функции и словари переводов, как указано ранее
