from db import get_connection

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "select id, username, email, password_hash, role, created_at from users where username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "select id, username, email, password_hash, role, created_at from users where email = ?",
        (email,)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "select id, username, email, role, created_at from users where id = ?",
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def create_user(username, email, password_hash, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        insert into users (username, email, password_hash, role)
        values (?, ?, ?, ?)
        """,
        (username, email, password_hash, role)
    )
    conn.commit()
    conn.close()