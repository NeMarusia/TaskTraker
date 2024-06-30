import sqlite3
from datetime import datetime

def init_db() -> None:
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority INTEGER,
                created_at TEXT
            )
            '''
        )
        conn.commit()

def add_task_to_db(title, description, due_date, priority):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO tasks (title, description, due_date, priority, created_at) VALUES (?, ?, ?, ?, ?)
            ''', (title, description, due_date, priority, created_at)
        )
        conn.commit()

def get_tasks_from_db():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
    return tasks

def update_task_in_db(task_id: int, title: str, description: str, due_date: str, priority: int) -> None:
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE tasks
            SET title = ?, description = ?, due_date = ?, priority = ?
            WHERE id = ?
            ''', (title, description, due_date, priority, task_id)
        )
        conn.commit()

def delete_task_from_db(task_id):
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
