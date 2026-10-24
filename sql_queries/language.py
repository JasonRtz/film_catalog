from flask import request
from myutil.util import get_connection_cursor, get_timestamp_now

def get_languages():
    connection, cursor = get_connection_cursor()

    cursor.execute("SELECT * FROM language;")
    languages = cursor.fetchall()

    connection.close()

    languages_list = languages
    print(f"get_languages(): {languages_list[0] if languages_list else 'No languages'}")
    return languages_list

def del_language():
    connection, cursor = get_connection_cursor()

    language_id = request.form['id']
    
    cursor.execute("SELECT COUNT(*) FROM film WHERE language_id = ?", (language_id,))
    film_count = cursor.fetchone()[0]
    
    if film_count > 0:
        connection.close()
        raise ValueError(f"Cannot delete language: it is used by {film_count} film(s).")
    
    cursor.execute("DELETE FROM language WHERE language_id = ?", (language_id,))
    connection.commit()
    connection.close()


def insert_language():
    connection, cursor = get_connection_cursor()

    name = request.form['name'].strip()
    last_update = get_timestamp_now()

    cursor.execute("INSERT INTO language (name, last_update) VALUES (?, ?)", (name, last_update))
    connection.commit()

    cursor.execute("SELECT * FROM language")
    languages = cursor.fetchall()

    connection.close()
    return languages


def get_language_by_id():
    connection, cursor = get_connection_cursor()

    cursor.execute("SELECT * FROM language WHERE language_id = ?", (request.form['id'],))
    language_info = cursor.fetchall()

    connection.close()
    return language_info


def edit_language():
    connection, cursor = get_connection_cursor()

    language_id = request.form['id']
    name = request.form['name'].strip()
    last_update = get_timestamp_now()

    cursor.execute("UPDATE language SET name = ?, last_update = ? WHERE language_id = ?", (name, last_update, language_id))
    connection.commit()

    cursor.execute("SELECT * FROM language")
    languages = cursor.fetchall()

    connection.close()
    return languages