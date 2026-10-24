from flask import request
from myutil.util import get_connection_cursor, get_timestamp_now

def get_categories():
    connection, cursor = get_connection_cursor()

    cursor.execute("SELECT * FROM category;")
    categories = cursor.fetchall()

    connection.close()

    categories_list = categories 
    return categories_list

def del_category():
    connection, cursor = get_connection_cursor()

    category_id = request.form['id']
    
    cursor.execute("DELETE FROM film_category WHERE category_id = ?", (category_id,))
    
    cursor.execute("DELETE FROM category WHERE category_id = ?", (category_id,))
    
    connection.commit()
    connection.close()


def insert_category():
    connection, cursor = get_connection_cursor()

    name = request.form['name'].strip()
    last_update = get_timestamp_now()

    cursor.execute("INSERT INTO category (name, last_update) VALUES (?, ?)", (name, last_update))
    connection.commit()

    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()

    connection.close()
    return categories


def get_category_by_id():
    connection, cursor = get_connection_cursor()

    cursor.execute("SELECT * FROM category WHERE category_id = ?", (request.form['id'],))
    category_info = cursor.fetchall()

    connection.close()
    return category_info


def edit_category():
    connection, cursor = get_connection_cursor()

    category_id = request.form['id']
    name = request.form['name'].strip()
    last_update = get_timestamp_now()

    cursor.execute("UPDATE category SET name = ?, last_update = ? WHERE category_id = ?", (name, last_update, category_id))
    connection.commit()

    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()

    connection.close()
    return categories