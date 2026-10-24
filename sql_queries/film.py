from flask import request
from myutil.util import get_connection_cursor, get_timestamp_now

VALID_RATINGS = ['G', 'PG', 'PG-13', 'R', 'NC-17']
SPECIAL_FEATURES = ['Trailers', 'Commentaries', 'Deleted Scenes', 'Behind the Scenes']

# Reads and validates the film form. Returns (values, errors): values is a dict ready for the
# INSERT/UPDATE (empty optional fields become None or the column default), errors a list of messages.
def parse_film_form():
    form = request.form
    values = {}
    errors = []

    def text(name):
        return form.get(name, '').strip()

    def number(name, label, cast, default, minimum, maximum):
        raw = text(name)
        if raw == '':
            return default
        try:
            value = cast(raw)
        except ValueError:
            errors.append(f"Sorry the {label} must be a number. Try again.")
            return default
        if not minimum <= value <= maximum:
            errors.append(f"Sorry the {label} must be between {minimum} and {maximum}. Try again.")
        return value

    values['title'] = text('title')
    if values['title'] == '':
        errors.append("Sorry the film title cannot be empty. Try again.")
    values['description'] = form.get('description', '')

    language_id = number('language_id', 'language id', int, None, 1, 2**31 - 1)
    if language_id is None and not any('language id' in e for e in errors):
        errors.append("Sorry you must select a language. Try again.")
    values['language_id'] = language_id

    values['original_language_id'] = number('original_language_id', 'original language id', int, None, 1, 2**31 - 1)

    release_year = text('release_year')
    if release_year != '' and not (len(release_year) == 4 and release_year.isdigit()):
        errors.append("Sorry the release year must be a 4 digit year. Try again.")
    values['release_year'] = release_year or None

    values['rental_duration'] = number('rental_duration', 'rental duration', int, 3, 1, 32767)
    values['rental_rate'] = number('rental_rate', 'rental rate', float, 4.99, 0, 99.99)
    values['length'] = number('length', 'length', int, None, 1, 32767)
    values['replacement_cost'] = number('replacement_cost', 'replacement cost', float, 19.99, 0, 999.99)

    values['rating'] = text('rating') or 'G'
    if values['rating'] not in VALID_RATINGS:
        errors.append(f"Sorry the rating must be one of: {', '.join(VALID_RATINGS)}. Try again.")

    selected = [f for f in form.getlist('special_features') if f in SPECIAL_FEATURES]
    values['special_features'] = ','.join(selected) or None

    return values, errors

def get_films():
    connection, cursor = get_connection_cursor()

    cursor.execute("SELECT * FROM film;")
    films = cursor.fetchall()

    connection.close()

    films_list = films
    print(f"get_films(): {films_list[0] if films_list else 'No films'}")
    return films_list

def del_film():
    connection, cursor = get_connection_cursor()

    film_id = request.form['id']
    
    cursor.execute("DELETE FROM film_actor WHERE film_id = ?", (film_id,))
    cursor.execute("DELETE FROM film_category WHERE film_id = ?", (film_id,))
    
    cursor.execute("DELETE FROM film WHERE film_id = ?", (film_id,))
    
    connection.commit()
    connection.close()


def insert_film():
    v, errors = parse_film_form()
    if errors:
        raise ValueError(" ".join(errors))

    connection, cursor = get_connection_cursor()
    try:
        cursor.execute("""INSERT INTO film (title, description, release_year, language_id, original_language_id,
                         rental_duration, rental_rate, length, replacement_cost, rating, special_features, last_update) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                       (v['title'], v['description'], v['release_year'], v['language_id'], v['original_language_id'],
                        v['rental_duration'], v['rental_rate'], v['length'], v['replacement_cost'], v['rating'],
                        v['special_features'], get_timestamp_now()))
        connection.commit()

        cursor.execute("SELECT * FROM film")
        return cursor.fetchall()
    finally:
        connection.close()


def get_film_by_id():
    connection, cursor = get_connection_cursor()

    cursor.execute("SELECT * FROM film WHERE film_id = ?", (request.form['id'],))
    film_info = cursor.fetchall()

    connection.close()
    return film_info


def edit_film():
    v, errors = parse_film_form()
    if errors:
        raise ValueError(" ".join(errors))

    connection, cursor = get_connection_cursor()
    try:
        cursor.execute("""UPDATE film SET title = ?, description = ?, release_year = ?, language_id = ?, original_language_id = ?,
                         rental_duration = ?, rental_rate = ?, length = ?, replacement_cost = ?, 
                         rating = ?, special_features = ?, last_update = ? WHERE film_id = ?""", 
                       (v['title'], v['description'], v['release_year'], v['language_id'], v['original_language_id'],
                        v['rental_duration'], v['rental_rate'], v['length'], v['replacement_cost'], v['rating'],
                        v['special_features'], get_timestamp_now(), request.form['id']))
        connection.commit()

        cursor.execute("SELECT * FROM film")
        return cursor.fetchall()
    finally:
        connection.close()
