import tkinter as tk
from task_tracker import TaskTracker
from translations import translations

if __name__ == "__main__":
    language_choice = 'ru'  # Выбираем язык 'ru' для примера
    main_window = tk.Tk()
    app = TaskTracker(main_window, language=language_choice)
    main_window.mainloop()
