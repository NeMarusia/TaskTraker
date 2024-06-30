import sqlite3
from typing import Optional
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
                priority INTEGER
            )
            '''
        )
        conn.commit()
        print("'tasks' table created successfully.")
        conn.close()


def add_task_to_db(title, description, due_date, priority):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (title, description, due_date, priority) VALUES (?, ?, ?, ?)
    ''', (title, description, due_date, priority))
    conn.commit()
    conn.close()

def get_tasks_from_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_in_db(task_id: int, title: str, description: str, due_date: str, priority: int) -> None:
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tasks
        SET title = ?, description = ?, due_date = ?, priority = ?
        WHERE id = ?
    ''', (title, description, due_date, priority, task_id))
    conn.commit()
    conn.close()

def delete_task_from_db(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
