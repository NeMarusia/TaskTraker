import tkinter as tk
from task_tracker import TaskTracker

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTracker(root, language='en')
    root.mainloop()
