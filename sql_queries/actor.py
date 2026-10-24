from flask import request
from myutil.util import get_connection_cursor, get_timestamp_now

'''
Return the information of all the actors. You are going to execute one SQL query.
'''
def get_actors():
    connection, cursor = get_connection_cursor()

    # Select and display data from the 'actor' table
    cursor.execute("SELECT * FROM actor;")
    actors = cursor.fetchall()

    connection.close()

    actors_list = actors #[(38, "TOM", "MCKELLEN", "2024-12-19 16:39:39")]
    return actors_list

'''
Delete an actor and then return nothing. You are going to execute two SQL queries.
'''
def del_actor():
    connection, cursor = get_connection_cursor()

    actor_id = request.form['id']
    
    cursor.execute("DELETE FROM film_actor WHERE actor_id = ?", (actor_id,))
    
    cursor.execute("DELETE FROM actor WHERE actor_id = ?", (actor_id,))
    
    connection.commit()
    connection.close()


'''
Insert an actor and then return a list of tuples with all the actors. You are going to execute two SQL queries.
'''
def insert_actor():
    connection, cursor = get_connection_cursor()

    first_name = request.form['first_name'].strip()
    last_name = request.form['last_name'].strip()
    last_update = get_timestamp_now()

    cursor.execute("INSERT INTO actor (first_name, last_name, last_update) VALUES (?, ?, ?)", (first_name, last_name, last_update))
    connection.commit()

    cursor.execute("SELECT * FROM actor")
    actors = cursor.fetchall()

    connection.close()
    return actors

'''
Return the information of a specific actor.
'''
def get_actor_by_id():
    connection, cursor = get_connection_cursor()

    cursor.execute("SELECT * FROM actor WHERE actor_id = ?", (request.form['id'],))
    actor_info = cursor.fetchall()

    connection.close()
    return actor_info

'''
Update the actor and then return a list of tuples with all the actors. You are going to execute two SQL queries.
'''
def edit_actor():
    connection, cursor = get_connection_cursor()

    actor_id = request.form['id']
    first_name = request.form['first_name'].strip()
    last_name = request.form['last_name'].strip()
    last_update = get_timestamp_now()

    cursor.execute("UPDATE actor SET first_name = ?, last_name = ?, last_update = ? WHERE actor_id = ?", (first_name, last_name, last_update, actor_id))
    connection.commit()

    cursor.execute("SELECT * FROM actor")
    actors = cursor.fetchall()

    connection.close()
    return actors